"""
Registrar Review Dashboard — Streamlit page for reviewing,
approving, or denying commencement exception requests.
"""

import os
import streamlit as st
from datetime import datetime, timezone

from mock_services import db
from pdf_generator import generate_pdf

# ─────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="USF Registrar — Exception Review",
    page_icon="\U0001F4CB",
    layout="wide",
)

st.markdown("""
<div style="text-align:center; padding: 0.5rem 0;">
    <h2 style="color:#00543C; margin-bottom:0;">Registrar Review Dashboard</h2>
    <p style="color:#888; font-size:0.9rem;">Commencement Exception Requests</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# Request list
# ─────────────────────────────────────────────────────────────────

all_requests = db.get_all_requests()

if not all_requests:
    st.info(
        "No requests in the system yet. "
        "Go to the **Student Request** page to submit one first."
    )
    st.stop()

# Split into pending and decided
pending = [r for r in all_requests if r.status in ("SUBMITTED", "UNDER_REVIEW")]
decided = [r for r in all_requests if r.status in ("APPROVED", "DENIED")]

# ── Tabs ──
tab_pending, tab_decided = st.tabs([
    f"\U0001F4E8 Pending ({len(pending)})",
    f"\u2705 Decided ({len(decided)})",
])


def render_request_card(req, show_actions=False):
    """Render a single request as an expander card."""
    status_badges = {
        "SUBMITTED": ":blue[SUBMITTED]",
        "UNDER_REVIEW": ":orange[UNDER REVIEW]",
        "APPROVED": ":green[APPROVED]",
        "DENIED": ":red[DENIED]",
    }
    badge = status_badges.get(req.status, req.status)

    with st.expander(
        f"**{req.student_name}** ({req.student_id}) — {req.program}, {req.school_college}  |  {badge}",
        expanded=show_actions,
    ):
        # ── Student info ──
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Student Information**")
            st.text(f"Name:            {req.student_name}")
            st.text(f"Student ID:      {req.student_id}")
            st.text(f"Email:           {req.usf_email}")
            st.text(f"Username:        {req.usf_username}")
            st.text(f"School/College:  {req.school_college}")
            st.text(f"Program:         {req.program}")
            st.text(f"Phone:           {req.phone_number}")

        with col2:
            st.markdown("**Request Details**")
            st.text(f"Original Ceremony:    {req.original_ceremony_semester}")
            st.text(f"Requested Ceremony:   {req.requested_ceremony_semester}")
            st.text(f"Submitted:            {(req.submitted_at or 'N/A')[:19]}")
            st.markdown("**Extenuating Circumstances:**")
            st.info(req.extenuating_circumstances or "N/A")

        # ── Decision display (if decided) ──
        if req.status in ("APPROVED", "DENIED"):
            st.divider()
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                if req.status == "APPROVED":
                    st.success(f"**APPROVED** by {req.reviewer_name}")
                else:
                    st.error(f"**DENIED** by {req.reviewer_name}")
                st.caption(f"Decided: {(req.decided_at or 'N/A')[:19]}")
            with dcol2:
                st.markdown("**Rationale:**")
                st.write(req.decision_rationale or "No rationale provided.")

        # ── Fulfillment display ──
        if req.status == "APPROVED" and req.gown_size:
            st.divider()
            st.markdown("**Fulfillment Order**")
            fcol1, fcol2, fcol3 = st.columns(3)
            with fcol1:
                st.text(f"Gown: {req.gown_size}  |  Cap: {req.cap_size}")
            with fcol2:
                addr = f"{req.mailing_street}, {req.mailing_city}, {req.mailing_state} {req.mailing_zip}"
                st.text(f"Ship to: {addr}")
            with fcol3:
                st.text(f"Status: {req.fulfillment_status or 'N/A'}")

        # ── Action buttons (for pending requests) ──
        if show_actions and req.status in ("SUBMITTED", "UNDER_REVIEW"):
            st.divider()
            st.markdown("### Make a Decision")

            reviewer_name = st.text_input(
                "Your name", value="Registrar Staff", key=f"reviewer_{req.id}"
            )
            rationale = st.text_area(
                "Rationale (required)", key=f"rationale_{req.id}",
                placeholder="Explain the reason for your decision..."
            )

            bcol1, bcol2, bcol3 = st.columns([1, 1, 2])
            with bcol1:
                if st.button("\u2705 Approve", key=f"approve_{req.id}", type="primary", use_container_width=True):
                    if not rationale.strip():
                        st.warning("Please provide a rationale.")
                    else:
                        db.update_status(req.id, "APPROVED", reviewer_name=reviewer_name, rationale=rationale)
                        # Auto-generate PDF
                        output_dir = os.path.join(os.path.dirname(__file__) or ".", "..", "output")
                        pdf_path = generate_pdf(req, output_dir=output_dir)
                        req.pdf_path = pdf_path
                        req.audit_log.append({
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "action": "PDF record generated",
                            "actor": reviewer_name,
                        })
                        st.success("Request APPROVED. PDF generated.")
                        st.rerun()

            with bcol2:
                if st.button("\u274C Deny", key=f"deny_{req.id}", use_container_width=True):
                    if not rationale.strip():
                        st.warning("Please provide a rationale.")
                    else:
                        db.update_status(req.id, "DENIED", reviewer_name=reviewer_name, rationale=rationale)
                        output_dir = os.path.join(os.path.dirname(__file__) or ".", "..", "output")
                        pdf_path = generate_pdf(req, output_dir=output_dir)
                        req.pdf_path = pdf_path
                        req.audit_log.append({
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "action": "PDF record generated",
                            "actor": reviewer_name,
                        })
                        st.error("Request DENIED. PDF generated.")
                        st.rerun()

        # ── PDF download ──
        if req.pdf_path and os.path.exists(req.pdf_path):
            st.divider()
            with open(req.pdf_path, "rb") as f:
                st.download_button(
                    "\U0001F4C4 Download PDF Record",
                    data=f,
                    file_name=os.path.basename(req.pdf_path),
                    mime="application/pdf",
                    key=f"pdf_{req.id}",
                )

        # ── Audit trail ──
        if req.audit_log:
            with st.popover("View Audit Trail"):
                for entry in req.audit_log:
                    st.caption(
                        f"`{entry['timestamp'][:19]}` — "
                        f"{entry['action']} — *{entry['actor']}*"
                    )


# ── Render tabs ──
with tab_pending:
    if pending:
        for req in pending:
            render_request_card(req, show_actions=True)
    else:
        st.success("No pending requests. All caught up!")

with tab_decided:
    if decided:
        for req in decided:
            render_request_card(req, show_actions=False)
    else:
        st.info("No decisions have been made yet.")

# ── Sidebar metrics ──
with st.sidebar:
    st.markdown("### Dashboard")
    m1, m2 = st.columns(2)
    m1.metric("Pending", len(pending))
    m2.metric("Decided", len(decided))

    approved = len([r for r in decided if r.status == "APPROVED"])
    denied = len([r for r in decided if r.status == "DENIED"])
    if decided:
        m3, m4 = st.columns(2)
        m3.metric("Approved", approved)
        m4.metric("Denied", denied)

    st.divider()
    if st.button("\U0001F504 Refresh", use_container_width=True):
        st.rerun()
