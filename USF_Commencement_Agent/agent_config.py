"""
AI Agent configuration: system prompt, tool definitions, and conversation
orchestration settings for the USF Commencement Exception Request Agent.

Supports both Google Gemini (free) and Anthropic Claude backends.
"""

# ─────────────────────────────────────────────────────────────────────
# System Prompt
# ─────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are the University of San Francisco's Commencement Exception Request \
Assistant. You help USF students submit requests to participate in a \
commencement ceremony other than the one they were originally scheduled for.

You are warm, professional, and supportive. You understand that students \
requesting exceptions are often navigating stressful circumstances, so you \
are patient and encouraging throughout the conversation.

═══════════════════════════════════════════════════════════════════
WORKFLOW — Follow these steps in order
═══════════════════════════════════════════════════════════════════

STEP 1 — RETRIEVE AND PRESENT PRE-FILLED INFORMATION
As soon as the conversation begins, call the `get_student_info` tool with \
the student's USF username (provided in the first user message). Present \
the retrieved information to the student in a clear, readable format and \
ask them to confirm it is correct:

  - Student Name
  - USF Email
  - Student ID
  - School/College
  - Program

If the student says any information is wrong, note their correction and \
proceed. Do NOT ask the student for information that has already been \
retrieved from Banner.

STEP 2 — COLLECT ADDITIONAL INFORMATION
After the student confirms (or corrects) their pre-filled information, \
collect the following information in TWO conversational turns (not four \
separate questions). This reduces the number of exchanges and keeps the \
conversation efficient.

  Turn A — Ask for these three items together in a single message:
     1. Phone Number — "What is the best phone number to reach you at?"
     2. Semester of Original Commencement Ceremony — "Which semester \
        were you originally scheduled to participate in commencement?" \
        (e.g. "Fall 2025" or "Spring 2026")
     3. Requested Semester for Commencement Participation — "Which \
        commencement ceremony would you like to participate in instead?"

     Present these naturally, for example: "I just need a few details. \
     Could you provide: (1) your phone number, (2) the semester you \
     were originally scheduled for commencement, and (3) which ceremony \
     you'd like to participate in instead?"

     If the phone number doesn't look like a valid US number (10 digits), \
     gently ask the student to double-check.

  Turn B — Ask for extenuating circumstances on its own:
     Ask: "Could you please describe the extenuating circumstances that \
     are preventing you from participating in your originally scheduled \
     commencement ceremony? Please share as much detail as you are \
     comfortable with — this information helps the Registrar's Office \
     evaluate your request."
     Be supportive. If the student's response is very brief (under ~20 \
     words), gently encourage them to elaborate, but do not pressure them.

STEP 3 — SUMMARIZE AND CONFIRM
Once all information has been collected, present a complete summary of \
the request in a clear, organized format that includes both the pre-filled \
Banner data and the student-provided data. Ask the student to review \
everything and confirm they would like to submit.

STEP 4 — SUBMIT
When the student confirms, call the `submit_exception_request` tool with \
all of the collected information. After successful submission, let the \
student know:
  - Their request has been submitted to the Registrar's Office.
  - They will receive a notification at their USF email when a decision \
    has been made.
  - They can check the status of their request at any time by returning \
    to this system.

═══════════════════════════════════════════════════════════════════
POST-APPROVAL FULFILLMENT FLOW
═══════════════════════════════════════════════════════════════════

If the student returns after their request has been APPROVED, congratulate \
them and then collect ALL of the following fulfillment information in a \
SINGLE message (not separate questions, to keep the conversation efficient):

  1. Gown Size (XS, S, M, L, XL, XXL, XXXL)
  2. Cap Size (S, M, L, XL)
  3. Mailing Address (street, city, state, ZIP code)

For example: "To get your cap and gown shipped to you, I need three \
things: (1) your gown size (XS–XXXL), (2) your cap size (S–XL), and \
(3) the mailing address you'd like it shipped to."

Present a summary of the fulfillment details and ask for confirmation, \
then call the `submit_fulfillment_info` tool. Let the student know their \
cap and gown will be mailed to the provided address.

═══════════════════════════════════════════════════════════════════
RULES
═══════════════════════════════════════════════════════════════════

- NEVER fabricate or assume student data. Only use data returned by tools.
- NEVER skip the confirmation step before submission.
- Keep responses concise — typically 2-4 sentences per turn.
- If the student asks about the status of an existing request, call the \
  `check_request_status` tool.
- If the student asks questions outside the scope of commencement \
  exceptions (financial aid, grades, etc.), politely let them know this \
  assistant only handles commencement exception requests and suggest they \
  contact the appropriate USF office.
- Refer to the university as "USF" (not "the University of San Francisco") \
  in conversation after the initial greeting.
"""


# ─────────────────────────────────────────────────────────────────────
# Tool Definitions — Anthropic Claude format
# (kept for reference / future Anthropic use)
# ─────────────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "get_student_info",
        "description": (
            "Retrieves a student's academic information from the Banner "
            "Student Information System using their USF username. Returns "
            "the student's name, email, student ID, school/college, and "
            "degree program. Call this at the start of the conversation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "usf_username": {
                    "type": "string",
                    "description": "The student's USF username (from Shibboleth SSO)."
                }
            },
            "required": ["usf_username"]
        }
    },
    {
        "name": "submit_exception_request",
        "description": (
            "Submits a completed commencement exception request to the "
            "Registrar's Office for review. Call this only after the student "
            "has confirmed all information in the summary."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "usf_username": {
                    "type": "string",
                    "description": "The student's USF username."
                },
                "student_name": {
                    "type": "string",
                    "description": "The student's full name."
                },
                "usf_email": {
                    "type": "string",
                    "description": "The student's USF email address."
                },
                "student_id": {
                    "type": "string",
                    "description": "The student's USF ID number."
                },
                "school_college": {
                    "type": "string",
                    "description": "The student's school or college (e.g., CAS, SOM)."
                },
                "program": {
                    "type": "string",
                    "description": "The student's degree program."
                },
                "phone_number": {
                    "type": "string",
                    "description": "The student's contact phone number."
                },
                "original_ceremony_semester": {
                    "type": "string",
                    "description": "The semester of the student's original commencement ceremony (e.g., 'Fall 2025')."
                },
                "requested_ceremony_semester": {
                    "type": "string",
                    "description": "The semester the student is requesting to participate in commencement (e.g., 'Spring 2026')."
                },
                "extenuating_circumstances": {
                    "type": "string",
                    "description": "The student's description of their extenuating circumstances."
                }
            },
            "required": [
                "usf_username", "student_name", "usf_email", "student_id",
                "school_college", "program", "phone_number",
                "original_ceremony_semester", "requested_ceremony_semester",
                "extenuating_circumstances"
            ]
        }
    },
    {
        "name": "check_request_status",
        "description": (
            "Checks the current status of a student's commencement exception "
            "request. Returns the status (SUBMITTED, UNDER_REVIEW, APPROVED, "
            "DENIED) along with any decision details."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "usf_username": {
                    "type": "string",
                    "description": "The student's USF username."
                }
            },
            "required": ["usf_username"]
        }
    },
    {
        "name": "submit_fulfillment_info",
        "description": (
            "Submits the student's cap-and-gown size and mailing address "
            "for fulfillment after their request has been approved. Only "
            "call this after a request has been approved."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "usf_username": {
                    "type": "string",
                    "description": "The student's USF username."
                },
                "gown_size": {
                    "type": "string",
                    "description": "The student's gown size.",
                    "enum": ["XS", "S", "M", "L", "XL", "XXL", "XXXL"]
                },
                "cap_size": {
                    "type": "string",
                    "description": "The student's cap size.",
                    "enum": ["S", "M", "L", "XL"]
                },
                "mailing_street": {
                    "type": "string",
                    "description": "Street address for delivery."
                },
                "mailing_city": {
                    "type": "string",
                    "description": "City for delivery."
                },
                "mailing_state": {
                    "type": "string",
                    "description": "State for delivery (2-letter abbreviation)."
                },
                "mailing_zip": {
                    "type": "string",
                    "description": "ZIP code for delivery."
                }
            },
            "required": [
                "usf_username", "gown_size", "cap_size",
                "mailing_street", "mailing_city", "mailing_state", "mailing_zip"
            ]
        }
    },
    {
        "name": "generate_pdf_record",
        "description": (
            "Generates a PDF document containing the complete record of "
            "the commencement exception request, including all submitted "
            "information, the Registrar's decision, and fulfillment details. "
            "Call this after the process is complete (either denied, or "
            "approved with fulfillment submitted)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "usf_username": {
                    "type": "string",
                    "description": "The student's USF username."
                }
            },
            "required": ["usf_username"]
        }
    },
]


# ─────────────────────────────────────────────────────────────────────
# Gemini Helpers — convert TOOLS to google-genai FunctionDeclarations
# ─────────────────────────────────────────────────────────────────────

def build_gemini_declarations():
    """
    Convert the Anthropic-style TOOLS list into google.genai
    FunctionDeclaration objects. Imported lazily so agent_config.py
    can be loaded without the google-genai SDK installed (e.g. in tests).
    """
    from google.genai import types

    def _prop_to_schema(prop: dict) -> types.Schema:
        kwargs = {
            "type": prop["type"].upper(),
            "description": prop.get("description", ""),
        }
        if "enum" in prop:
            kwargs["enum"] = prop["enum"]
        return types.Schema(**kwargs)

    declarations = []
    for tool in TOOLS:
        schema = tool["input_schema"]
        properties = {
            k: _prop_to_schema(v)
            for k, v in schema["properties"].items()
        }
        declarations.append(
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool["description"],
                parameters=types.Schema(
                    type="OBJECT",
                    properties=properties,
                    required=schema.get("required", []),
                ),
            )
        )
    return declarations
