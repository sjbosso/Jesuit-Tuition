"""
Student-facing AI chat page for commencement exception requests.
Uses Google Gemini with function calling via Streamlit's chat UI.

NOTE: Streamlit reruns the entire script on every interaction, which
closes the genai.Client's HTTP connection. To handle this, we create
a fresh client + chat for each send, passing the stored conversation
history so Gemini retains full context.
"""

import json
import os
import time
import streamlit as st
from datetime import datetime, timezone

from google import genai
from google.genai import types
from google.genai.errors import ClientError

from agent_config import SYSTEM_PROMPT, build_gemini_declarations
from mock_services import get_sso_username, lookup_banner_record, db, ExceptionRequest
from pdf_generator import generate_pdf

# ─────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="USF Commencement Exception — Student Request",
    page_icon="\U0001F393",
    layout="centered",
)

# ─────────────────────────────────────────────────────────────────
# Tool execution (same logic as CLI version)
# ─────────────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict) -> dict:
    """Execute a tool called by the AI Agent."""

    if tool_name == "get_student_info":
        username = tool_input["usf_username"]
        record = lookup_banner_record(username)
        if record:
            return {"success": True, "student_info": record}
        return {"success": False, "error": f"No Banner record found for '{username}'."}

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
            "message": "The request has been submitted to the Registrar's Office.",
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
                result["message"] = "Approved. Student needs to provide cap-and-gown size and mailing address."
            if request.fulfillment_status:
                result["fulfillment_status"] = request.fulfillment_status
            return result
        return {"success": False, "error": f"No request found for '{username}'."}

    elif tool_name == "submit_fulfillment_info":
        username = tool_input["usf_username"]
        request = db.get_request_by_username(username)
        if not request:
            return {"success": False, "error": "No request found."}
        if request.status != "APPROVED":
            return {"success": False, "error": f"Request is '{request.status}', not APPROVED."}
        db.update_fulfillment(
            request.id,
            gown_size=tool_input["gown_size"],
            cap_size=tool_input["cap_size"],
            street=tool_input["mailing_street"],
            city=tool_input["mailing_city"],
            state=tool_input["mailing_state"],
            zip_code=tool_input["mailing_zip"],
        )
        return {"success": True, "message": "Fulfillment info saved. Cap and gown will be mailed.", "fulfillment_status": "PENDING"}

    elif tool_name == "generate_pdf_record":
        username = tool_input["usf_username"]
        request = db.get_request_by_username(username)
        if not request:
            return {"success": False, "error": "No request found."}
        output_dir = os.path.join(os.path.dirname(__file__) or ".", "..", "output")
        pdf_path = generate_pdf(request, output_dir=output_dir)
        request.pdf_path = pdf_path
        request.audit_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "PDF record generated",
            "actor": "system",
        })
        return {"success": True, "pdf_path": pdf_path, "message": "PDF generated."}

    return {"success": False, "error": f"Unknown tool: {tool_name}"}


# ─────────────────────────────────────────────────────────────────
# Gemini helpers
# ─────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    """Retrieve API key from Streamlit secrets or environment."""
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except (KeyError, FileNotFoundError):
        return os.environ.get("GOOGLE_API_KEY", "")


def _build_config():
    """Build a GenerateContentConfig with system prompt and tools."""
    declarations = build_gemini_declarations()
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=declarations,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True,
        ),
    )


def _send_with_retry(chat, message, max_retries=2):
    """Send a message to Gemini with automatic retry on rate-limit errors."""
    for attempt in range(max_retries + 1):
        try:
            return chat.send_message(message)
        except ClientError as e:
            if "429" in str(e) and attempt < max_retries:
                wait = 15 * (attempt + 1)  # 15s, then 30s
                st.toast(f"Rate limit hit — waiting {wait}s before retrying...", icon="\u23F3")
                time.sleep(wait)
            else:
                raise


def send_and_handle_tools(user_message) -> str:
    """
    Create a FRESH Gemini client and chat for this interaction,
    replay the stored conversation history, send the new message,
    handle any tool calls, and return the final text response.

    This avoids the 'client has been closed' error that occurs
    when Streamlit reruns the script and the old client is stale.
    """
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)
    config = _build_config()

    # Retrieve the Gemini-native history from session state
    gemini_history = st.session_state.get("gemini_history", [])

    # Create a new chat, replaying previous conversation
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=config,
        history=gemini_history,
    )

    try:
        # Send the new message
        response = _send_with_retry(chat, user_message)

        # Handle tool calls in a loop
        while response.function_calls:
            response_parts = []
            for fc in response.function_calls:
                args = dict(fc.args) if fc.args else {}
                result = execute_tool(fc.name, args)
                response_parts.append(
                    types.Part.from_function_response(
                        name=fc.name,
                        response=result,
                    )
                )
            response = _send_with_retry(chat, response_parts)

        # Persist the updated Gemini history for the next rerun
        st.session_state.gemini_history = list(chat._curated_history)

        return response.text or ""

    except ClientError as e:
        if "429" in str(e):
            return (
                "\u26A0\uFE0F **Rate limit reached.** The free tier of Gemini allows "
                "10 requests per minute and 250 per day. Please wait about a minute "
                "and try again. Your conversation is saved — nothing is lost."
            )
        raise


# ─────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────

# SSO mock
sso_username = get_sso_username()

# Header
st.markdown("""
<div style="text-align:center; padding: 0.5rem 0;">
    <h2 style="color:#00543C; margin-bottom:0;">Commencement Exception Request</h2>
    <p style="color:#888; font-size:0.9rem;">University of San Francisco &mdash; Office of the Registrar</p>
</div>
""", unsafe_allow_html=True)

# SSO badge
st.markdown(
    f'<div style="background:#F0F7F4; padding:0.5rem 1rem; border-radius:6px; '
    f'font-size:0.85rem; color:#555; margin-bottom:1rem;">'
    f'\U0001F512 Authenticated as <strong>{sso_username}</strong> via Shibboleth SSO</div>',
    unsafe_allow_html=True,
)

# API key check
api_key = get_api_key()
if not api_key or api_key == "your-google-api-key-here":
    st.warning(
        "**Google API key not configured.** "
        "Add your free key to `.streamlit/secrets.toml` or set the "
        "`GOOGLE_API_KEY` environment variable.\n\n"
        "Get a free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)"
    )
    st.stop()

# Initialize display messages and Gemini history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.gemini_history = []

    # Send the initial SSO trigger message to Gemini
    initial_msg = (
        f"[SYSTEM: Student has authenticated via Shibboleth SSO. "
        f"USF Username: {sso_username}. Please retrieve their "
        f"information and begin the commencement exception request process.]"
    )
    with st.spinner("Loading your information from Banner..."):
        greeting = send_and_handle_tools(initial_msg)

    st.session_state.messages.append({"role": "assistant", "content": greeting})

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Type your message..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            agent_reply = send_and_handle_tools(user_input)
        st.markdown(agent_reply)

    st.session_state.messages.append({"role": "assistant", "content": agent_reply})

    # Save conversation to the request if one exists
    request = db.get_request_by_username(sso_username)
    if request:
        request.conversation_history = [
            {"role": m["role"].upper(), "content": m["content"]}
            for m in st.session_state.messages
        ]

# ── Sidebar: request status & PDF download ──
request = db.get_request_by_username(sso_username)
if request:
    with st.sidebar:
        st.markdown("### Request Status")

        status_colors = {
            "SUBMITTED": "\U0001F4E8",
            "UNDER_REVIEW": "\U0001F50D",
            "APPROVED": "\u2705",
            "DENIED": "\u274C",
        }
        icon = status_colors.get(request.status, "\u2B55")
        st.markdown(f"**{icon} {request.status}**")
        st.caption(f"Request ID: {request.id[:8]}...")

        if request.status in ("APPROVED", "DENIED") and request.pdf_path and os.path.exists(request.pdf_path):
            with open(request.pdf_path, "rb") as f:
                st.download_button(
                    "\U0001F4C4 Download PDF Record",
                    data=f,
                    file_name=os.path.basename(request.pdf_path),
                    mime="application/pdf",
                    use_container_width=True,
                )
