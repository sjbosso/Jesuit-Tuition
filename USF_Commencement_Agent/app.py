"""
USF Commencement Exception Request — Streamlit App
====================================================

Run locally:  streamlit run app.py

This is the home/landing page. The student chat and Registrar
dashboard live in the pages/ directory.
"""

import streamlit as st
from branding import (
    inject_branding, render_header, render_gold_divider,
    render_footer, get_usf_symbol,
    USF_GREEN, USF_YELLOW, USF_GRAY, USF_GREEN_LIGHT,
)

st.set_page_config(
    page_title="USF Commencement Exception",
    page_icon="\U0001F393",
    layout="centered",
)

inject_branding()

# ── USF-branded header ──
render_header(
    "University of San Francisco",
    "Office of the Registrar"
)

# ── Title section ──
st.markdown(f"""
<div style="text-align:center; padding: 1.5rem 0 0.5rem 0;">
    <h2 style="color:{USF_GREEN}; margin-bottom:0.3rem;
               font-family:'Source Sans 3',Arial,sans-serif;
               font-weight:700; letter-spacing:0.01em;">
        Commencement Exception Request
    </h2>
    <p style="color:{USF_GRAY}; font-size:0.95rem; margin-top:0;">
        Change the World from Here
    </p>
</div>
""", unsafe_allow_html=True)

render_gold_divider()
st.write("")

# ── Two-column layout ──
col1, col2 = st.columns(2)

with col1:
    symbol_student = get_usf_symbol(size=28, color=USF_GREEN)
    st.markdown(f"""
    <div style="padding:0.2rem 0 0.5rem 0;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.5rem;">
            {symbol_student}
            <h3 style="color:{USF_GREEN}; margin:0; font-family:'Source Sans 3',Arial,sans-serif;">
                Students
            </h3>
        </div>
        <p style="color:#444; font-size:0.92rem; line-height:1.5;">
            Submit a request to participate in a commencement
            ceremony other than the one you were originally
            scheduled for. The AI assistant will guide you
            through the process step by step.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Start Exception Request", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Student_Request.py")

with col2:
    symbol_reg = get_usf_symbol(size=28, color=USF_YELLOW)
    st.markdown(f"""
    <div style="padding:0.2rem 0 0.5rem 0;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.5rem;">
            {symbol_reg}
            <h3 style="color:{USF_GREEN}; margin:0; font-family:'Source Sans 3',Arial,sans-serif;">
                Registrar Staff
            </h3>
        </div>
        <p style="color:#444; font-size:0.92rem; line-height:1.5;">
            Review pending commencement exception requests,
            approve or deny them, and manage cap-and-gown
            fulfillment orders.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Review Dashboard", use_container_width=True):
        st.switch_page("pages/2_Registrar_Review.py")

# ── Footer ──
render_footer()
