"""
PricePulse AI v3.5 | Algorithmic Retail Arbitrage & Competitive Intelligence Terminal
Custom Bespoke Dark Terminal with Real-Time Arbitrage Simulation,
Circuit Breaker Safety Guard, and Live Price Engine.
"""

from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="PricePulse AI v3.5 | Algorithmic Retail Arbitrage",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Seamless Fullscreen Framing to host the Bespoke Custom Terminal
st.markdown("""
<style>
    /* Clean framing for bespoke interface */
    header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }
    .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    iframe {
        border: none !important;
        width: 100% !important;
        min-height: 100vh !important;
        height: 100vh !important;
        display: block !important;
    }
    .stApp {
        background-color: #0B0F19 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Load & Render Full Bespoke Terminal Application
html_file = Path(__file__).resolve().parent / "index.html"
if html_file.exists():
    with open(html_file, "r", encoding="utf-8") as f:
        html_code = f.read()
    components.html(html_code, height=980, scrolling=True)
else:
    st.error("index.html not found. Please verify repository contents.")
