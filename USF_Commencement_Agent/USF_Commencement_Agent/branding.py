"""
USF Branding Module
====================
Shared colors, typography, CSS, and logo SVG based on the
University of San Francisco Graphic Standards Manual.
"""

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

# ── USF Diamond Cross Symbol (inline SVG) ──
# Simplified representation of the USF crossroads/cross symbol
USF_SYMBOL_SVG = """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">
  <!-- Outer diamond -->
  <g transform="translate(50,50) rotate(45)">
    <rect x="-34" y="-34" width="68" height="68" rx="3"
          fill="none" stroke="{color}" stroke-width="3.5"/>
  </g>
  <!-- Vertical bar -->
  <rect x="45" y="12" width="10" height="76" rx="2" fill="{color}"/>
  <!-- Horizontal bar -->
  <rect x="12" y="45" width="76" height="10" rx="2" fill="{color}"/>
  <!-- Arrow head - top -->
  <polygon points="50,5 40,22 60,22" fill="{color}"/>
  <!-- Arrow head - bottom -->
  <polygon points="50,95 40,78 60,78" fill="{color}"/>
  <!-- Arrow head - left -->
  <polygon points="5,50 22,40 22,60" fill="{color}"/>
  <!-- Arrow head - right -->
  <polygon points="95,50 78,40 78,60" fill="{color}"/>
  <!-- Center diamond accent -->
  <g transform="translate(50,50) rotate(45)">
    <rect x="-6" y="-6" width="12" height="12" fill="{color}"/>
  </g>
</svg>
"""


def get_usf_symbol(size=48, color=None):
    """Return the USF symbol SVG string at the given size."""
    if color is None:
        color = USF_YELLOW
    return USF_SYMBOL_SVG.format(size=size, color=color)


# ── Global CSS injected into every page ──
GLOBAL_CSS = f"""
<style>
    /* ── Typography (Whitney → Source Sans 3 → Arial → sans-serif) ── */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap');

    html, body, [class*="st-"] {{
        font-family: 'Source Sans 3', 'Whitney', Arial, Helvetica, sans-serif;
    }}

    /* ── Header bar ── */
    .usf-header {{
        background: linear-gradient({USF_GREEN}, {USF_GREEN_DARK});
        padding: 1rem 2rem;
        border-radius: 0 0 12px 12px;
        margin: -1rem -1rem 1.5rem -1rem;
        text-align: center;
    }}
    .usf-header h1 {{
        color: white;
        font-family: 'Source Sans 3', Arial, sans-serif;
        font-weight: 700;
        font-size: 1.8rem;
        margin: 0;
        letter-spacing: 0.02em;
    }}
    .usf-header .subtitle {{
        color: {USF_GRAY_ON_BLACK};
        font-size: 0.9rem;
        margin-top: 0.2rem;
        letter-spacing: 0.05em;
    }}

    /* ── Gold accent divider ── */
    .usf-gold-divider {{
        height: 3px;
        background: {USF_YELLOW};
        border: none;
        margin: 1rem 0;
        border-radius: 2px;
    }}

    /* ── SSO badge ── */
    .usf-sso-badge {{
        background: {USF_GREEN_LIGHT};
        border-left: 4px solid {USF_GREEN};
        padding: 0.6rem 1rem;
        border-radius: 0 6px 6px 0;
        font-size: 0.85rem;
        color: #333;
        margin-bottom: 1rem;
    }}

    /* ── Card-style containers ── */
    .usf-card {{
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }}
    .usf-card:hover {{
        border-color: {USF_GREEN};
        box-shadow: 0 2px 8px rgba(0,84,60,0.1);
    }}

    /* ── Primary button overrides ── */
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

    /* ── Secondary button style ── */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="stBaseButton-secondary"] {{
        border-color: {USF_GREEN} !important;
        color: {USF_GREEN} !important;
        font-weight: 600;
        border-radius: 6px;
    }}

    /* ── Sidebar styling ── */
    section[data-testid="stSidebar"] {{
        background: {USF_GREEN_LIGHT};
        border-right: 2px solid {USF_GREEN};
    }}
    section[data-testid="stSidebar"] .stMarkdown h3 {{
        color: {USF_GREEN};
    }}

    /* ── Tab styling ── */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        color: {USF_GREEN};
        border-bottom-color: {USF_GREEN};
    }}

    /* ── Chat message styling ── */
    [data-testid="stChatMessage"] {{
        border-radius: 10px;
    }}

    /* ── Metric value colors ── */
    [data-testid="stMetricValue"] {{
        color: {USF_GREEN};
    }}

    /* ── FERPA footer ── */
    .usf-footer {{
        text-align: center;
        padding: 1rem 0 0.5rem 0;
        font-size: 0.75rem;
        color: {USF_GRAY};
        border-top: 1px solid #e0e0e0;
        margin-top: 2rem;
    }}
</style>
"""


def inject_branding():
    """Inject the global USF CSS into the current Streamlit page.
    Call this at the top of every page after set_page_config."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = ""):
    """Render a USF-branded header bar with the symbol."""
    import streamlit as st
    symbol = get_usf_symbol(size=36, color=USF_YELLOW)
    sub_html = f'<div class="subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="usf-header">
        <div style="display:inline-block; vertical-align:middle; margin-right:10px;">
            {symbol}
        </div>
        <div style="display:inline-block; vertical-align:middle; text-align:left;">
            <h1>{title}</h1>
            {sub_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_gold_divider():
    """Render the signature USF gold accent line."""
    import streamlit as st
    st.markdown('<div class="usf-gold-divider"></div>', unsafe_allow_html=True)


def render_sso_badge(username: str):
    """Render the Shibboleth SSO authentication badge."""
    import streamlit as st
    st.markdown(
        f'<div class="usf-sso-badge">'
        f'&#x1F512; Authenticated as <strong>{username}</strong> '
        f'via Shibboleth SSO</div>',
        unsafe_allow_html=True,
    )


def render_footer():
    """Render the FERPA compliance footer."""
    import streamlit as st
    st.markdown(
        '<div class="usf-footer">'
        'This system is protected by USF Shibboleth Single Sign-On. '
        'All student data is handled in compliance with FERPA. '
        'For technical support, contact the Office of the Registrar.'
        '</div>',
        unsafe_allow_html=True,
    )
