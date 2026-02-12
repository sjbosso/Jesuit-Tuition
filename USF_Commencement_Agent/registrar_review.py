#!/usr/bin/env python3
"""
USF Commencement Exception — Registrar Review CLI
===================================================

Run:  python registrar_review.py

This provides a command-line interface for Registrar staff to review,
approve, or deny commencement exception requests. In production, this
would be a web-based dashboard protected by Shibboleth with role-based
access control.

After making a decision, the student can return to the agent (main.py)
to see their updated status and, if approved, provide fulfillment info.
"""

import os
import sys
from datetime import datetime, timezone

from mock_services import db, ExceptionRequest
from pdf_generator import generate_pdf


# ─────────────────────────────────────────────────────────────────────
# Display helpers
# ─────────────────────────────────────────────────────────────────────

def print_header():
    print()
    print("=" * 65)
    print("  USF Registrar's Office — Commencement Exception Review")
    print("=" * 65)
    print()


def print_request_summary(req: ExceptionRequest, index: int = None):
    prefix = f"  [{index}] " if index is not None else "  "
    status_icon = {
        "SUBMITTED": "NEW",
        "UNDER_REVIEW": "REVIEWING",
        "APPROVED": "APPROVED",
        "DENIED": "DENIED",
    }.get(req.status, req.status)

    print(f"{prefix}{req.student_name} ({req.student_id}) — "
          f"{req.program}, {req.school_college}")
    print(f"       Status: {status_icon}  |  Submitted: {(req.submitted_at or 'N/A')[:19]}")


def print_request_detail(req: ExceptionRequest):
    print()
    print("-" * 65)
    print(f"  REQUEST DETAIL — {req.id}")
    print("-" * 65)
    print()
    print(f"  Student Name:           {req.student_name}")
    print(f"  Student ID:             {req.student_id}")
    print(f"  USF Email:              {req.usf_email}")
    print(f"  USF Username:           {req.usf_username}")
    print(f"  School/College:         {req.school_college}")
    print(f"  Program:                {req.program}")
    print(f"  Phone:                  {req.phone_number}")
    print()
    print(f"  Original Ceremony:      {req.original_ceremony_semester}")
    print(f"  Requested Ceremony:     {req.requested_ceremony_semester}")
    print()
    print(f"  Extenuating Circumstances:")
    # Wrap long text
    circ = req.extenuating_circumstances or "N/A"
    words = circ.split()
    line = "    "
    for word in words:
        if len(line) + len(word) > 62:
            print(line)
            line = "    " + word + " "
        else:
            line += word + " "
    if line.strip():
        print(line)
    print()
    print(f"  Status:                 {req.status}")
    print(f"  Submitted:              {(req.submitted_at or 'N/A')[:19]}")

    if req.status in ("APPROVED", "DENIED"):
        print()
        print(f"  Decision:               {req.status}")
        print(f"  Reviewer:               {req.reviewer_name}")
        print(f"  Rationale:              {req.decision_rationale}")
        print(f"  Decided:                {(req.decided_at or 'N/A')[:19]}")

    if req.gown_size:
        print()
        print(f"  Gown Size:              {req.gown_size}")
        print(f"  Cap Size:               {req.cap_size}")
        print(f"  Mailing Address:        {req.mailing_street}")
        print(f"                          {req.mailing_city}, {req.mailing_state} {req.mailing_zip}")
        print(f"  Fulfillment Status:     {req.fulfillment_status}")

    print()
    print("-" * 65)


# ─────────────────────────────────────────────────────────────────────
# Review workflow
# ─────────────────────────────────────────────────────────────────────

def review_request(req: ExceptionRequest) -> bool:
    """
    Present a request for review and collect the Registrar's decision.
    Returns True if a decision was made, False if cancelled.
    """
    print_request_detail(req)

    if req.status not in ("SUBMITTED", "UNDER_REVIEW"):
        print("  This request has already been decided.")
        return False

    # Mark as under review
    if req.status == "SUBMITTED":
        db.update_status(req.id, "UNDER_REVIEW", reviewer_name="Registrar Staff")

    print("  Actions:")
    print("    [A] Approve")
    print("    [D] Deny")
    print("    [C] Cancel (return to list)")
    print()

    while True:
        choice = input("  Decision (A/D/C): ").strip().upper()
        if choice in ("A", "D", "C"):
            break
        print("  Please enter A, D, or C.")

    if choice == "C":
        # Revert to SUBMITTED if we just moved to UNDER_REVIEW
        print("  Cancelled. Returning to request list.")
        return False

    # Collect rationale
    print()
    rationale = input("  Rationale (required): ").strip()
    while not rationale:
        rationale = input("  Please provide a rationale: ").strip()

    # Collect reviewer name
    reviewer = input("  Your name (Registrar reviewer): ").strip()
    if not reviewer:
        reviewer = "Registrar Staff"

    # Apply decision
    new_status = "APPROVED" if choice == "A" else "DENIED"
    db.update_status(req.id, new_status, reviewer_name=reviewer, rationale=rationale)

    print()
    decision_word = "APPROVED" if choice == "A" else "DENIED"
    print(f"  Request {decision_word}.")
    print(f"  Student {req.student_name} will be notified at {req.usf_email}.")

    # Generate PDF after decision
    print()
    gen_pdf = input("  Generate PDF record now? (Y/n): ").strip().lower()
    if gen_pdf != "n":
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        pdf_path = generate_pdf(req, output_dir=output_dir)
        req.pdf_path = pdf_path
        req.audit_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "PDF record generated",
            "actor": reviewer,
        })
        print(f"  PDF saved to: {pdf_path}")

    return True


# ─────────────────────────────────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────────────────────────────────

def main():
    print_header()

    while True:
        # Show all requests
        all_requests = db.get_all_requests()

        if not all_requests:
            print("  No requests in the system.")
            print("  Run 'python main.py' to submit a student request first.")
            print()
            input("  Press Enter to refresh, or Ctrl+C to exit...")
            print_header()
            continue

        print("  PENDING REQUESTS:")
        print()
        pending = [r for r in all_requests if r.status in ("SUBMITTED", "UNDER_REVIEW")]
        decided = [r for r in all_requests if r.status in ("APPROVED", "DENIED")]

        if pending:
            for i, req in enumerate(pending):
                print_request_summary(req, i + 1)
            print()
        else:
            print("    (No pending requests)")
            print()

        if decided:
            print("  DECIDED REQUESTS:")
            print()
            for i, req in enumerate(decided):
                print_request_summary(req, len(pending) + i + 1)
            print()

        combined = pending + decided
        print("  Commands:")
        print("    [#] Enter a request number to review/view")
        print("    [R] Refresh list")
        print("    [Q] Quit")
        print()

        choice = input("  > ").strip().upper()

        if choice == "Q":
            print("\n  Goodbye!")
            break
        elif choice == "R":
            print_header()
            continue
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(combined):
                review_request(combined[idx])
                print()
                input("  Press Enter to return to the list...")
                print_header()
            else:
                print("  Invalid number.")
        else:
            print("  Invalid input.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Goodbye!")
