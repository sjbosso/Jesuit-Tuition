"""
USF Commencement Exception Request — Streamlit App
====================================================

Run locally:  streamlit run app.py

This is the home/landing page. The student chat and Registrar
dashboard live in the pages/ directory.
"""

import streamlit as st

st.set_page_config(
    page_title="USF Commencement Exception",
    page_icon="\U0001F393",
    layout="centered",
)

# ── USF-branded header ──
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem 0;">
    <h1 style="color:#00543C; margin-bottom:0;">University of San Francisco</h1>
    <p style="color:#888; font-size:1.1rem; margin-top:0.2rem;">Office of the Registrar</p>
    <hr style="border: 2px solid #FDBB30; width: 60%; margin: 1rem auto;">
    <h2 style="color:#333;">Commencement Exception Request</h2>
</div>
""", unsafe_allow_html=True)

st.write("")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### \U0001F9D1\u200D\U0001F393 Students
    Submit a request to participate in a commencement
    ceremony other than the one you were originally
    scheduled for.

    The AI assistant will guide you through the process
    step by step.
    """)
    if st.button("\U0001F4AC  Start Exception Request", use_container_width=True):
        st.switch_page("pages/1_Student_Request.py")

with col2:
    st.markdown("""
    ### \U0001F4CB Registrar Staff
    Review pending commencement exception requests,
    approve or deny them, and manage cap-and-gown
    fulfillment orders.
    """)
    if st.button("\U0001F50D  Open Review Dashboard", use_container_width=True):
        st.switch_page("pages/2_Registrar_Review.py")

st.divider()

st.caption(
    "This system is protected by USF Shibboleth Single Sign-On. "
    "All student data is handled in compliance with FERPA. "
    "For technical support, contact the Office of the Registrar."
)
