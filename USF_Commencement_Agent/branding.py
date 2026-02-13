"""
USF Branding Module
====================
Shared colors, typography, CSS, and logo based on the
University of San Francisco Graphic Standards Manual.
"""

import base64

# ── Official USF Colors (from Graphic Standards Manual p.34) ──
USF_GREEN = "#00543C"
USF_YELLOW = "#FDBB30"
USF_GRAY = "#919194"
USF_GREEN_ON_BLACK = "#00684A"
USF_GRAY_ON_BLACK = "#BBBDBF"

# Derived / UI colors
USF_GREEN_LIGHT = "#E8F0ED"    # Very light green for backgrounds
USF_YELLOW_LIGHT = "#FFF8E7"   # Very light gold for highlights
USF_GREEN_DARK = "#003D2B"     # Darker green for hover states


# ── USF Diamond Cross Symbol ──
# Simplified representation of the USF crossroads/cross symbol.
# Rendered as base64 data URI so Streamlit doesn't strip SVG tags.

def _build_symbol_svg(color):
    """Build raw SVG string for the USF diamond cross."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<g transform="translate(50,50) rotate(45)">'
        f'<rect x="-34" y="-34" width="68" height="68" rx="3" fill="none" stroke="{color}" stroke-width="3.5"/>'
        '</g>'
        f'<rect x="45" y="12" width="10" height="76" rx="2" fill="{color}"/>'
        f'<rect x="12" y="45" width="76" height="10" rx="2" fill="{color}"/>'
        f'<polygon points="50,5 40,22 60,22" fill="{color}"/>'
        f'<polygon points="50,95 40,78 60,78" fill="{color}"/>'
        f'<polygon points="5,50 22,40 22,60" fill="{color}"/>'
        f'<polygon points="95,50 78,40 78,60" fill="{color}"/>'
        '<g transform="translate(50,50) rotate(45)">'
        f'<rect x="-6" y="-6" width="12" height="12" fill="{color}"/>'
        '</g>'
        '</svg>'
    )


def get_usf_symbol_img(size=48, color=None):
    """Return an <img> tag with the USF symbol as a base64 data URI."""
    if color is None:
        color = USF_YELLOW
    svg_str = _build_symbol_svg(color)
    b64 = base64.b64encode(svg_str.encode("utf-8")).decode("utf-8")
    return (
        f'<img src="data:image/svg+xml;base64,{b64}" '
        f'width="{size}" height="{size}" '
        f'style="vertical-align:middle;" />'
    )


# ── Global CSS injected into every page ──
GLOBAL_CSS = f"""<style>
html, body, [class*="st-"] {{
    font-family: Arial, Helvetica, sans-serif;
}}
.usf-header {{
    background: linear-gradient({USF_GREEN}, {USF_GREEN_DARK});
    padding: 1rem 2rem;
    border-radius: 0 0 12px 12px;
    margin: -1rem -1rem 1.5rem -1rem;
    text-align: center;
}}
.usf-header-title {{
    color: white;
    font-family: Arial, Helvetica, sans-serif;
    font-weight: 700;
    font-size: 1.8rem;
    margin: 0;
    letter-spacing: 0.02em;
}}
.usf-header-sub {{
    color: {USF_GRAY_ON_BLACK};
    font-size: 0.9rem;
    margin-top: 0.2rem;
    letter-spacing: 0.05em;
}}
.usf-gold-divider {{
    height: 3px;
    background: {USF_YELLOW};
    border: none;
    margin: 1rem 0;
    border-radius: 2px;
}}
.usf-sso-badge {{
    background: {USF_GREEN_LIGHT};
    border-left: 4px solid {USF_GREEN};
    padding: 0.6rem 1rem;
    border-radius: 0 6px 6px 0;
    font-size: 0.85rem;
    color: #333;
    margin-bottom: 1rem;
}}
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {{
    background-color: {USF_GREEN} !important;
    border-color: {USF_GREEN} !important;
    color: white !important;
    font-weight: 600;
    border-radius: 6px;
}}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {{
    background-color: {USF_GREEN_DARK} !important;
    border-color: {USF_GREEN_DARK} !important;
}}
.stButton > button[kind="secondary"],
.stButton > button[data-testid="stBaseButton-secondary"] {{
    border-color: {USF_GREEN} !important;
    color: {USF_GREEN} !important;
    font-weight: 600;
    border-radius: 6px;
}}
section[data-testid="stSidebar"] {{
    background: {USF_GREEN_LIGHT};
    border-right: 2px solid {USF_GREEN};
}}
section[data-testid="stSidebar"] .stMarkdown h3 {{
    color: {USF_GREEN};
}}
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
    color: {USF_GREEN};
    border-bottom-color: {USF_GREEN};
}}
[data-testid="stChatMessage"] {{
    border-radius: 10px;
}}
[data-testid="stMetricValue"] {{
    color: {USF_GREEN};
}}
.usf-footer {{
    text-align: center;
    padding: 1rem 0 0.5rem 0;
    font-size: 0.75rem;
    color: {USF_GRAY};
    border-top: 1px solid #e0e0e0;
    margin-top: 2rem;
}}
</style>"""


def inject_branding():
    """Inject the global USF CSS into the current Streamlit page."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_header(title, subtitle=""):
    """Render a USF-branded green header bar with the diamond symbol."""
    import streamlit as st
    symbol_img = get_usf_symbol_img(size=36, color=USF_YELLOW)
    sub_html = f'<div class="usf-header-sub">{subtitle}</div>' if subtitle else ""
    html = (
        '<div class="usf-header">'
        f'{symbol_img}'
        f'<div class="usf-header-title">{title}</div>'
        f'{sub_html}'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_gold_divider():
    """Render the signature USF gold accent line."""
    import streamlit as st
    st.markdown('<div class="usf-gold-divider"></div>', unsafe_allow_html=True)


def render_sso_badge(username):
    """Render the Shibboleth SSO authentication badge."""
    import streamlit as st
    html = (
        '<div class="usf-sso-badge">'
        f'&#x1F512; Authenticated as <strong>{username}</strong> '
        'via Shibboleth SSO</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_footer():
    """Render the FERPA compliance footer."""
    import streamlit as st
    html = (
        '<div class="usf-footer">'
        'This system is protected by USF Shibboleth Single Sign-On. '
        'All student data is handled in compliance with FERPA. '
        'For technical support, contact the Office of the Registrar.'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
