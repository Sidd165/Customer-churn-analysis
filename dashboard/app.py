"""
Customer Churn Analysis Dashboard
A clean, professional analytics tool — built by a data analyst, for data analysts.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import joblib, os, warnings

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Churn Analysis",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# DESIGN TOKENS (Premium SaaS Dark Theme — Slate & Navy)
# --------------------------------------------------------------------------
BG      = "#0a0e17"   # Rich deep dark slate-navy
SB_BG   = "#0f1423"   # Sidebar background
CARD_BG = "#151b2d"   # Premium card background
BORDER  = "#222a45"   # Borders
TEXT_1  = "#ffffff"   # High-contrast white
TEXT_2  = "#94a3b8"   # Secondary text (slate gray)
TEXT_3  = "#64748b"   # Muted / labels / hints

# Elegant primary accent color (Deep Blue/Indigo)
BLUE    = "#3b82f6"
BLUE_DIM= "rgba(59,130,246,0.1)"

# Status colors for charts/metrics (Vibrant, high-contrast)
RED     = "#f43f5e"   # Rose (churn)
GREEN   = "#10b981"   # Emerald (retained)
AMBER   = "#f59e0b"   # Amber


# --------------------------------------------------------------------------
# CSS — MINIMAL, PURPOSEFUL, NO NEON GRADIENTS
# --------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Keyframe Animations ── */
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
}}
@keyframes fadeInPage {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
}}
@keyframes slideInLeft {{
    from {{ opacity: 0; transform: translateX(-16px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}
@keyframes shimmer {{
    0%   {{ background-position: -200% center; }}
    100% {{ background-position: 200% center; }}
}}
@keyframes pulseGlow {{
    0%, 100% {{ box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06); }}
    50%      {{ box-shadow: 0 4px 20px -1px rgba(59,130,246,0.15), 0 2px 8px -1px rgba(59,130,246,0.08); }}
}}

/* ── Reset ── */
html, body, [class*="css"], [class*="st-"], .stWidget, .stButton, .stSelectbox, .stSlider, .stMarkdown, .stText, p, label, input, select, div, td, th {{
    font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
}}
h1, h2, h3, h4, .page-title, .section-header, .kpi-val, .result-pct, [data-testid="metric-container"] [data-testid="metric-value"], [role="radiogroup"] label {{
    font-family: 'Space Grotesk', -apple-system, sans-serif !important;
}}
/* Restore Streamlit material symbol icons */
[class*="material-symbols"], [class*="MaterialSymbols"], [class*="material-icons"], 
button[data-testid^="stSidebarCollapse"] *, button[data-testid^="stSidebarCollapse"],
button.e12tamyi15 *, button.e12tamyi15, .e12tamyi15 *, .e12tamyi15 {{
    font-family: "material-symbols-rounded", "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons", sans-serif !important;
}}
*, *::before, *::after {{ box-sizing: border-box; }}

/* ── Backgrounds ── */
html, body                  {{ background: {BG} !important; }}
.stApp                      {{ background: {BG} !important; }}
.stApp > header,
[data-testid="stHeader"],
[data-testid="stToolbar"]   {{ background: {BG} !important;
                               border-bottom: 1px solid {BORDER} !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
.main {{
    background: {BG} !important;
}}
.main .block-container {{
    padding: 2.2rem 2.8rem 4rem !important;
    max-width: 1380px !important;
    transition: max-width 0.3s ease, padding 0.3s ease !important;
    animation: fadeInPage 0.45s cubic-bezier(0.16, 1, 0.3, 1) both;
}}

/* ── Full screen when sidebar is collapsed (class toggled by JS) ── */
.block-container.sidebar-collapsed,
.main .block-container.sidebar-collapsed {{
    max-width: 100% !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}}

/* Redundant rule removed – layout handled by .block-container.sidebar-collapsed */


/* ── SIDEBAR — premium dark glass style ── */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {SB_BG} 0%, #08101f 100%) !important;
    border-right: 1px solid rgba(59,130,246,0.15) !important;
    padding: 0 !important;
    transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1), min-width 0.3s cubic-bezier(0.4, 0, 0.2, 1), max-width 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
}}
section[data-testid="stSidebar"]:not([data-collapsed="true"]) {{
    width: 300px !important;
    min-width: 300px !important;
    max-width: 300px !important;
}}
section[data-testid="stSidebar"][data-collapsed="true"] {{
    width: 0px !important;
    min-width: 0px !important;
    max-width: 0px !important;
    border-right: none !important;
    box-shadow: none !important;
}}
section[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
    transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}
section[data-testid="stSidebar"]:not([data-collapsed="true"]) > div:first-child {{
    width: 300px !important;
}}
section[data-testid="stSidebar"][data-collapsed="true"] > div:first-child {{
    width: 0px !important;
}}
section[data-testid="stSidebar"] {{ left: 0 !important; }}

/* ── NUKE all Streamlit inner sidebar wrappers ── */
[data-testid="stSidebarContent"] {{
    padding: 0 !important;
    gap: 0 !important;
    overflow-x: hidden !important;
}}
section[data-testid="stSidebar"] div {{
    gap: 0 !important;
}}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"],
section[data-testid="stSidebar"] .stElementContainer {{
    gap: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
}}

/* ── Sidebar widgets spacing ── */
section[data-testid="stSidebar"] .stMultiSelect,
section[data-testid="stSidebar"] .stSlider {{
    padding: 4px 16px !important;
    margin: 0 !important;
}}
section[data-testid="stSidebar"] .stMarkdown {{
    padding: 0 !important;
    margin: 0 !important;
}}
/* ── Sidebar brand spacing (override nuke rules above) ── */
section[data-testid="stSidebar"] .sidebar-brand {{
    margin-bottom: 16px !important;
    padding-bottom: 0 !important;
}}

/* ── Radio/Nav: every single wrapper must be 100% width, 0 gaps ── */
section[data-testid="stSidebar"] .stRadio {{
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}}
section[data-testid="stSidebar"] .stRadio * {{
    border-radius: 0 !important;
}}
section[data-testid="stSidebar"] .stRadio > div,
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"],
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > div {{
    padding: 0 !important;
    margin: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    gap: 0 !important;
}}

/* ── Sidebar filter labels ── */
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label {{
    color: {TEXT_3} !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
}}

/* Hide radio group outer label */
[data-testid="stSidebar"] .stRadio > label {{ display: none !important; }}

/* ── Nav group container ── */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
    gap: 0 !important;
    flex-direction: column !important;
    width: 100% !important;
    align-items: stretch !important;
    display: flex !important;
}}

/* ── Each nav item row ── */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
    background: transparent !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    border-radius: 0 !important;
    padding: 16px 24px !important;
    color: {TEXT_2} !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    width: 100% !important;
    box-sizing: border-box !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease !important;
    margin: 0 !important;
}}

/* ── Hide the radio button circle ── */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child {{
    display: none !important;
}}

/* ── Label text container ── */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label [data-testid="stMarkdownContainer"] {{
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label [data-testid="stMarkdownContainer"] p {{
    margin: 0 !important;
    padding: 0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.005em !important;
    color: inherit !important;
    white-space: nowrap !important;
}}

/* ── Active nav item ── */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {{
    background: rgba(59,130,246,0.13) !important;
    border-left: 3px solid {BLUE} !important;
    color: #ffffff !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) [data-testid="stMarkdownContainer"] p {{
    color: #ffffff !important;
    font-weight: 700 !important;
}}

/* ── Hover ── */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
    background: rgba(255,255,255,0.04) !important;
    color: #e2e8f0 !important;
    border-left-color: rgba(59,130,246,0.5) !important;
}}

/* ── Multiselect & Selectboxes ── */
[data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] {{
    background: rgba(59,130,246,0.18) !important;
    color: {BLUE} !important;
    border-radius: 4px !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
}}
/* Target standard widgets to avoid white backgrounds */
div[data-baseweb="select"] > div,
[data-testid="stSidebar"] .stMultiSelect > div > div,
[data-testid="stSidebar"] .stMultiSelect div[role="combobox"] {{
    background: {CARD_BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}}
div[data-baseweb="select"] {{
    background: transparent !important;
}}
div[data-baseweb="select"] div {{
    color: #ffffff !important;
}}
div[data-baseweb="menu"] {{
    background-color: {CARD_BG} !important;
    border: 1px solid {BORDER} !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
}}
div[data-baseweb="menu"] li {{
    background-color: transparent !important;
    color: {TEXT_2} !important;
}}
div[data-baseweb="menu"] li:hover {{
    background-color: rgba(255,255,255,0.04) !important;
    color: #ffffff !important;
}}
div[data-baseweb="menu"] li[aria-selected="true"] {{
    background-color: {BLUE_DIM} !important;
    color: {BLUE} !important;
}}

/* ── Custom Sliders ── */
div[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {{
    background-color: {BLUE} !important;
    border-color: {BLUE} !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important;
}}
div[data-testid="stSlider"] [data-baseweb="slider"] > div {{
    background: {BORDER} !important;
}}
div[data-testid="stSlider"] [data-baseweb="slider"] > div > div {{
    background: {BLUE} !important;
}}

/* ── Metrics Cards — animated entrance ── */
[data-testid="metric-container"] {{
    background: {CARD_BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
    padding: 20px 20px !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06) !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    overflow: visible !important;
    animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both !important;
}}
[data-testid="stHorizontalBlock"] > div:nth-child(1) [data-testid="metric-container"] {{ animation-delay: 0s !important; }}
[data-testid="stHorizontalBlock"] > div:nth-child(2) [data-testid="metric-container"] {{ animation-delay: 0.08s !important; }}
[data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="metric-container"] {{ animation-delay: 0.16s !important; }}
[data-testid="stHorizontalBlock"] > div:nth-child(4) [data-testid="metric-container"] {{ animation-delay: 0.24s !important; }}
[data-testid="stHorizontalBlock"] > div:nth-child(5) [data-testid="metric-container"] {{ animation-delay: 0.32s !important; }}
[data-testid="metric-container"]:hover {{
    transform: translateY(-3px) scale(1.01) !important;
    border-color: rgba(59, 130, 246, 0.5) !important;
    box-shadow: 0 12px 20px -3px rgba(0,0,0,0.35), 0 0 0 1px rgba(59,130,246,0.1) !important;
}}
[data-testid="metric-container"] label {{
    color: {TEXT_3} !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    white-space: nowrap !important;
}}
[data-testid="metric-container"] [data-testid="metric-value"] {{
    color: #ffffff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em !important;
}}
[data-testid="metric-container"] [data-testid="metric-delta"] svg {{ display: none !important; }}

/* ── Typography ── */
h1, h2, h3, h4 {{ color: #ffffff !important; font-family: 'Space Grotesk', sans-serif !important; font-weight: 600 !important; letter-spacing: -0.01em; }}
p, span, div, li {{ color: {TEXT_2}; }}
hr {{ border: none !important; border-top: 1px solid {BORDER} !important; margin: 18px 0 !important; }}
a  {{ color: {BLUE} !important; }}

/* ── Page title — animated gradient text ── */
.page-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.85rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff 0%, {BLUE} 50%, #818cf8 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 4s linear infinite, fadeIn 0.6s ease both;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
    line-height: 1.3;
}}
.page-sub {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.85rem;
    color: {TEXT_3};
    margin-bottom: 28px;
    animation: fadeIn 0.8s ease 0.15s both;
    letter-spacing: 0.01em;
}}

/* ── Section headers ── */
.section-header {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    color: {TEXT_3};
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin: 28px 0 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid {BORDER};
    animation: slideInLeft 0.4s ease 0.2s both;
}}

/* ── Insight row cards — animated ── */
.kpi-card {{
    background: linear-gradient(145deg, {CARD_BG} 0%, rgba(30,40,68,0.8) 100%);
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06) !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.3s both;
    position: relative;
    overflow: hidden;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, {BLUE}, transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}}
.kpi-card:hover {{
    transform: translateY(-3px) scale(1.01) !important;
    border-color: rgba(59, 130, 246, 0.4) !important;
    box-shadow: 0 14px 28px -4px rgba(0,0,0,0.35), 0 0 0 1px rgba(59,130,246,0.08) !important;
}}
.kpi-card:hover::before {{
    opacity: 1;
}}
.kpi-val {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.03em;
    line-height: 1.2;
}}
.kpi-val-blue  {{ color: {BLUE} !important;  }}
.kpi-val-red   {{ color: {RED} !important;   }}
.kpi-val-green {{ color: {GREEN} !important; }}
.kpi-label {{
    font-size: 0.7rem;
    color: {TEXT_2};
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}}
.kpi-note {{
    font-size: 0.8rem;
    color: {TEXT_3};
    margin-top: 8px;
    line-height: 1.5;
}}

/* ── Predict result ── */
.result-box {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 36px;
    text-align: center;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}
.result-box.risk-hi {{
    border-color: rgba(244,63,94,0.3) !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 0 40px rgba(244,63,94,0.12) !important;
}}
.result-box.risk-md {{
    border-color: rgba(245,158,11,0.3) !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 0 40px rgba(245,158,11,0.12) !important;
}}
.result-box.risk-lo {{
    border-color: rgba(16,185,129,0.3) !important;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 0 40px rgba(16,185,129,0.12) !important;
}}
.result-pct {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 4.5rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 8px;
    animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}}
.result-pct-hi {{ color: {RED};   }}
.result-pct-md {{ color: {AMBER}; }}
.result-pct-lo {{ color: {GREEN}; }}
.result-badge {{
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 6px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}}
.badge-hi {{ background: rgba(244,63,94,0.15);  color: {RED};   border: 1px solid rgba(244,63,94,0.3);  }}
.badge-md {{ background: rgba(245,158,11,0.15); color: {AMBER}; border: 1px solid rgba(245,158,11,0.3); }}
.badge-lo {{ background: rgba(16,185,129,0.15);  color: {GREEN}; border: 1px solid rgba(16,185,129,0.3);  }}
.result-meta {{ font-size: 0.82rem; color: {TEXT_3}; margin-top: 16px; }}

/* ── Premium Tactile Predict Button ── */
.stButton > button,
.stButton > button * {{
    color: #ffffff !important;
}}
.stButton > button {{
    background: linear-gradient(135deg, {BLUE} 0%, #1d4ed8 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    padding: 14px 28px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
    color: #ffffff !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    width: 100% !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, #4f46e5 0%, {BLUE} 100%) !important;
    box-shadow: 0 10px 25px rgba(59, 130, 246, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.25) !important;
    transform: translateY(-2px) scale(1.02) !important;
}}
.stButton > button:active {{
    transform: translateY(1px) scale(0.98) !important;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2) !important;
}}

/* ── Selects/sliders in predict form ── */
div[data-baseweb="select"], div[data-baseweb="select"] > div, .stSelectbox > div > div, .stMultiSelect > div > div {{
    background-color: {CARD_BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    transition: all 0.2s ease !important;
}}
div[data-baseweb="select"]:hover, div[data-baseweb="select"] > div:hover, .stSelectbox > div > div:hover, .stMultiSelect > div > div:hover {{
    border-color: rgba(59, 130, 246, 0.4) !important;
    box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.1) !important;
}}
.stSelectbox label, .stSlider label {{
    color: {TEXT_3} !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}}

/* ── Expander ── */
.stExpander {{
    background: {CARD_BG} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
}}
.stExpander summary {{ color: {TEXT_2} !important; font-weight: 500 !important; font-size: 0.875rem !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {SB_BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 2px; }}

/* ── Footer ── */
.footer {{
    font-size: 0.72rem;
    color: {TEXT_3};
    text-align: center;
    margin-top: 60px;
    padding-top: 16px;
    border-top: 1px solid {BORDER};
}}
</style>

<script>
// Watch sidebar collapse state and toggle class on block-container
(function() {{
    function update() {{
        var sb = document.querySelector('section[data-testid="stSidebar"]');
        var bc = document.querySelector('.block-container');
        if (sb && bc) {{
            if (sb.getAttribute('data-collapsed') === 'true') {{
                bc.classList.add('sidebar-collapsed');
            }} else {{
                bc.classList.remove('sidebar-collapsed');
            }}
        }}
    }}
    // Run on load
    update();
    // Watch for attribute changes on sidebar
    var observer = new MutationObserver(update);
    var target = document.querySelector('section[data-testid="stSidebar"]');
    if (target) {{
        observer.observe(target, {{ attributes: true, attributeFilter: ['data-collapsed'] }});
    }} else {{
        // Sidebar might load after this script, so watch the whole body briefly
        var bodyObs = new MutationObserver(function() {{
            var sb = document.querySelector('section[data-testid="stSidebar"]');
            if (sb) {{
                bodyObs.disconnect();
                update();
                observer.observe(sb, {{ attributes: true, attributeFilter: ['data-collapsed'] }});
            }}
        }});
        bodyObs.observe(document.body, {{ childList: true, subtree: true }});
    }}
}})();

// Count-up animations for KPI cards & metrics
(function() {{
    function animateValue(obj, start, end, duration, formatter) {{
        let startTimestamp = null;
        const step = (timestamp) => {{
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            const easeProgress = progress * (2 - progress);
            const current = start + easeProgress * (end - start);
            obj.innerText = formatter(current);
            if (progress < 1) {{
                window.requestAnimationFrame(step);
            }} else {{
                obj.innerText = formatter(end);
            }}
        }};
        window.requestAnimationFrame(step);
    }}

    function parseValue(str) {{
        const clean = str.trim();
        if (!clean) return null;
        
        const numRegex = /[-+]?[0-9,]*\.?[0-9]+/g;
        const match = clean.match(numRegex);
        if (!match) return null;
        
        const numStr = match[0];
        const num = parseFloat(numStr.replace(/,/g, ''));
        
        const idx = clean.indexOf(numStr);
        const prefix = clean.substring(0, idx);
        const suffix = clean.substring(idx + numStr.length);
        
        let decimals = 0;
        if (numStr.includes('.')) {{
            decimals = numStr.split('.')[1].length;
        }}
        
        const hasCommas = numStr.includes(',');
        
        return {{
            value: num,
            prefix: prefix,
            suffix: suffix,
            decimals: decimals,
            hasCommas: hasCommas
        }};
    }}

    function formatValue(val, parsed) {{
        let v = val;
        if (parsed.decimals > 0) {{
            v = v.toFixed(parsed.decimals);
        }} else {{
            v = Math.round(v).toString();
        }}
        if (parsed.hasCommas) {{
            const parts = v.split('.');
            parts[0] = parts[0].replace(/\B(?=(\d{{3}})+(?!\d))/g, ",");
            v = parts.join('.');
        }}
        return parsed.prefix + v + parsed.suffix;
    }}

    function checkAndAnimate() {{
        const selectors = [
            '[data-testid="metric-container"] [data-testid="metric-value"]',
            '.kpi-val',
            '.result-pct'
        ];
        selectors.forEach(sel => {{
            const elements = document.querySelectorAll(sel);
            elements.forEach(el => {{
                if (el.dataset.animating === "true") return;
                
                const text = el.innerText.trim();
                if (!text) return;
                
                if (el.dataset.lastValue === text) return;
                
                const parsed = parseValue(text);
                if (parsed === null) return;
                
                const prevValText = el.dataset.lastValue || "";
                let prevParsed = parseValue(prevValText);
                let startValue = 0;
                if (prevParsed !== null && prevParsed.prefix === parsed.prefix && prevParsed.suffix === parsed.suffix) {{
                    startValue = prevParsed.value;
                }}
                
                el.dataset.lastValue = text;
                el.dataset.animating = "true";
                
                if (startValue === parsed.value) {{
                    el.dataset.animating = "false";
                    return;
                }}
                
                animateValue(el, startValue, parsed.value, 800, (current) => {{
                    const formatted = formatValue(current, parsed);
                    el.dataset.lastValue = formatted;
                    return formatted;
                }});
                
                setTimeout(() => {{
                    el.dataset.animating = "false";
                    el.dataset.lastValue = text;
                }}, 850);
            }});
        }});
    }}

    // Check periodically for updates
    setInterval(checkAndAnimate, 300);
}})();
</script>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# PLOTLY THEME — dark, minimal, premium
# --------------------------------------------------------------------------
_BG     = "rgba(0,0,0,0)"
_PBG    = CARD_BG      # Matches card background
_GRID   = "rgba(255,255,255,0.03)" # Very thin, elegant gridline
_TICK   = "#222c47"    # Tick marks

def chart(fig, h=300, title="", xt="", yt="", xr=None, yr=None,
          gx=True, gy=True, leg=True, extra=None):
    lo = dict(
        paper_bgcolor=_BG, plot_bgcolor=_PBG, height=h, showlegend=leg,
        font=dict(family="Plus Jakarta Sans", color=TEXT_2, size=11),
        title=dict(text=title, x=0, font=dict(size=13, color="#ffffff", family="Plus Jakarta Sans")),
        margin=dict(t=40, b=36, l=10, r=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                    font=dict(color=TEXT_2, size=11), orientation="h",
                    x=0, y=-0.18),
        hoverlabel=dict(bgcolor="#151b2d", bordercolor=BORDER,
                        font=dict(color="#ffffff", size=11, family="Plus Jakarta Sans")),
    )
    if extra: lo.update(extra)
    fig.update_layout(**lo)
    xkw = dict(gridcolor=_GRID, linecolor=_TICK, tickcolor=_TICK, zeroline=False,
               showgrid=gx, tickfont=dict(color=TEXT_2, size=10),
               title_text=xt, title_font=dict(color=TEXT_2, size=10))
    ykw = dict(gridcolor=_GRID, linecolor=_TICK, tickcolor=_TICK, zeroline=False,
               showgrid=gy, tickfont=dict(color=TEXT_2, size=10),
               title_text=yt, title_font=dict(color=TEXT_2, size=10))
    if xr: xkw["range"] = xr
    if yr: ykw["range"] = yr
    fig.update_xaxes(**xkw)
    fig.update_yaxes(**ykw)
    return fig


# --------------------------------------------------------------------------
# DATA & MODEL
# --------------------------------------------------------------------------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@st.cache_data
def load_data():
    p = os.path.join(BASE, "data", "processed", "churn_cleaned.csv")
    r = os.path.join(BASE, "data", "raw", "telco_churn.csv")
    if os.path.exists(p):
        return pd.read_csv(p)
    elif os.path.exists(r):
        df = pd.read_csv(r)
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        df["TotalCharges"].fillna(df["TotalCharges"].median(), inplace=True)
        df["ChurnBinary"] = (df["Churn"] == "Yes").astype(int)
        return df
    return None

@st.cache_resource
def load_model():
    mp = os.path.join(BASE, "models", "random_forest.pkl")
    fp = os.path.join(BASE, "models", "feature_names.csv")
    if os.path.exists(mp):
        m = joblib.load(mp)
        f = pd.read_csv(fp).iloc[:, 0].tolist() if os.path.exists(fp) else []
        return m, f
    return None, []

df = load_data()
model, feat_names = load_model()

if df is None:
    st.error("Dataset not found — run:  python data/generate_data.py")
    st.stop()

# --------------------------------------------------------------------------
# SIDEBAR  — flat navigation + compact filters
# --------------------------------------------------------------------------
with st.sidebar:

    # ── Sidebar brand header (clean wordmark, no emoji) ──
    st.markdown(f"""
    <div class="sidebar-brand" style="border-bottom: 1px solid rgba(59,130,246,0.18); padding-top: 0;">
        <div style="height: 3px; background: linear-gradient(90deg, {BLUE}, transparent);"></div>
        <div style="padding: 4px 24px 10px;">
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 700; color: #fff; letter-spacing: -0.03em; line-height:1.2;">Churn Analysis</div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 0.68rem; color: {TEXT_3}; margin-top: 5px; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 500;">Telco Retention</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", ["Overview", "EDA", "Model", "Predict"],
                    label_visibility="collapsed")

    # ── Filter section header ──
    st.markdown(f"""
    <div style="padding: 20px 24px 10px; margin-top: 4px;">
        <div style="font-size: 0.6rem; font-weight: 700; color: {TEXT_3}; text-transform: uppercase; letter-spacing: 0.15em; display:flex; align-items:center; gap:8px;">
            <div style="flex:1; height:1px; background:{BORDER};"></div>
            <span>Filters</span>
            <div style="flex:1; height:1px; background:{BORDER};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    all_c = sorted(df["Contract"].dropna().unique().tolist())
    all_i = sorted(df["InternetService"].dropna().unique().tolist())
    sel_c = st.multiselect("Contract", all_c, default=all_c)
    sel_i = st.multiselect("Internet", all_i, default=all_i)
    t_lo  = int(df["tenure"].min())
    t_hi  = int(df["tenure"].max())
    t_rng = st.slider("Tenure (months)", t_lo, t_hi, (t_lo, t_hi))

    uc  = sel_c or all_c
    ui  = sel_i or all_i
    dff = df[df["Contract"].isin(uc) & df["InternetService"].isin(ui)
             & df["tenure"].between(*t_rng)]

    n      = len(dff)
    cp     = dff["ChurnBinary"].mean() * 100 if n else 0

    # ── Stats summary card ──
    st.markdown(f"""
    <div style="margin: 8px 12px 16px; padding: 14px 16px;
                background: rgba(59,130,246,0.06);
                border: 1px solid rgba(59,130,246,0.15);
                border-radius: 10px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="color:{TEXT_3}; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em;">Customers</span>
            <span style="color:#fff; font-weight:700; font-size:0.95rem;">{n:,}</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="color:{TEXT_3}; font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em;">Churn Rate</span>
            <span style="color:{RED}; font-weight:700; font-size:0.95rem;">{cp:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================================================
# PAGE — OVERVIEW
# ==========================================================================
if page == "Overview":

    st.markdown('<div class="page-title">Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Telco customer churn · 7,043 records</div>',
                unsafe_allow_html=True)

    total   = len(dff)
    churned = int(dff["ChurnBinary"].sum())
    ret     = total - churned
    cpct    = churned / total * 100 if total else 0
    rev     = dff[dff["Churn"] == "Yes"]["MonthlyCharges"].sum() if "Churn" in dff.columns else 0
    avg_t   = dff[dff["ChurnBinary"] == 1]["tenure"].mean() if churned else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Customers",     f"{total:,}")
    k2.metric("Churned",             f"{churned:,}",   delta=f"-{cpct:.1f}%", delta_color="inverse")
    k3.metric("Retained",            f"{ret:,}")
    k4.metric("Rev. at Risk / Mo",   f"${rev:,.0f}",   delta="monthly", delta_color="off")
    k5.metric("Avg Tenure (Churned)",f"{avg_t:.0f} mo",delta_color="off")

    st.markdown('<div class="section-header">Distribution</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")

    with col1:
        fig = go.Figure(go.Pie(
            labels=["Retained", "Churned"], values=[ret, churned],
            hole=0.62,
            marker=dict(colors=[GREEN, RED], line=dict(color=BG, width=4)),
            textinfo="none",
            hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>",
        ))
        fig.add_annotation(
            text=f"<b>{cpct:.1f}%</b><br><span style='font-size:10px'>churn</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=17, color=TEXT_1, family="Inter"))
        chart(fig, h=260, title="Churn split",
              extra={"legend": dict(orientation="h", x=0.5, xanchor="center", y=-0.08,
                                   bgcolor="rgba(0,0,0,0)", borderwidth=0,
                                   font=dict(color=TEXT_3, size=11))})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        ct = dff.groupby("Contract")["ChurnBinary"].mean().mul(100).round(1).reset_index()
        ct.columns = ["Contract", "pct"]
        ct = ct.sort_values("pct")
        bc = [GREEN if v < 20 else AMBER if v < 32 else RED for v in ct["pct"]]
        fig2 = go.Figure(go.Bar(
            x=ct["pct"], y=ct["Contract"], orientation="h",
            marker=dict(color=bc, line=dict(color="rgba(0,0,0,0)")),

            text=[f"{v:.1f}%" for v in ct["pct"]], textposition="outside",
            textfont=dict(color=TEXT_2, size=11),
            width=0.45,
            hovertemplate="<b>%{y}</b> — %{x:.1f}%<extra></extra>",
        ))
        chart(fig2, h=260, title="Churn rate by contract type",
              xt="Churn rate (%)", xr=[0, ct["pct"].max() * 1.3],
              extra={"bargap": 0.4}, leg=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Key numbers</div>', unsafe_allow_html=True)
    m2m  = dff[dff["Contract"] == "Month-to-month"]["ChurnBinary"].mean() * 100
    newc = dff[dff["tenure"] < 12]["ChurnBinary"].mean() * 100
    fo   = dff[dff["InternetService"] == "Fiber optic"]["ChurnBinary"].mean() * 100 \
           if "Fiber optic" in dff["InternetService"].values else 0

    i1, i2, i3 = st.columns(3, gap="medium")
    with i1:
        st.markdown(f"""<div class='kpi-card'>
            <div class='kpi-val kpi-val-red'>{m2m:.1f}%</div>
            <div class='kpi-label'>Month-to-month churn</div>
            <div class='kpi-note'>vs {dff[dff["Contract"]=="Two year"]["ChurnBinary"].mean()*100:.1f}% for 2-year contracts</div>
        </div>""", unsafe_allow_html=True)
    with i2:
        st.markdown(f"""<div class='kpi-card'>
            <div class='kpi-val kpi-val-blue'>${rev:,.0f}</div>
            <div class='kpi-label'>Monthly revenue at risk</div>
            <div class='kpi-note'>From {churned:,} churned customers at avg ${rev/max(churned,1):.0f}/mo</div>
        </div>""", unsafe_allow_html=True)
    with i3:
        st.markdown(f"""<div class='kpi-card'>
            <div class='kpi-val kpi-val-red'>{newc:.1f}%</div>
            <div class='kpi-label'>New customer churn (&lt;12 mo)</div>
            <div class='kpi-note'>Drops to {dff[dff["tenure"]>=60]["ChurnBinary"].mean()*100:.1f}% after 60 months</div>
        </div>""", unsafe_allow_html=True)


# ==========================================================================
# PAGE — EDA
# ==========================================================================
elif page == "EDA":

    st.markdown('<div class="page-title">Exploratory Data Analysis</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Distributions, segment breakdown, and cohort analysis</div>',
                unsafe_allow_html=True)

    cc = "Churn" if "Churn" in dff.columns else None

    st.markdown('<div class="section-header">Distributions</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")

    with c1:
        fig = go.Figure()
        for val, col, nm in [("No", GREEN, "Retained"), ("Yes", RED, "Churned")]:
            sub = dff[dff[cc] == val]["tenure"] if cc else \
                  dff[dff["ChurnBinary"] == (1 if val == "Yes" else 0)]["tenure"]
            fig.add_trace(go.Histogram(
                x=sub, name=nm, nbinsx=26,
                marker=dict(color=col, opacity=0.7, line=dict(color=BG, width=0.4)),
                hovertemplate=f"<b>{nm}</b> — %{{y}} customers at %{{x}} months<extra></extra>"))
        chart(fig, h=280, title="Tenure distribution by churn status",
              xt="Tenure (months)", yt="Customers",
              extra={"barmode": "overlay"})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = go.Figure()
        colors_rgba = {"No": f"rgba(63,185,80,0.12)", "Yes": f"rgba(229,83,75,0.12)"}
        for val, col, nm in [("No", GREEN, "Retained"), ("Yes", RED, "Churned")]:
            sub = dff[dff[cc] == val]["MonthlyCharges"] if cc else \
                  dff[dff["ChurnBinary"] == (1 if val == "Yes" else 0)]["MonthlyCharges"]
            fig.add_trace(go.Box(
                x=[nm]*len(sub), y=sub, name=nm,
                marker_color=col, line_color=col,
                fillcolor=colors_rgba[val],
                boxmean="sd",
                hovertemplate=f"<b>{nm}</b><br>${{%{{y:.2f}}}}/mo<extra></extra>"))
        chart(fig, h=280, title="Monthly charges by churn status",
              yt="Monthly charges ($)", leg=True,
              extra={"boxmode": "group"})
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Churn rate by segment</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2, gap="large")

    with c3:
        inet = dff.groupby("InternetService")["ChurnBinary"].mean().mul(100).round(1).reset_index()
        inet.columns = ["service", "pct"]
        inet = inet.sort_values("pct", ascending=False)
        bc3  = [RED if v > 30 else AMBER if v > 22 else GREEN for v in inet["pct"]]
        fig  = go.Figure(go.Bar(
            x=inet["service"], y=inet["pct"],
            marker=dict(color=bc3, line=dict(color="rgba(0,0,0,0)")),

            text=[f"{v:.1f}%" for v in inet["pct"]], textposition="outside",
            textfont=dict(color=TEXT_2, size=11),
            hovertemplate="<b>%{x}</b> — %{y:.1f}%<extra></extra>"))
        chart(fig, h=260, title="By internet service",
              yt="Churn rate (%)", yr=[0, inet["pct"].max() * 1.3], leg=False)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        pay = dff.groupby("PaymentMethod")["ChurnBinary"].mean().mul(100).round(1).reset_index()
        pay.columns = ["method", "pct"]
        pay["short"] = pay["method"] \
            .str.replace(" (automatic)", "", regex=False) \
            .str.replace("Bank transfer", "Bank xfer", regex=False)
        pay = pay.sort_values("pct")
        bc4 = [RED if v > 30 else AMBER if v > 25 else GREEN for v in pay["pct"]]
        fig = go.Figure(go.Bar(
            x=pay["pct"], y=pay["short"], orientation="h",
            marker=dict(color=bc4, line=dict(color="rgba(0,0,0,0)")),

            text=[f"{v:.1f}%" for v in pay["pct"]], textposition="outside",
            textfont=dict(color=TEXT_2, size=11), width=0.5,
            hovertemplate="<b>%{y}</b> — %{x:.1f}%<extra></extra>"))
        chart(fig, h=260, title="By payment method",
              xt="Churn rate (%)", xr=[0, pay["pct"].max() * 1.35], leg=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Customer lifetime cohort</div>', unsafe_allow_html=True)
    dc = dff.copy()
    dc["cohort"] = pd.cut(dc["tenure"],
                          bins=[0, 11, 23, 35, 47, 59, 1000],
                          labels=["0–11 mo", "12–23 mo", "24–35 mo",
                                  "36–47 mo", "48–59 mo", "60+ mo"])
    coh = dc.groupby("cohort", observed=True)["ChurnBinary"].mean().mul(100).round(1).reset_index()
    coh.columns = ["Cohort", "pct"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=coh["Cohort"].astype(str), y=coh["pct"],
        mode="lines+markers",
        line=dict(color=BLUE, width=2),
        marker=dict(size=7, color=BLUE,
                    line=dict(color=_PBG, width=2)),
        fill="tozeroy",
        fillcolor=BLUE_DIM,
        hovertemplate="<b>%{x}</b><br>Churn rate: %{y:.1f}%<extra></extra>"))
    avg = coh["pct"].mean()
    fig.add_hline(y=avg, line_dash="dot", line_color=_TICK,
                  annotation_text=f"avg {avg:.1f}%",
                  annotation_font_color=_TICK, annotation_font_size=10)
    chart(fig, h=240, title="Churn rate by tenure cohort",
          xt="Cohort", yt="Churn rate (%)", yr=[0, coh["pct"].max() * 1.35], leg=False)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Show raw data (100 rows)"):
        st.dataframe(dff.sample(min(100, len(dff))).reset_index(drop=True),
                     use_container_width=True, height=240)


# ==========================================================================
# PAGE — MODEL
# ==========================================================================
elif page == "Model":

    st.markdown('<div class="page-title">Model Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Random Forest trained on 5,634 customers</div>',
                unsafe_allow_html=True)

    if model is None:
        st.warning("Run `python notebooks/02_modeling.py` to train the model.")
    else:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import (roc_auc_score, roc_curve,
                                     confusion_matrix, classification_report)

        drop_c = [c for c in ["Churn", "ChurnBinary", "customerID"] if c in df.columns]
        Xd = pd.get_dummies(df.drop(columns=drop_c), drop_first=True)
        y  = df["ChurnBinary"]
        for c in feat_names:
            if c not in Xd.columns: Xd[c] = 0
        if feat_names: Xd = Xd[feat_names]
        Xt, Xv, yt, yv = train_test_split(Xd, y, test_size=0.2, random_state=42, stratify=y)
        yp  = model.predict(Xv)
        ypr = model.predict_proba(Xv)[:, 1]
        auc = roc_auc_score(yv, ypr)
        rep = classification_report(yv, yp, output_dict=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ROC-AUC",           f"{auc:.3f}")
        m2.metric("Precision (churn)", f"{rep['1']['precision']:.3f}")
        m3.metric("Recall (churn)",    f"{rep['1']['recall']:.3f}")
        m4.metric("F1 (churn)",        f"{rep['1']['f1-score']:.3f}")

        st.markdown('<div class="section-header">Evaluation</div>', unsafe_allow_html=True)
        r1, r2 = st.columns(2, gap="large")

        with r1:
            fpr, tpr, _ = roc_curve(yv, ypr)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=fpr, y=tpr, mode="lines",
                name=f"RF (AUC {auc:.3f})",
                line=dict(color=BLUE, width=2),
                fill="tozeroy", fillcolor=BLUE_DIM,
                hovertemplate="FPR %{x:.3f} / TPR %{y:.3f}<extra></extra>"))
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1], mode="lines", name="Random",
                line=dict(color=_TICK, dash="dot", width=1.5)))
            chart(fig, h=310, title="ROC curve",
                  xt="False positive rate", xr=[-0.02, 1.02],
                  yt="True positive rate",  yr=[-0.02, 1.02])
            st.plotly_chart(fig, use_container_width=True)

        with r2:
            cm = confusion_matrix(yv, yp)
            labels = [["TN", "FP"], ["FN", "TP"]]
            ann = [[f"<b>{cm[i][j]:,}</b><br><span style='font-size:10px'>{labels[i][j]}</span>"
                    for j in range(2)] for i in range(2)]
            fig = go.Figure(go.Heatmap(
                z=cm,
                x=["Pred: retained", "Pred: churned"],
                y=["Actual: retained", "Actual: churned"],
                colorscale=[[0, _PBG], [0.4, "#193a2b"], [1, GREEN]],
                showscale=False,
                text=ann, texttemplate="%{text}",
                textfont=dict(size=14, color=TEXT_1),
                hovertemplate="<b>%{x}</b> / %{y}<br>%{z:,}<extra></extra>"))
            chart(fig, h=310, title="Confusion matrix",
                  gx=False, gy=False, leg=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown('<div class="section-header">Feature importance</div>', unsafe_allow_html=True)
        if hasattr(model, "feature_importances_") and feat_names:
            imp = pd.Series(model.feature_importances_,
                            index=feat_names).nlargest(15).sort_values()
            colors = [BLUE if v < imp.median() else RED for v in imp.values]
            fig = go.Figure(go.Bar(
                x=imp.values, y=imp.index, orientation="h",
                marker=dict(color=colors, line=dict(color="rgba(0,0,0,0)")),

                text=[f"{v:.3f}" for v in imp.values], textposition="outside",
                textfont=dict(color=TEXT_3, size=9), width=0.6,
                hovertemplate="<b>%{y}</b><br>importance: %{x:.4f}<extra></extra>"))
            fig.add_vline(x=imp.median(), line_dash="dot", line_color=_TICK,
                          annotation_text="median",
                          annotation_font_color=_TICK, annotation_font_size=9)
            chart(fig, h=400, title="Top 15 features by importance",
                  xt="Importance", xr=[0, imp.max() * 1.3],
                  extra={"bargap": 0.3}, leg=False)
            fig.update_yaxes(tickfont=dict(size=9, color=_TICK))
            st.plotly_chart(fig, use_container_width=True)


# ==========================================================================
# PAGE — PREDICT
# ==========================================================================
elif page == "Predict":

    st.markdown('<div class="page-title">Predict Churn Risk</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-sub">Enter a customer\'s profile to estimate churn probability</div>',
                unsafe_allow_html=True)

    if model is None:
        st.warning("Run `python notebooks/02_modeling.py` to train the model.")
    else:
        st.markdown('<div class="section-header">Customer profile</div>', unsafe_allow_html=True)
        p1, p2, p3 = st.columns(3, gap="large")

        with p1:
            st.caption("DEMOGRAPHICS")
            gender  = st.selectbox("Gender",          ["Male", "Female"])
            senior  = st.selectbox("Senior citizen",  ["No", "Yes"])
            partner = st.selectbox("Has partner",      ["Yes", "No"])
            deps    = st.selectbox("Dependents",       ["No", "Yes"])
            tenure  = st.slider("Tenure (months)",     1, 72, 12)

        with p2:
            st.caption("SERVICES")
            phone   = st.selectbox("Phone service",    ["Yes", "No"])
            lines   = st.selectbox("Multiple lines",   ["No", "Yes", "No phone service"])
            inet    = st.selectbox("Internet service", ["Fiber optic", "DSL", "No"])
            osec    = st.selectbox("Online security",  ["No", "Yes", "No internet service"])
            tsup    = st.selectbox("Tech support",     ["No", "Yes", "No internet service"])

        with p3:
            st.caption("BILLING")
            contract = st.selectbox("Contract",        ["Month-to-month", "One year", "Two year"])
            paper    = st.selectbox("Paperless billing",["Yes", "No"])
            payment  = st.selectbox("Payment method",  ["Electronic check", "Mailed check",
                                                         "Bank transfer (automatic)",
                                                         "Credit card (automatic)"])
            mchg     = st.slider("Monthly charges ($)", 18.0, 120.0, 65.0, 0.5)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        col_btn_1, col_btn_2, col_btn_3 = st.columns([1.1, 0.8, 1.1])
        with col_btn_2:
            run_pred = st.button("⚡ Calculate Churn Risk")

        if run_pred:
            row = {
                "gender": gender, "SeniorCitizen": int(senior == "Yes"),
                "Partner": partner, "Dependents": deps, "tenure": tenure,
                "PhoneService": phone, "MultipleLines": lines,
                "InternetService": inet, "OnlineSecurity": osec,
                "OnlineBackup": "No", "DeviceProtection": "No", "TechSupport": tsup,
                "StreamingTV": "No", "StreamingMovies": "No", "Contract": contract,
                "PaperlessBilling": paper, "PaymentMethod": payment,
                "MonthlyCharges": mchg, "TotalCharges": mchg * tenure,
            }
            inp = pd.get_dummies(pd.DataFrame([row]), drop_first=True)
            for c in feat_names:
                if c not in inp.columns: inp[c] = 0
            if feat_names: inp = inp[feat_names]

            prob = model.predict_proba(inp)[0][1]
            pct  = prob * 100

            _, mid, _ = st.columns([1, 1.6, 1])
            with mid:
                if pct >= 65:
                    pc, bc, blab = "result-pct-hi", "badge-hi", "High risk"
                    rc = "risk-hi"
                    gc = RED
                elif pct >= 35:
                    pc, bc, blab = "result-pct-md", "badge-md", "Medium risk"
                    rc = "risk-md"
                    gc = AMBER
                else:
                    pc, bc, blab = "result-pct-lo", "badge-lo", "Low risk"
                    rc = "risk-lo"
                    gc = GREEN

                st.markdown(f"""
                <div class='result-box {rc}'>
                    <div style='font-size:0.65rem; font-weight:600; color:{TEXT_3};
                                text-transform:uppercase; letter-spacing:0.1em;
                                margin-bottom:8px;'>Churn probability</div>
                    <div class='result-pct {pc}'>{pct:.1f}%</div>
                    <div style='margin:10px 0;'>
                        <span class='result-badge {bc}'>{blab}</span>
                    </div>
                    <div class='result-meta'>
                        {contract} · {tenure} mo tenure · ${mchg:.0f}/mo
                    </div>
                </div>""", unsafe_allow_html=True)

                # Clean gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=pct,
                    number=dict(suffix="%",
                                font=dict(size=26, color=TEXT_1, family="Plus Jakarta Sans")),
                    gauge=dict(
                        axis=dict(range=[0, 100], tickcolor=_TICK,
                                  tickfont=dict(color=TEXT_2, size=9)),
                        bar=dict(color=gc, thickness=0.2),
                        bgcolor=_PBG, borderwidth=0,
                        steps=[
                            dict(range=[0, 35],   color="rgba(16,185,129,0.08)"),
                            dict(range=[35, 65],  color="rgba(245,158,11,0.08)"),
                            dict(range=[65, 100], color="rgba(244,63,94,0.08)"),
                        ],
                    )))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Plus Jakarta Sans", color=TEXT_2),
                    height=220, margin=dict(t=10, b=10, l=16, r=16))
                st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------------------------------
# FOOTER
# --------------------------------------------------------------------------
st.markdown("""
<div class='footer'>
    Churn Analysis Dashboard &nbsp;·&nbsp;
    Python · Pandas · Scikit-learn · Plotly · Streamlit
</div>
""", unsafe_allow_html=True)
