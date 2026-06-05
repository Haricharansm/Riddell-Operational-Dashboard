import streamlit as st
import base64
from pathlib import Path

st.set_page_config(
    page_title="Riddell Operations & Financial Dashboard",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

def img_to_base64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()

LOGO_B64 = img_to_base64("pages_src/riddell_logo.png")

# Brand colors: Riddell red + dark navy sidebar
st.markdown(f"""
<style>
    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background-color: #1a1a1a;
    }}
    [data-testid="stSidebar"] * {{
        color: #f0f0f0 !important;
    }}
    [data-testid="stSidebar"] .stSelectbox > div > div {{
        background-color: #2d2d2d !important;
        border: 1px solid #444 !important;
        color: #f0f0f0 !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: #333 !important;
    }}

    /* ── Sidebar logo container ── */
    .sidebar-logo {{
        background: #ffffff;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 16px;
        text-align: center;
    }}
    .sidebar-logo img {{
        max-width: 140px;
    }}

    /* ── Top header bar ── */
    .riddell-header {{
        display: flex;
        align-items: center;
        gap: 20px;
        background: #ffffff;
        border-bottom: 3px solid #C8102E;
        padding: 14px 24px;
        margin: -1rem -1rem 1.5rem -1rem;
        border-radius: 0;
    }}
    .riddell-header img {{
        height: 44px;
        width: auto;
    }}
    .riddell-header .header-title {{
        font-size: 20px;
        font-weight: 700;
        color: #1a1a1a;
    }}
    .riddell-header .header-sub {{
        font-size: 12px;
        color: #718096;
        margin-top: 2px;
    }}
    .header-divider {{
        width: 2px; height: 44px;
        background: #C8102E;
        border-radius: 2px;
    }}

    /* ── Metric cards ── */
    div[data-testid="stMetric"] {{
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 3px solid #C8102E;
        border-radius: 10px;
        padding: 16px 20px;
    }}
    div[data-testid="stMetric"] label {{
        color: #718096 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: #1a1a1a !important;
        font-weight: 700 !important;
    }}

    /* ── Section headers ── */
    .section-header {{
        font-size: 16px;
        font-weight: 700;
        color: #1a1a1a;
        border-left: 4px solid #C8102E;
        padding-left: 12px;
        margin: 24px 0 12px 0;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 6px 6px 0 0;
        padding: 8px 20px;
        font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #C8102E !important;
        color: white !important;
    }}

    /* ── Dataframe header ── */
    [data-testid="stDataFrame"] th {{
        background-color: #C8102E !important;
        color: white !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background-color: #C8102E;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
    }}
    .stButton > button:hover {{
        background-color: #a00d25;
        color: white;
    }}

    /* ── Info boxes ── */
    .stInfo {{
        border-left: 4px solid #C8102E !important;
    }}

    /* ── Page background ── */
    .main .block-container {{
        background-color: #f8f9fa;
        padding-top: 1rem;
    }}
</style>
""", unsafe_allow_html=True)

# Inject logo into sidebar
st.sidebar.markdown(f"""
<div class="sidebar-logo">
    <img src="data:image/png;base64,{LOGO_B64}" alt="Riddell" />
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Analytics Platform")
    st.markdown("---")
    page = st.selectbox(
        "Navigate to",
        [
            "🏠 Home",
            "📦 Order Pipeline",
            "⏱️ Aging & SLA Tracking",
            "🏪 Store Details",
            "📊 Financial Dashboard",
            "🏆 Scoreboard & Reps",
        ],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**Data as of:** June 5, 2026")
    st.markdown("**Prototype** — synthetic data")
    st.caption("Connect live data to go live")

# Page header with logo
page_titles = {
    "🏠 Home": ("Operations & Financial Dashboard", "Prototype · Synthetic data · June 5, 2026"),
    "📦 Order Pipeline": ("Order Pipeline View", "Open orders by stage · $ and units"),
    "⏱️ Aging & SLA Tracking": ("Aging Report & SLA Tracking", "Daily ops view · Promise vs. status"),
    "🏪 Store Details": ("Store Details", "Gameday stores · Rep attribution · Performance"),
    "📊 Financial Dashboard": ("Financial Dashboard", "Monthly shipped recap · CY vs LY"),
    "🏆 Scoreboard & Reps": ("Scoreboard & Rep Performance", "Top reps · Top regions · Top stores"),
}
title, subtitle = page_titles.get(page, ("Dashboard", ""))

st.markdown(f"""
<div class="riddell-header">
    <img src="data:image/png;base64,{LOGO_B64}" alt="Riddell" />
    <div class="header-divider"></div>
    <div>
        <div class="header-title">{title}</div>
        <div class="header-sub">{subtitle}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Route pages
if page == "🏠 Home":
    from pages_src.home import render
elif page == "📦 Order Pipeline":
    from pages_src.order_pipeline import render
elif page == "⏱️ Aging & SLA Tracking":
    from pages_src.aging_sla import render
elif page == "🏪 Store Details":
    from pages_src.store_details import render
elif page == "📊 Financial Dashboard":
    from pages_src.financial import render
elif page == "🏆 Scoreboard & Reps":
    from pages_src.scoreboard import render

render()
