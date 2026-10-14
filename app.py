"""
PricePulse AI v3.5 | Algorithmic Retail Arbitrage & Competitive Intelligence Terminal
Production-Ready Web Application with Tailwind CSS and Lucide Icons.
Cinematic Slate/Navy Dark Mode (#0B0F19, #121826) with 100% interactive client-side simulation.
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

# 2. Seamless Fullscreen Framing
st.markdown("""
<style>
    /* Completely eliminate default Streamlit padding and headers */
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
        height: 100vh !important;
        min-height: 980px !important;
        display: block !important;
    }
    .stApp {
        background-color: #0B0F19 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Load & Render Full Tailwind CSS + Lucide Icons Single-Page Application
html_file = Path(__file__).resolve().parent / "index.html"
if html_file.exists():
    with open(html_file, "r", encoding="utf-8") as f:
        html_code = f.read()
    components.html(html_code, height=980, scrolling=True)
else:
    st.error("index.html not found. Please verify project repository.")
