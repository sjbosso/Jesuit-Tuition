#!/usr/bin/env python3
"""
Smoke test — validates imports, mock services, tool execution,
PDF generation, and Gemini SDK setup without needing any API key.
"""

import json
import os
import sys

# ── Core imports (no SDK needed) ──
from mock_services import get_sso_username, lookup_banner_record, db, ExceptionRequest
from agent_config import SYSTEM_PROMPT, TOOLS
from pdf_generator import generate_pdf

# ── Test 1: Shibboleth mock ──
print("[Test 1]  Shibboleth SSO mock...", end=" ")
username = get_sso_username()
assert username == "sjbosso", f"Expected 'sjbosso', got '{username}'"
print(f"OK — username={username}")

# ── Test 2: Banner mock ──
print("[Test 2]  Banner lookup...", end=" ")
record = lookup_banner_record("sjbosso")
assert record is not None
assert record["student_name"] == "Steven Bosso"
assert record["usf_email"] == "sjbosso@usfca.edu"
assert record["student_id"] == "12345678"
assert record["school_college"] == "CAS"
assert record["program"] == "Computer Science"
print(f"OK — {record['student_name']}, {record['program']}")

# ── Test 3: Banner miss ──
print("[Test 3]  Banner miss...", end=" ")
assert lookup_banner_record("nonexistent") is None
print("OK")

# ── Test 4: System prompt ──
print("[Test 4]  System prompt...", end=" ")
assert len(SYSTEM_PROMPT) > 500
assert "get_student_info" in SYSTEM_PROMPT
print(f"OK — {len(SYSTEM_PROMPT)} chars")

# ── Test 5: Tool definitions ──
print("[Test 5]  Tool definitions...", end=" ")
tool_names = {t["name"] for t in TOOLS}
expected = {"get_student_info", "submit_exception_request", "check_request_status",
            "submit_fulfillment_info", "generate_pdf_record"}
assert tool_names == expected
print(f"OK — {len(TOOLS)} tools")

# ── Test 6: Gemini FunctionDeclaration build ──
print("[Test 6]  Gemini declarations...", end=" ")
try:
    from agent_config import build_gemini_declarations
    declarations = build_gemini_declarations()
    assert len(declarations) == 5
    decl_names = {d.name for d in declarations}
    assert decl_names == expected
    print(f"OK — {len(declarations)} FunctionDeclarations built")
except ImportError as e:
    print(f"SKIP — google-genai not installed ({e})")

# ── Test 7: Tool execution — get_student_info ──
print("[Test 7]  Tool exec: get_student_info...", end=" ")
from main import execute_tool
result = execute_tool("get_student_info", {"usf_username": "sjbosso"})
assert result["success"] is True
assert result["student_info"]["student_name"] == "Steven Bosso"
print("OK")

# ── Test 8: Tool execution — submit_exception_request ──
print("[Test 8]  Tool exec: submit_exception_request...", end=" ")
result = execute_tool("submit_exception_request", {
    "usf_username": "sjbosso",
    "student_name": "Steven Bosso",
    "usf_email": "sjbosso@usfca.edu",
    "student_id": "12345678",
    "school_college": "CAS",
    "program": "Computer Science",
    "phone_number": "(415) 555-1234",
    "original_ceremony_semester": "Fall 2025",
    "requested_ceremony_semester": "Spring 2026",
    "extenuating_circumstances": "I need to complete one remaining course in January 2026.",
})
assert result["success"] is True
assert result["status"] == "SUBMITTED"
request_id = result["request_id"]
print(f"OK — id={request_id[:8]}...")

# ── Test 9: check_request_status ──
print("[Test 9]  Tool exec: check_request_status...", end=" ")
result = execute_tool("check_request_status", {"usf_username": "sjbosso"})
assert result["success"] is True
assert result["status"] == "SUBMITTED"
print("OK")

# ── Test 10: Registrar approval ──
print("[Test 10] Registrar approval...", end=" ")
db.update_status(request_id, "APPROVED",
                 reviewer_name="Dr. Jane Smith",
                 rationale="Student is in good standing with only one course remaining.")
assert db.get_request(request_id).status == "APPROVED"
print("OK")

# ── Test 11: Fulfillment ──
print("[Test 11] Tool exec: submit_fulfillment_info...", end=" ")
result = execute_tool("submit_fulfillment_info", {
    "usf_username": "sjbosso",
    "gown_size": "L",
    "cap_size": "M",
    "mailing_street": "2130 Fulton Street",
    "mailing_city": "San Francisco",
    "mailing_state": "CA",
    "mailing_zip": "94117",
})
assert result["success"] is True
print("OK")

# ── Test 12: PDF generation ──
print("[Test 12] PDF generation...", end=" ")
req = db.get_request(request_id)
req.conversation_history = [
    {"role": "ASSISTANT", "content": "Welcome, Steven! I've retrieved your information from our system."},
    {"role": "USER", "content": "Yes, that looks correct."},
    {"role": "ASSISTANT", "content": "What is the best phone number to reach you at?"},
    {"role": "USER", "content": "(415) 555-1234"},
]
output_dir = os.path.join(os.path.dirname(__file__) or ".", "output")
pdf_path = generate_pdf(req, output_dir=output_dir)
assert os.path.exists(pdf_path)
print(f"OK — {os.path.getsize(pdf_path):,} bytes")

# ── Done ──
print()
print("=" * 50)
print("  All 12 tests passed.")
print(f"  PDF: {pdf_path}")
print("=" * 50)
