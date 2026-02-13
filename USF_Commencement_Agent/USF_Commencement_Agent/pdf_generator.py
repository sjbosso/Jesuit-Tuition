"""
PDF generation service for commencement exception request records.
Produces a branded PDF containing all request data, decisions, and fulfillment info.
"""

import os
from datetime import datetime, timezone
from fpdf import FPDF

from mock_services import ExceptionRequest


# USF brand colors
USF_GREEN_R, USF_GREEN_G, USF_GREEN_B = 0, 84, 60
USF_GOLD_R, USF_GOLD_G, USF_GOLD_B = 253, 187, 48


class USFCommencementPDF(FPDF):
    """Custom PDF class with USF branding."""

    def header(self):
        # USF green bar at top
        self.set_fill_color(USF_GREEN_R, USF_GREEN_G, USF_GREEN_B)
        self.rect(0, 0, 210, 12, "F")

        # Gold accent line
        self.set_fill_color(USF_GOLD_R, USF_GOLD_G, USF_GOLD_B)
        self.rect(0, 12, 210, 1.5, "F")

        self.set_y(18)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(USF_GREEN_R, USF_GREEN_G, USF_GREEN_B)
        self.cell(0, 6, "University of San Francisco", ln=True, align="C")

        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "Office of the Registrar", ln=True, align="C")

        self.ln(3)

    def footer(self):
        self.set_y(-20)

        # Gold accent line
        self.set_fill_color(USF_GOLD_R, USF_GOLD_G, USF_GOLD_B)
        self.rect(10, self.get_y(), 190, 0.5, "F")

        self.ln(3)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(130, 130, 130)
        self.cell(0, 4, "CONFIDENTIAL - This document contains protected student education records (FERPA)", ln=True, align="C")
        self.cell(0, 4, f"Page {self.page_no()}/{{nb}}    |    Generated {datetime.now(timezone.utc).strftime('%B %d, %Y at %I:%M %p UTC')}", align="C")

    def section_title(self, title: str):
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(USF_GREEN_R, USF_GREEN_G, USF_GREEN_B)
        self.cell(0, 7, title, ln=True)

        # Underline
        self.set_draw_color(USF_GOLD_R, USF_GOLD_G, USF_GOLD_B)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def label_value(self, label: str, value: str):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(60, 60, 60)
        self.cell(55, 6, label + ":", align="R")
        self.cell(3, 6, "")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)
        self.cell(0, 6, value or "N/A", ln=True)

    def label_multiline(self, label: str, value: str):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(60, 60, 60)
        self.cell(55, 6, label + ":", align="R")
        self.cell(3, 6, "")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)

        # Multi-line text in a constrained width
        x = self.get_x()
        y = self.get_y()
        self.multi_cell(130, 5, value or "N/A")
        self.ln(1)

    def status_badge(self, status: str):
        color_map = {
            "APPROVED": (34, 139, 34),
            "DENIED": (200, 50, 50),
            "SUBMITTED": (50, 100, 180),
            "UNDER_REVIEW": (180, 140, 20),
            "DRAFT": (150, 150, 150),
        }
        r, g, b = color_map.get(status, (100, 100, 100))

        self.set_font("Helvetica", "B", 12)
        self.set_text_color(r, g, b)
        self.cell(55, 8, "Decision:", align="R")
        self.cell(3, 8, "")
        self.cell(40, 8, f"  {status}  ", border=1, ln=True)
        self.set_text_color(0, 0, 0)


def generate_pdf(request: ExceptionRequest, output_dir: str = ".") -> str:
    """
    Generate a comprehensive PDF record of a commencement exception request.

    Args:
        request: The ExceptionRequest object with all data.
        output_dir: Directory to write the PDF to.

    Returns:
        The file path of the generated PDF.
    """
    pdf = USFCommencementPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()

    # ── Document Title ──
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(USF_GREEN_R, USF_GREEN_G, USF_GREEN_B)
    pdf.cell(0, 10, "Commencement Exception Request", ln=True, align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Request ID: {request.id}", ln=True, align="C")
    pdf.ln(4)

    # ── Section 1: Student Information ──
    pdf.section_title("Student Information")
    pdf.label_value("Student Name", request.student_name)
    pdf.label_value("USF Username", request.usf_username)
    pdf.label_value("USF Email", request.usf_email)
    pdf.label_value("Student ID", request.student_id)
    pdf.label_value("School/College", request.school_college)
    pdf.label_value("Degree Program", request.program)
    pdf.label_value("Phone Number", request.phone_number)

    # ── Section 2: Exception Request Details ──
    pdf.section_title("Exception Request Details")
    pdf.label_value("Original Ceremony", request.original_ceremony_semester)
    pdf.label_value("Requested Ceremony", request.requested_ceremony_semester)
    pdf.label_multiline("Extenuating Circumstances", request.extenuating_circumstances)
    pdf.label_value("Submitted", request.submitted_at or "N/A")

    # ── Section 3: Registrar Decision ──
    pdf.section_title("Registrar Decision")
    pdf.status_badge(request.status)
    pdf.label_value("Reviewer", request.reviewer_name or "Pending")
    pdf.label_multiline("Rationale", request.decision_rationale or "Pending review")
    pdf.label_value("Decision Date", request.decided_at or "Pending")

    # ── Section 4: Fulfillment (if approved) ──
    if request.status == "APPROVED":
        pdf.section_title("Cap and Gown Fulfillment")
        if request.gown_size:
            pdf.label_value("Gown Size", request.gown_size)
            pdf.label_value("Cap Size", request.cap_size)
            full_address = (
                f"{request.mailing_street}, "
                f"{request.mailing_city}, {request.mailing_state} {request.mailing_zip}"
            )
            pdf.label_value("Mailing Address", full_address)
            pdf.label_value("Fulfillment Status", request.fulfillment_status or "N/A")
        else:
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(130, 130, 130)
            pdf.cell(0, 6, "    Awaiting student fulfillment information.", ln=True)

    # ── Section 5: Audit Trail ──
    pdf.section_title("Audit Trail")
    if request.audit_log:
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(60, 60, 60)

        # Table header
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(55, 5, "  Timestamp", fill=True)
        pdf.cell(80, 5, "  Action", fill=True)
        pdf.cell(45, 5, "  Actor", fill=True, ln=True)

        pdf.set_font("Helvetica", "", 8)
        for entry in request.audit_log:
            pdf.cell(55, 5, "  " + entry.get("timestamp", "")[:19])
            pdf.cell(80, 5, "  " + entry.get("action", ""))
            pdf.cell(45, 5, "  " + entry.get("actor", ""), ln=True)
    else:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(130, 130, 130)
        pdf.cell(0, 6, "    No audit events recorded.", ln=True)

    # ── Section 6: Conversation Transcript ──
    if request.conversation_history:
        pdf.add_page()
        pdf.section_title("Conversation Transcript")
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(40, 40, 40)

        for msg in request.conversation_history:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            if not content or not isinstance(content, str):
                continue

            pdf.set_font("Helvetica", "B", 8)
            color = (0, 84, 60) if role == "ASSISTANT" else (50, 50, 150)
            pdf.set_text_color(*color)
            pdf.cell(0, 5, f"[{role}]", ln=True)

            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(0, 4, content[:2000])  # Truncate very long messages
            pdf.ln(2)

    # ── Write file ──
    os.makedirs(output_dir, exist_ok=True)
    safe_id = request.id[:8]
    filename = f"commencement_exception_{request.student_id}_{safe_id}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)

    return filepath
