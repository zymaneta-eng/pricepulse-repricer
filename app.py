"""
PricePulse AI — E-Commerce Competitor Price Intelligence & Dynamic Repricing Engine.
Sleek Linear/Clay Dark Mode Web Dashboard for Upwork Portfolio.
"""

import io
from pathlib import Path
from datetime import datetime

import openpyxl
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from repricer import RepricingEngine, RepricingRule
from dataset import generate_catalog_dataframe, generate_time_series_history

# 1. Page Configuration
st.set_page_config(
    page_title="PricePulse AI | E-Commerce Repricing Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Modern Linear/Clay Dark Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    .stApp {
        background-color: #0B0F17 !important;
        color: #F8FAFC !important;
    }

    /* Completely hide Streamlit header overlay & toolbar */
    header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2.2rem !important;
        padding-right: 2.2rem !important;
        max-width: 100% !important;
    }

    div[data-testid="stVerticalBlock"] > div {
        gap: 0.6rem !important;
    }

    /* Top Nav */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid rgba(31, 41, 55, 0.6);
        margin-bottom: 0.9rem;
    }
    .brand-title {
        font-size: 1.28rem;
        font-weight: 700;
        color: #F8FAFC;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.02em;
    }
    .version-badge {
        font-size: 0.72rem;
        font-weight: 500;
        color: #94A3B8;
        background: #121826;
        border: 1px solid #1F2937;
        padding: 2px 8px;
        border-radius: 9999px;
    }
    .live-badge {
        font-size: 0.72rem;
        font-weight: 600;
        color: #10B981;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 2px 8px;
        border-radius: 9999px;
    }
    .dev-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 5px 14px;
        border-radius: 9999px;
        background: #121826;
        border: 1px solid #1F2937;
        font-size: 0.82rem;
        font-weight: 500;
        color: #CBD5E1;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 8px #10B981;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    .ghost-nav-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
        background: rgba(18, 24, 38, 0.6);
        border: 1px solid #1F2937;
        color: #94A3B8;
    }

    /* Container Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #121826 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 12px !important;
        padding: 0.9rem 1.2rem !important;
        margin-bottom: 0.4rem !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 0.2rem;
        margin-bottom: 0.6rem;
    }
    .kpi-card {
        background: #121826;
        border: 1px solid #1F2937;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        transition: border-color 0.15s ease, transform 0.15s ease;
    }
    .kpi-card:hover {
        border-color: #374151;
        transform: translateY(-1px);
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.2;
        letter-spacing: -0.02em;
    }
    .kpi-subtitle {
        font-size: 0.74rem;
        font-weight: 600;
        color: #94A3B8;
        margin-top: 0.25rem;
        letter-spacing: 0.02em;
    }

    /* Primary and Secondary Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
        transition: all 0.15s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.55) !important;
    }
    div.stButton > button[kind="secondary"] {
        background: #121826 !important;
        color: #CBD5E1 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #38BDF8 !important;
        color: #FFFFFF !important;
    }

    /* Input Styling */
    div[data-baseweb="select"] > div {
        background-color: #0B0F17 !important;
        border-color: #1F2937 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stTextInput"] input {
        background-color: #121826 !important;
        border: 1px solid #1F2937 !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Top Navigation
st.markdown("""
<div class="top-nav">
  <div style="display: flex; align-items: center; gap: 10px;">
    <span class="brand-title">⚡ PricePulse AI</span>
    <span class="version-badge">v2.0 Enterprise</span>
    <span class="live-badge">● Live Market Radar</span>
  </div>
  <div class="dev-badge">
    Designed &amp; Engineered by Freelancer • Available for Hire
    <span class="status-dot"></span>
  </div>
  <div style="display: flex; gap: 8px;">
    <span class="ghost-nav-btn">📊 Shopify Sync: Active</span>
    <span class="ghost-nav-btn">🛡️ Floor Protection: ON</span>
  </div>
</div>
""", unsafe_allow_html=True)

# 4. Load & Initialize Data
if "catalog_df" not in st.session_state:
    cat_file = Path(__file__).resolve().parent / "catalog.xlsx"
    if cat_file.exists():
        st.session_state.catalog_df = pd.read_excel(cat_file)
    else:
        st.session_state.catalog_df = generate_catalog_dataframe()

if "history_df" not in st.session_state:
    hist_file = Path(__file__).resolve().parent / "price_history.xlsx"
    if hist_file.exists():
        st.session_state.history_df = pd.read_excel(hist_file)
    else:
        st.session_state.history_df = generate_time_series_history()

# 5. Unified Control Strip: Repricing Strategy & Parameters
with st.container(border=True):
    c1, c2, c3, c4, c5 = st.columns([1.5, 1.2, 1.2, 1.3, 1.4])

    with c1:
        st_cat = st.selectbox(
            "Category Filter",
            ["All Categories", "Audio & Headphones", "PC Peripherals", "Displays & Monitors", "Gaming Consoles", "Drones & Cameras"]
        )
    with c2:
        margin_floor = st.slider("Safety Margin Floor %", min_value=10, max_value=35, value=15, step=5, help="Never reprice below cost + this margin")
    with c3:
        undercut_cents = st.selectbox("Buy-Box Beat Margin", ["$0.10", "$0.50", "$1.00", "$2.00"], index=1)
        undercut_val = float(undercut_cents.replace("$", ""))
    with c4:
        stockout_surge = st.slider("Stockout Surge %", min_value=3, max_value=20, value=7, help="Raise price when competitors go out of stock")
    with c5:
        st.markdown("<div style='height: 1.45rem;'></div>", unsafe_allow_html=True)
        run_repricer_btn = st.button("⚡ Run Dynamic Repricer", use_container_width=True, type="primary")

# Execute Repricing Logic
rule = RepricingRule(
    min_margin_percent=float(margin_floor),
    undercut_cents=undercut_val,
    stockout_surge_percent=float(stockout_surge)
)
engine = RepricingEngine(rule=rule)

# Filter catalog
active_df = st.session_state.catalog_df.copy()
if st_cat != "All Categories":
    active_df = active_df[active_df["category"] == st_cat]

processed_df = engine.process_catalog(active_df)

# 6. KPI Telemetry Row
total_skus = len(processed_df)
undercut_needed = (processed_df["status_badge"] == "UNDERCUT").sum()
surges = (processed_df["status_badge"] == "SURGE").sum()
floor_protects = (processed_df["status_badge"] == "PROTECTED").sum()
avg_new_margin = round(processed_df["new_margin_pct"].mean(), 1) if total_skus else 0.0

st.markdown(f"""
<div class="kpi-container">
  <div class="kpi-card">
    <div class="kpi-value">{total_skus} SKUs</div>
    <div class="kpi-subtitle">Tracked Products</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color: #38BDF8;">{undercut_needed} SKUs</div>
    <div class="kpi-subtitle">Buy-Box Undercuts (Action Required)</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color: #10B981;">{surges} SKUs</div>
    <div class="kpi-subtitle">Stockout Surge Opportunities (+Margin)</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value" style="color: #818CF8;">{avg_new_margin}%</div>
    <div class="kpi-subtitle">Projected Average Gross Margin</div>
  </div>
</div>
""", unsafe_allow_html=True)

# 7. Hero Catalog & Dynamic Pricing Table
tb_col1, tb_col2 = st.columns([3.8, 1.2])
with tb_col1:
    search_q = st.text_input("Search catalog", "", placeholder="🔍 Search by SKU, product name, or competitor...", label_visibility="collapsed")
    if search_q:
        mask = processed_df.astype(str).apply(lambda row: row.str.contains(search_q, case=False).any(), axis=1)
        processed_df = processed_df[mask]

with tb_col2:
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine='openpyxl') as writer:
        processed_df.to_excel(writer, index=False, sheet_name="Repriced Catalog")
    st.download_button(
        label="📥 Export Shopify / CSV",
        data=excel_buf.getvalue(),
        file_name="Shopify_Repriced_Catalog.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# Format table presentation
table_view = processed_df.copy()
table_view["Our Price"] = table_view["current_price"].apply(lambda x: f"${x:.2f}")
table_view["Amazon US"] = table_view.apply(lambda r: f"${r['competitor_a_price']:.2f}" if r['comp_a_in_stock'] else f"${r['competitor_a_price']:.2f} (Out of Stock)", axis=1)
table_view["BestBuy"] = table_view.apply(lambda r: f"${r['competitor_b_price']:.2f}" if r['comp_b_in_stock'] else f"${r['competitor_b_price']:.2f} (Out of Stock)", axis=1)
table_view["Recommended Buy-Box"] = table_view["recommended_price"].apply(lambda x: f"${x:.2f}")
table_view["Delta"] = table_view["price_diff"].apply(lambda x: f"+${x:.2f}" if x > 0 else (f"-${abs(x):.2f}" if x < 0 else "$0.00"))
table_view["Projected Margin"] = table_view["new_margin_pct"].apply(lambda x: f"{x:.1f}%")

display_cols = ["sku", "title", "Our Price", "Amazon US", "BestBuy", "Recommended Buy-Box", "Delta", "action", "Projected Margin"]

st.dataframe(
    table_view[display_cols],
    use_container_width=True,
    column_config={
        "sku": st.column_config.TextColumn("SKU", width="small"),
        "title": st.column_config.TextColumn("Product Name", width="large"),
        "Our Price": st.column_config.TextColumn("Current Price", width="small"),
        "Amazon US": st.column_config.TextColumn("Amazon US", width="small"),
        "BestBuy": st.column_config.TextColumn("BestBuy", width="small"),
        "Recommended Buy-Box": st.column_config.TextColumn("⚡ Recommended Buy-Box", width="small"),
        "Delta": st.column_config.TextColumn("Diff", width="small"),
        "action": st.column_config.TextColumn("Repricing Action", width="medium"),
        "Projected Margin": st.column_config.TextColumn("Margin", width="small")
    },
    height=360,
    hide_index=True
)

# 8. Interactive Time-Series Price Trend Chart (Plotly)
st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)
with st.container(border=True):
    ch_col1, ch_col2 = st.columns([3.5, 1.5])
    with ch_col1:
        st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.2rem;'>📈 30-Day Competitor Price Volatility & Trend Analysis</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.8rem; color: #94A3B8; margin-bottom: 0.6rem;'>Historical daily price fluctuations vs Amazon and BestBuy. Real-time detection of price wars.</div>", unsafe_allow_html=True)
    with ch_col2:
        prod_options = processed_df["title"].tolist()
        selected_prod_title = st.selectbox("Select Product to Inspect", prod_options, index=0)

    # Filter history
    prod_row = processed_df[processed_df["title"] == selected_prod_title].iloc[0]
    sku_val = prod_row["sku"]
    hist_sub = st.session_state.history_df[st.session_state.history_df["sku"] == sku_val]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_sub["date"], y=hist_sub["our_price"],
        name="Our Store Price",
        line=dict(color="#6366F1", width=3)
    ))
    fig.add_trace(go.Scatter(
        x=hist_sub["date"], y=hist_sub["comp_a_price"],
        name="Amazon US",
        line=dict(color="#38BDF8", width=2, dash="dot")
    ))
    fig.add_trace(go.Scatter(
        x=hist_sub["date"], y=hist_sub["comp_b_price"],
        name="BestBuy Online",
        line=dict(color="#F59E0B", width=2, dash="dash")
    ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#121826",
        plot_bgcolor="#0B0F17",
        margin=dict(l=30, r=20, t=20, b=30),
        height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="#1F2937"),
        yaxis=dict(showgrid=True, gridcolor="#1F2937", tickprefix="$")
    )
    st.plotly_chart(fig, use_container_width=True)

# 9. Automated Actions & Webhooks
with st.container(border=True):
    act_col1, act_col2 = st.columns([3.5, 1.5])
    with act_col1:
        st.markdown(f"""
        <div style="font-size: 0.88rem; font-weight: 600; color: #F8FAFC;">
          ⚡ Selected Target: <strong>{selected_prod_title}</strong> (<code>{sku_val}</code>)
        </div>
        <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 0.2rem;">
          Strategy: <em>{prod_row['reason']}</em>
        </div>
        """, unsafe_allow_html=True)
    with act_col2:
        sync_shopify_btn = st.button("🚀 Push All Repriced to Shopify API", use_container_width=True, type="primary")
        alert_btn = st.button("🚨 Simulate Telegram Price Drop Alert", use_container_width=True)

    if sync_shopify_btn:
        st.toast(f"✅ Successfully updated {len(processed_df)} live prices on Shopify Store via GraphQL Admin API!", icon="🚀")
        st.success(f"✓ GraphQL Batch Mutation completed: {len(processed_df)} SKUs synchronized.")

    if alert_btn:
        st.toast(f"🔔 Telegram Alert sent: Competitor dropped price on {sku_val} to ${prod_row['competitor_a_price']:.2f}!", icon="🚨")
        st.info(f"📢 Webhook payload dispatched to Telegram channel: Price drop detected on {selected_prod_title}.")
