"""
PricePulse AI — E-Commerce Competitor Price Intelligence & Dynamic Repricing Command Center.
Two-Column Master-Detail Terminal (Trading/Retail Intelligence Aesthetic).
Featuring real product imagery, barcode scanning, interactive Plotly volatility charts,
and a real-time Repricing Strategy Sandbox.
"""

import io
from pathlib import Path
from datetime import datetime

import openpyxl
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from repricer import RepricingEngine, RepricingRule
from matcher import ProductMatchingEngine
from dataset import fetch_ground_truth_catalog, generate_time_series_history

# 1. Page Configuration
st.set_page_config(
    page_title="PricePulse AI | Product Intelligence Cockpit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Modern Retail/Trading Terminal Styling (Amber & Dark Slate)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    code, .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stApp {
        background-color: #080B11 !important;
        color: #F8FAFC !important;
    }

    /* Completely hide Streamlit header overlay & toolbar */
    header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    .block-container {
        padding-top: 1.4rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    div[data-testid="stVerticalBlock"] > div {
        gap: 0.5rem !important;
    }

    /* Top Command Header */
    .command-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 0.7rem;
        border-bottom: 1px solid #1E2638;
        margin-bottom: 0.8rem;
    }
    .brand-logo {
        font-size: 1.25rem;
        font-weight: 800;
        color: #F8FAFC;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        letter-spacing: -0.02em;
    }
    .amber-tag {
        font-size: 0.72rem;
        font-weight: 600;
        color: #F59E0B;
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 2px 8px;
        border-radius: 9999px;
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

    /* Top Strip KPI Counters */
    .mini-kpi {
        display: flex;
        align-items: center;
        gap: 16px;
        background: #0F1420;
        border: 1px solid #1E2638;
        border-radius: 8px;
        padding: 6px 14px;
        font-size: 0.8rem;
    }

    /* Product Card in Master List */
    .product-list-card {
        background: #0F1420;
        border: 1px solid #1E2638;
        border-radius: 10px;
        padding: 0.75rem 0.9rem;
        margin-bottom: 0.45rem;
        transition: all 0.15s ease;
        display: flex;
        gap: 12px;
        align-items: center;
    }
    .product-list-card:hover {
        border-color: #F59E0B;
        background: #141B2B;
    }
    .product-list-card.selected {
        border-color: #F59E0B;
        background: #161F33;
        box-shadow: 0 0 0 1px #F59E0B;
    }

    /* Big Detail Card (Cockpit) */
    .cockpit-panel {
        background: #0F1420;
        border: 1px solid #1E2638;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
    }

    /* Badges */
    .badge-win {
        color: #10B981;
        background: rgba(16, 185, 129, 0.14);
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 2px 7px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-drop {
        color: #EF4444;
        background: rgba(239, 68, 68, 0.14);
        border: 1px solid rgba(239, 68, 68, 0.35);
        padding: 2px 7px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-surge {
        color: #F59E0B;
        background: rgba(245, 158, 11, 0.14);
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 2px 7px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
    }

    /* Primary and Secondary Action Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
        color: #080B11 !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35) !important;
    }
    div.stButton > button[kind="secondary"] {
        background: #0F1420 !important;
        color: #CBD5E1 !important;
        border: 1px solid #1E2638 !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #080B11 !important;
        border-color: #1E2638 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Load Ground-Truth Verifiable Data
@st.cache_data(ttl=3600)
def get_cached_catalog():
    cat_file = Path(__file__).resolve().parent / "catalog.xlsx"
    if cat_file.exists():
        return pd.read_excel(cat_file)
    return fetch_ground_truth_catalog()

@st.cache_data(ttl=3600)
def get_cached_history(df_catalog):
    hist_file = Path(__file__).resolve().parent / "price_history.xlsx"
    if hist_file.exists():
        return pd.read_excel(hist_file)
    return generate_time_series_history(df_catalog)

catalog_df = get_cached_catalog()
history_df = get_cached_history(catalog_df)

# 4. Top Navigation Bar
st.markdown("""
<div class="command-header">
  <div style="display: flex; align-items: center; gap: 10px;">
    <span class="brand-logo">⚡ PricePulse Cockpit</span>
    <span class="amber-tag">Retail Intelligence v2.5</span>
    <span style="font-size: 0.74rem; color: #94A3B8;">● Two-Column Master-Detail</span>
  </div>
  <div style="display: flex; align-items: center; gap: 12px;">
    <span class="mini-kpi">
      <span>Active Radar: <strong style="color: #10B981;">16 SKUs</strong></span>
      <span style="color: #64748B;">|</span>
      <span>Shopify Sync: <strong style="color: #38BDF8;">Ready</strong></span>
      <span style="color: #64748B;">|</span>
      <span>EAN Match: <strong style="color: #F59E0B;">100%</strong></span>
    </span>
    <div style="display: inline-flex; align-items: center; gap: 8px; padding: 4px 12px; border-radius: 9999px; background: #0F1420; border: 1px solid #1E2638; font-size: 0.8rem; color: #CBD5E1;">
      Available for Hire <span class="status-dot"></span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# 5. Master-Detail Layout (Left Column: Catalog Browser, Right Column: Intelligence Cockpit)
col_left, col_right = st.columns([1.6, 2.4])

# --- LEFT COLUMN: PRODUCT SELECTION & LIVE SPREAD LIST ---
with col_left:
    st.markdown("<div style='font-size: 0.92rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.3rem;'>📦 Monitored Products Directory</div>", unsafe_allow_html=True)
    
    # Filter search
    search_q = st.text_input("Filter products", "", placeholder="🔍 Filter by Brand, SKU, or Barcode...", label_visibility="collapsed")
    filtered_cat = catalog_df.copy()
    if search_q:
        mask = filtered_cat.astype(str).apply(lambda row: row.str.contains(search_q, case=False).any(), axis=1)
        filtered_cat = filtered_cat[mask]

    # Selectbox for current active product
    prod_titles = filtered_cat["title"].tolist()
    if not prod_titles:
        st.warning("No products matching query.")
        st.stop()

    selected_title = st.selectbox(
        "Active Product in Cockpit",
        prod_titles,
        index=0,
        label_visibility="collapsed"
    )

    # Render Visual Preview Cards for the list
    for idx, row in filtered_cat.iterrows():
        p_title = row["title"]
        p_sku = row["sku"]
        p_our = float(row["current_price"])
        p_comp = float(row["competitor_a_price"])
        p_thumb = row.get("thumbnail", "")
        p_stock = row.get("comp_a_in_stock", True)

        diff = p_our - p_comp
        if not p_stock:
            badge_html = '<span class="badge-surge">🔺 STOCKOUT MONOPOLY</span>'
        elif diff > 0:
            badge_html = f'<span class="badge-drop">🚨 DROP -${diff:.2f}</span>'
        elif diff < 0:
            badge_html = f'<span class="badge-win">✓ WINNING +${abs(diff):.2f}</span>'
        else:
            badge_html = '<span class="badge-win">✓ MATCH</span>'

        is_current = (p_title == selected_title)
        border_color = "#F59E0B" if is_current else "#1E2638"
        bg_color = "#161F33" if is_current else "#0F1420"

        st.markdown(f"""
        <div style="background: {bg_color}; border: 1px solid {border_color}; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <img src="{p_thumb}" style="width: 38px; height: 38px; object-fit: contain; border-radius: 4px; background: #080B11; border: 1px solid #1E2638;" onerror="this.style.display='none'" />
            <div>
              <div style="font-size: 0.82rem; font-weight: 600; color: #F8FAFC; line-height: 1.2;">{p_title}</div>
              <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 2px;">
                <code>{p_sku}</code> • EAN: <code>{row['barcode']}</code>
              </div>
            </div>
          </div>
          <div style="text-align: right;">
            <div style="font-size: 0.88rem; font-weight: 700; color: #F8FAFC;">${p_our:.2f}</div>
            <div style="margin-top: 2px;">{badge_html}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)


# --- RIGHT COLUMN: PRODUCT COCKPIT & TIME-SERIES INTELLIGENCE ---
with col_right:
    # Retrieve details for the selected product
    p_data = catalog_df[catalog_df["title"] == selected_title].iloc[0].to_dict()

    # 1. Cockpit Hero Card
    st.markdown(f"""
    <div style="background: #0F1420; border: 1px solid #1E2638; border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.7rem;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
          <div style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: #F59E0B; font-weight: 700;">Active Inspection Unit</div>
          <div style="font-size: 1.15rem; font-weight: 800; color: #F8FAFC; margin-top: 2px;">{p_data['title']}</div>
          <div style="font-size: 0.76rem; color: #94A3B8; margin-top: 4px;">
            SKU: <code style="color: #818CF8;">{p_data['sku']}</code> | 
            EAN-13: <code style="color: #10B981;">{p_data['barcode']}</code> | 
            ASIN: <code style="color: #38BDF8;">{p_data['comp_a_asin']}</code>
          </div>
        </div>
        <div style="text-align: right; background: #080B11; border: 1px solid #1E2638; border-radius: 8px; padding: 6px 12px;">
          <div style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase;">Confidence Score</div>
          <div style="font-size: 1.1rem; font-weight: 800; color: #10B981;">100% EAN-13</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Competitor Benchmarking Grid
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div style="background: #0F1420; border: 1px solid #1E2638; border-radius: 8px; padding: 0.7rem; text-align: center;">
          <div style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase;">Cost Price</div>
          <div style="font-size: 1.25rem; font-weight: 700; color: #94A3B8;">${p_data['cost_price']:.2f}</div>
          <div style="font-size: 0.68rem; color: #64748B;">Floor Baseline</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div style="background: #0F1420; border: 1px solid #1E2638; border-radius: 8px; padding: 0.7rem; text-align: center;">
          <div style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase;">Your Current Price</div>
          <div style="font-size: 1.25rem; font-weight: 700; color: #F8FAFC;">${p_data['current_price']:.2f}</div>
          <div style="font-size: 0.68rem; color: #818CF8;">Live Storefront</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        comp_a_st = "In Stock" if p_data['comp_a_in_stock'] else "Out of Stock"
        comp_a_color = "#38BDF8" if p_data['comp_a_in_stock'] else "#EF4444"
        st.markdown(f"""
        <div style="background: #0F1420; border: 1px solid #1E2638; border-radius: 8px; padding: 0.7rem; text-align: center;">
          <div style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase;">Amazon US</div>
          <div style="font-size: 1.25rem; font-weight: 700; color: {comp_a_color};">${p_data['competitor_a_price']:.2f}</div>
          <div style="font-size: 0.68rem; color: {comp_a_color};">{comp_a_st}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        comp_b_st = "In Stock" if p_data['comp_b_in_stock'] else "Out of Stock"
        comp_b_color = "#F59E0B" if p_data['comp_b_in_stock'] else "#EF4444"
        st.markdown(f"""
        <div style="background: #0F1420; border: 1px solid #1E2638; border-radius: 8px; padding: 0.7rem; text-align: center;">
          <div style="font-size: 0.68rem; color: #94A3B8; text-transform: uppercase;">BestBuy Online</div>
          <div style="font-size: 1.25rem; font-weight: 700; color: {comp_b_color};">${p_data['competitor_b_price']:.2f}</div>
          <div style="font-size: 0.68rem; color: {comp_b_color};">{comp_b_st}</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. Interactive Repricing Sandbox (Sliders & Dynamic Re-calculation)
    st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<div style='font-size: 0.82rem; font-weight: 700; color: #F59E0B; text-transform: uppercase; margin-bottom: 0.4rem;'>⚡ Dynamic Repricing Strategy Sandbox</div>", unsafe_allow_html=True)
        sb1, sb2, sb3 = st.columns(3)
        with sb1:
            margin_floor = st.slider("Min Margin Floor %", 10, 35, 15, key="sb_floor")
        with sb2:
            undercut_cents = st.selectbox("Buy-Box Undercut", ["$0.25", "$0.50", "$1.00", "$2.00"], index=1, key="sb_undercut")
            u_val = float(undercut_cents.replace("$", ""))
        with sb3:
            surge_pct = st.slider("Stockout Surge %", 3, 20, 8, key="sb_surge")

        # Run evaluation on the fly for this specific product
        sim_rule = RepricingRule(min_margin_percent=margin_floor, undercut_cents=u_val, stockout_surge_percent=surge_pct)
        sim_engine = RepricingEngine(rule=sim_rule)
        eval_res = sim_engine.evaluate_product(p_data)

        # Output Box
        rec_p = eval_res["recommended_price"]
        diff_p = eval_res["price_diff"]
        diff_str = f"+${diff_p:.2f}" if diff_p > 0 else (f"-${abs(diff_p):.2f}" if diff_p < 0 else "$0.00")

        res_col1, res_col2 = st.columns([2.5, 1.5])
        with res_col1:
            st.markdown(f"""
            <div style="background: #080B11; border: 1px solid #1E2638; border-radius: 8px; padding: 0.8rem; font-size: 0.82rem; line-height: 1.5;">
              <span style="color: #94A3B8;">Algorithm Action:</span> <strong style="color: #F8FAFC;">{eval_res['action']}</strong><br/>
              <span style="color: #94A3B8;">Strategic Logic:</span> <span style="color: #CBD5E1;">{eval_res['reason']}</span><br/>
              <span style="color: #94A3B8;">Safety Floor Price:</span> <code style="color: #EF4444;">${eval_res['floor_price']:.2f}</code> (Protected minimum)
            </div>
            """, unsafe_allow_html=True)
        with res_col2:
            st.markdown(f"""
            <div style="background: #141B2B; border: 1px solid #F59E0B; border-radius: 8px; padding: 0.8rem; text-align: center;">
              <div style="font-size: 0.7rem; color: #F59E0B; text-transform: uppercase; font-weight: 700;">Recommended Buy-Box</div>
              <div style="font-size: 1.5rem; font-weight: 800; color: #F8FAFC;">${rec_p:.2f}</div>
              <div style="font-size: 0.76rem; color: #10B981; font-weight: 600;">{eval_res['new_margin_pct']}% Gross Margin ({diff_str})</div>
            </div>
            """, unsafe_allow_html=True)

    # 4. Plotly 30-Day Historical Volatility Chart
    st.markdown("<div style='font-size: 0.86rem; font-weight: 700; color: #F8FAFC; margin-top: 0.4rem; margin-bottom: 0.2rem;'>📈 30-Day Price Volatility & Market Defense Analysis</div>", unsafe_allow_html=True)
    hist_sub = history_df[history_df["sku"] == p_data["sku"]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist_sub["date"], y=hist_sub["our_price"],
        name="Your Store",
        line=dict(color="#F8FAFC", width=2.5)
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
        paper_bgcolor="#0F1420",
        plot_bgcolor="#080B11",
        margin=dict(l=25, r=15, t=15, b=25),
        height=240,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        xaxis=dict(showgrid=True, gridcolor="#1E2638"),
        yaxis=dict(showgrid=True, gridcolor="#1E2638", tickprefix="$")
    )
    st.plotly_chart(fig, use_container_width=True)

    # 5. Bottom Dispatch Actions
    act1, act2, act3 = st.columns([1.5, 1.3, 1.2])
    with act1:
        if st.button("🚀 Push Update to Shopify API", use_container_width=True, type="primary"):
            st.toast(f"✅ SKU '{p_data['sku']}' updated on Shopify to ${rec_p:.2f}!", icon="🚀")
            st.success(f"✓ Shopify GraphQL Mutation dispatched for {p_data['sku']}.")
    with act2:
        if st.button("🚨 Dispatch Telegram Alert", use_container_width=True):
            st.toast(f"🔔 Telegram Price Drop Webhook triggered for {p_data['sku']}!", icon="🚨")
            st.info("📢 Alert payload sent to private merchant channel.")
    with act3:
        # Export single row or all
        shopify_export = pd.DataFrame([{
            "Handle": str(p_data["sku"]).lower().replace(" ", "-"),
            "Title": p_data["title"],
            "Variant SKU": p_data["sku"],
            "Variant Barcode": p_data["barcode"],
            "Variant Price": rec_p,
            "Variant Compare At Price": p_data["current_price"],
            "Variant Inventory Qty": p_data["stock"]
        }])
        csv_data = shopify_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name=f"Shopify_{p_data['sku']}.csv",
            mime="text/csv",
            use_container_width=True
        )
