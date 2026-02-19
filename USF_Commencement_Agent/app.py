"""
USF Commencement Exception Request — Streamlit App
====================================================

Run locally:  streamlit run app.py

Navigation router for the multi-page app using st.navigation().
Icons use Streamlit's Material icon format: :material/icon_name:
(lowercase with underscores, e.g. :material/keyboard_double_arrow_right:)
"""

import streamlit as st

pg = st.navigation(
    [
        st.Page(
            "home.py",
            title="Home",
            icon=":material/home:",
            default=True,
        ),
        st.Page(
            "pages/1_Student_Request.py",
            title="Student Request",
            icon=":material/school:",
        ),
        st.Page(
            "pages/2_Registrar_Review.py",
            title="Registrar Review",
            icon=":material/fact_check:",
        ),
    ]
)

pg.run()
