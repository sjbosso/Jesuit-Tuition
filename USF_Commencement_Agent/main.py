#!/usr/bin/env python3
"""
USF Commencement Exception Request — Student-Facing AI Agent
=============================================================

Run:  python main.py

This launches the conversational AI Agent that guides USF students
through the commencement exception request process. The agent:
  1. Authenticates via Shibboleth SSO (mocked)
  2. Retrieves student data from Ellucian Banner (mocked)
  3. Collects additional information conversationally
  4. Submits the request for Registrar review
  5. (Post-approval) Collects cap-and-gown fulfillment info
  6. Generates a PDF record of the complete transaction

Prerequisites:
  pip install google-genai fpdf2
  export GOOGLE_API_KEY=your-api-key-here

Get a free API key at: https://aistudio.google.com/apikey
"""

import json
import os
import sys
from datetime import datetime, timezone

from google import genai
from google.genai import types

from agent_config import SYSTEM_PROMPT, build_gemini_declarations
from mock_services import (
    get_sso_username,
    lookup_banner_record,
    db,
    ExceptionRequest,
)
from pdf_generator import generate_pdf


# ─────────────────────────────────────────────────────────────────────
# Tool Execution — maps tool calls from the LLM to application logic
# ─────────────────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Execute a tool called by the AI Agent and return the result as a
    dict that will be sent back to Gemini as a function response.
    """

    if tool_name == "get_student_info":
        username = tool_input["usf_username"]
        record = lookup_banner_record(username)
        if record:
            return {"success": True, "student_info": record}
        else:
            return {"success": False, "error": f"No Banner record found for username '{username}'."}

    elif tool_name == "submit_exception_request":
        request = ExceptionRequest(
            usf_username=tool_input["usf_username"],
            student_name=tool_input["student_name"],
            usf_email=tool_input["usf_email"],
            student_id=tool_input["student_id"],
            school_college=tool_input["school_college"],
            program=tool_input["program"],
            phone_number=tool_input["phone_number"],
            original_ceremony_semester=tool_input["original_ceremony_semester"],
            requested_ceremony_semester=tool_input["requested_ceremony_semester"],
            extenuating_circumstances=tool_input["extenuating_circumstances"],
            status="SUBMITTED",
            submitted_at=datetime.now(timezone.utc).isoformat(),
        )
        request.audit_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "Request submitted by student",
            "actor": request.usf_username,
        })
        request_id = db.save_request(request)
        return {
            "success": True,
            "request_id": request_id,
            "status": "SUBMITTED",
            "message": "The commencement exception request has been submitted to the Registrar's Office for review.",
        }

    elif tool_name == "check_request_status":
        username = tool_input["usf_username"]
        request = db.get_request_by_username(username)
        if request:
            result = {
                "success": True,
                "request_id": request.id,
                "status": request.status,
                "submitted_at": request.submitted_at,
            }
            if request.status in ("APPROVED", "DENIED"):
                result["decided_at"] = request.decided_at
                result["reviewer"] = request.reviewer_name
                result["rationale"] = request.decision_rationale
            if request.status == "APPROVED" and not request.gown_size:
                result["needs_fulfillment"] = True
                result["message"] = "This request has been approved. The student needs to provide cap-and-gown size and mailing address."
            if request.fulfillment_status:
                result["fulfillment_status"] = request.fulfillment_status
            return result
        else:
            return {"success": False, "error": f"No request found for username '{username}'."}

    elif tool_name == "submit_fulfillment_info":
        username = tool_input["usf_username"]
        request = db.get_request_by_username(username)
        if not request:
            return {"success": False, "error": "No request found."}
        if request.status != "APPROVED":
            return {"success": False, "error": f"Request status is '{request.status}', not APPROVED."}

        db.update_fulfillment(
            request.id,
            gown_size=tool_input["gown_size"],
            cap_size=tool_input["cap_size"],
            street=tool_input["mailing_street"],
            city=tool_input["mailing_city"],
            state=tool_input["mailing_state"],
            zip_code=tool_input["mailing_zip"],
        )
        return {
            "success": True,
            "message": "Fulfillment information saved. The cap and gown will be mailed to the provided address.",
            "fulfillment_status": "PENDING",
        }

    elif tool_name == "generate_pdf_record":
        username = tool_input["usf_username"]
        request = db.get_request_by_username(username)
        if not request:
            return {"success": False, "error": "No request found."}

        output_dir = os.path.join(os.path.dirname(__file__) or ".", "output")
        pdf_path = generate_pdf(request, output_dir=output_dir)
        request.pdf_path = pdf_path
        request.audit_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "PDF record generated",
            "actor": "system",
        })
        return {"success": True, "pdf_path": pdf_path, "message": "PDF record generated successfully."}

    else:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}


# ─────────────────────────────────────────────────────────────────────
# Conversation Loop  (Google Gemini — google-genai SDK)
# ─────────────────────────────────────────────────────────────────────

def run_agent():
    """Main conversation loop for the student-facing agent."""

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print()
        print("[ERROR] GOOGLE_API_KEY environment variable is not set.")
        print()
        print("  To get a FREE API key (no credit card required):")
        print("    1. Go to  https://aistudio.google.com/apikey")
        print("    2. Sign in with your Google account")
        print("    3. Click 'Create API key'")
        print("    4. Then run:")
        print("       export GOOGLE_API_KEY=your-key-here")
        print("       python main.py")
        print()
        sys.exit(1)

    # ── Create Gemini client and chat session ──
    client = genai.Client(api_key=api_key)

    # Build FunctionDeclarations from our tool config
    function_declarations = build_gemini_declarations()

    # Create a chat with system instructions, tools, and manual function calling
    chat = client.chats.create(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=function_declarations,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True,  # We handle tool execution ourselves
            ),
        ),
    )

    # ── Shibboleth SSO: get the authenticated username ──
    sso_username = get_sso_username()

    print("=" * 65)
    print("  USF Commencement Exception Request System")
    print("=" * 65)
    print(f"  Authenticated as: {sso_username} (via Shibboleth SSO)")
    print("-" * 65)
    print("  Type your messages below. Type 'quit' to exit.")
    print("  Type 'status' to check your request status.")
    print("=" * 65)
    print()

    def send_and_handle_tools(message) -> str:
        """
        Send a message to Gemini. If it responds with function calls,
        execute them and loop until we get a final text response.
        """
        response = chat.send_message(message)

        # Loop while Gemini wants to call tools
        while response.function_calls:
            response_parts = []
            for fc in response.function_calls:
                args = dict(fc.args) if fc.args else {}
                print(f"  [Tool: {fc.name}]")
                result = execute_tool(fc.name, args)

                # Build a function-response Part to send back
                response_parts.append(
                    types.Part.from_function_response(
                        name=fc.name,
                        response=result,
                    )
                )

            # Send tool results back to Gemini
            response = chat.send_message(response_parts)

        return response.text or ""

    # ── Initial agent greeting (triggered by SSO context) ──
    initial_message = (
        f"[SYSTEM: Student has authenticated via Shibboleth SSO. "
        f"USF Username: {sso_username}. Please retrieve their "
        f"information and begin the commencement exception request process.]"
    )
    agent_text = send_and_handle_tools(initial_message)
    print(f"\nAgent: {agent_text}\n")

    # ── Main conversation loop ──
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            print("\nThank you for using the USF Commencement Exception system. Goodbye!")
            break

        if user_input.lower() == "status":
            user_input = "What is the status of my request?"

        # Send to Gemini and handle any tool calls
        agent_text = send_and_handle_tools(user_input)
        print(f"\nAgent: {agent_text}\n")

        # Save conversation to the request if one exists
        request = db.get_request_by_username(sso_username)
        if request:
            request.conversation_history = []
            for msg in chat._curated_history:
                role_str = msg.role.upper() if hasattr(msg, "role") else "UNKNOWN"
                for part in (msg.parts or []):
                    if hasattr(part, "text") and part.text:
                        request.conversation_history.append({
                            "role": "ASSISTANT" if role_str == "MODEL" else "USER",
                            "content": part.text,
                        })


if __name__ == "__main__":
    run_agent()
