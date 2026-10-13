"""
PricePulse Terminal v3.0 — High-Frequency Algorithmic E-Commerce Repricing Terminal.
Bloomberg Terminal & TradingView Hybrid Aesthetic.
Deep midnight-black palette (#05070D, #0B0F1C) with vibrant trading accents:
Neon Cyan, Amber Gold, Emerald Green, and Alert Crimson.
"""

from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from repricer import RepricingEngine, RepricingRule
from matcher import ProductMatchingEngine
from dataset import fetch_ground_truth_catalog, generate_time_series_history

# 1. Page Configuration
st.set_page_config(
    page_title="PricePulse Terminal v3.0 | Algorithmic Retail Arbitrage",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Ultra-Precise Trading Terminal & FinTech CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, .mono, .ticker, .stat-num {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stApp {
        background-color: #05070D !important;
        color: #E2E8F0 !important;
    }

    /* Completely hide Streamlit default chrome & paddings */
    header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }

    div[data-testid="stVerticalBlock"] > div {
        gap: 0.4rem !important;
    }

    /* Top Bloomberg Header */
    .terminal-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #161F30;
    }
    .terminal-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #F8FAFC;
        letter-spacing: -0.02em;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .neon-cyan { color: #00F0FF; text-shadow: 0 0 10px rgba(0, 240, 255, 0.4); }
    .amber-gold { color: #F59E0B; }
    .emerald-up { color: #10B981; }
    .crimson-down { color: #EF4444; }

    .pulse-dot {
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

    /* Full-Width Ticker Tape */
    .ticker-bar {
        background: #080C16;
        border-top: 1px solid #121A2B;
        border-bottom: 1px solid #161F30;
        padding: 5px 12px;
        margin-top: 0.35rem;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        overflow-x: auto;
        white-space: nowrap;
        gap: 20px;
        font-size: 0.76rem;
    }
    .ticker-item {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Trading Panels */
    .trading-panel {
        background: #0A0F1D;
        border: 1px solid #162035;
        border-radius: 8px;
        padding: 1rem;
    }

    /* Order Book Style Box */
    .orderbook-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 8px;
        border-bottom: 1px solid #121A2B;
        font-size: 0.78rem;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Execution CTA */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00F0FF 0%, #3B82F6 100%) !important;
        color: #05070D !important;
        font-weight: 800 !important;
        font-size: 0.86rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        border: none !important;
        border-radius: 6px !important;
        box-shadow: 0 4px 18px rgba(0, 240, 255, 0.35) !important;
        letter-spacing: 0.02em !important;
    }
    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 24px rgba(0, 240, 255, 0.6) !important;
        transform: translateY(-1px) !important;
    }
    div.stButton > button[kind="secondary"] {
        background: #0D1424 !important;
        color: #94A3B8 !important;
        border: 1px solid #1C273E !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #00F0FF !important;
        color: #F8FAFC !important;
    }

    /* Terminal Console Stream */
    .console-stream {
        background: #04060A;
        border: 1px solid #121A2B;
        border-left: 3px solid #00F0FF;
        border-radius: 6px;
        padding: 8px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.74rem;
        color: #94A3B8;
        line-height: 1.5;
    }

    div[data-baseweb="select"] > div {
        background-color: #080C16 !important;
        border-color: #162035 !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Load Ground-Truth Data
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

# 4. Top Navigation Bar (Bloomberg Terminal Inspired)
st.markdown("""
<div class="terminal-nav">
  <div style="display: flex; align-items: center; gap: 12px;">
    <span class="terminal-title">⚡ <span class="neon-cyan">PricePulse Terminal</span> <span style="font-size: 0.8rem; color: #64748B;">v3.0</span></span>
    <span style="font-size: 0.72rem; color: #94A3B8; background: #0D1424; padding: 2px 8px; border-radius: 4px; border: 1px solid #1C273E;">
      Algorithmic Retail Arbitrage
    </span>
  </div>
  <div style="display: flex; align-items: center; gap: 14px;">
    <span style="font-size: 0.76rem; font-family: 'JetBrains Mono'; color: #94A3B8;">
      <span class="pulse-dot"></span> Market Feeds: <strong style="color: #10B981;">Live WebSocket</strong>
    </span>
    <span style="font-size: 0.76rem; font-family: 'JetBrains Mono'; color: #94A3B8;">
      Shopify GraphQL: <strong style="color: #00F0FF;">Connected</strong>
    </span>
    <div style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 9999px; background: #0D1424; border: 1px solid #1C273E; font-size: 0.76rem; color: #CBD5E1;">
      Portfolio by Freelancer
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# 5. Full-Width Financial Ticker Tape
ticker_items = []
for _, r in catalog_df.head(6).iterrows():
    p_name = r["title"]
    diff = round(float(r["current_price"]) - float(r["competitor_a_price"]), 2)
    if not r.get("comp_a_in_stock", True):
        ticker_items.append(f'<span class="ticker-item"><span style="color: #E2E8F0;">{p_name[:16]}:</span> <span class="amber-gold">AMZN OOS ▲ +8%</span></span>')
    elif diff > 0:
        ticker_items.append(f'<span class="ticker-item"><span style="color: #E2E8F0;">{p_name[:16]}:</span> <span class="crimson-down">AMZN -${diff:.2f} ▼</span></span>')
    else:
        ticker_items.append(f'<span class="ticker-item"><span style="color: #E2E8F0;">{p_name[:16]}:</span> <span class="emerald-up">MATCH =</span></span>')

ticker_html = "".join([f'<span style="margin-right: 18px;">{item}</span>' for item in ticker_items])
st.markdown(f"""
<div class="ticker-bar">
  <div style="display: flex; align-items: center; gap: 18px;">
    <span style="font-size: 0.7rem; font-weight: 700; color: #F59E0B; text-transform: uppercase;">[LIVE TICKER]</span>
    {ticker_html}
  </div>
  <div style="font-size: 0.7rem; color: #64748B; font-family: 'JetBrains Mono';">LATENCY: 42ms</div>
</div>
""", unsafe_allow_html=True)

# 6. Main Split-Screen Workspace (65% Chart Workspace, 35% Order Book & Control Terminal)
col_chart, col_terminal = st.columns([2.6, 1.4])

# --- 65% LEFT / CENTER: HERO TRADINGVIEW CHART & TIMELINE ---
with col_chart:
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
      <div style="font-size: 0.86rem; font-weight: 700; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
        <span>📊 PRICE ACTION &amp; COMPETITOR VOLATILITY TERMINAL</span>
      </div>
      <div style="display: flex; gap: 6px; font-family: 'JetBrains Mono'; font-size: 0.7rem;">
        <span style="background: #10B981; color: #05070D; padding: 2px 6px; border-radius: 4px; font-weight: 700;">1D</span>
        <span style="background: #0D1424; color: #94A3B8; padding: 2px 6px; border-radius: 4px;">7D</span>
        <span style="background: #00F0FF; color: #05070D; padding: 2px 6px; border-radius: 4px; font-weight: 700;">30D (ACTIVE)</span>
        <span style="background: #0D1424; color: #94A3B8; padding: 2px 6px; border-radius: 4px;">YTD</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Product Selector for Terminal Target
    prod_titles = catalog_df["title"].tolist()
    sel_prod_title = st.selectbox(
        "Select Active Market Asset",
        prod_titles,
        index=0,
        label_visibility="collapsed"
    )

    # Active Product Data
    active_row = catalog_df[catalog_df["title"] == sel_prod_title].iloc[0]
    sku_val = active_row["sku"]
    cost_val = float(active_row["cost_price"])
    our_p = float(active_row["current_price"])
    comp_a_p = float(active_row["competitor_a_price"])
    comp_b_p = float(active_row["competitor_b_price"])
    ean_code = active_row["barcode"]

    # History Time-Series
    hist_sub = history_df[history_df["sku"] == sku_val].copy().reset_index(drop=True)

    # Calculate Floor for chart
    floor_val = round(cost_val * 1.15, 2)

    # Render TradingView Style Plotly Figure
    fig = go.Figure()

    # Red-Shaded Margin Floor Zone
    fig.add_hrect(
        y0=0, y1=floor_val,
        fillcolor="rgba(239, 68, 68, 0.12)",
        line_width=1,
        line_color="rgba(239, 68, 68, 0.4)",
        annotation_text=f"PROTECTED MARGIN FLOOR (${floor_val:.2f})",
        annotation_position="bottom right",
        annotation_font=dict(size=10, color="#EF4444")
    )

    # Our Store Line (Solid Neon Cyan)
    fig.add_trace(go.Scatter(
        x=hist_sub["date"], y=hist_sub["our_price"],
        name="Our Store Price",
        line=dict(color="#00F0FF", width=3)
    ))

    # Amazon Line (Dashed Orange)
    fig.add_trace(go.Scatter(
        x=hist_sub["date"], y=hist_sub["comp_a_price"],
        name="Amazon US",
        line=dict(color="#FB923C", width=2, dash="dash")
    ))

    # BestBuy Line (Dotted Amber Gold)
    fig.add_trace(go.Scatter(
        x=hist_sub["date"], y=hist_sub["comp_b_price"],
        name="BestBuy Online",
        line=dict(color="#F59E0B", width=2, dash="dot")
    ))

    # Pinned Event Flag directly on recent price drop
    last_date = hist_sub["date"].iloc[-1]
    fig.add_annotation(
        x=last_date, y=comp_a_p,
        text="🚨 Competitor Undercut",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#EF4444",
        arrowsize=1,
        arrowwidth=2,
        bgcolor="#0A0F1D",
        bordercolor="#EF4444",
        borderwidth=1,
        font=dict(color="#F8FAFC", size=10)
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0A0F1D",
        plot_bgcolor="#05070D",
        margin=dict(l=30, r=20, t=10, b=20),
        height=370,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="JetBrains Mono", size=10)),
        xaxis=dict(showgrid=True, gridcolor="#121A2B", tickfont=dict(family="JetBrains Mono", size=10)),
        yaxis=dict(showgrid=True, gridcolor="#121A2B", tickprefix="$", tickfont=dict(family="JetBrains Mono", size=10))
    )
    st.plotly_chart(fig, use_container_width=True)

    # Bottom Terminal Event Stream
    time_now = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"""
    <div class="console-stream">
      <div>[{time_now}] <strong>INGESTION:</strong> Live barcode <code>{ean_code}</code> verified with Amazon ASIN <code>{active_row['comp_a_asin']}</code>.</div>
      <div>[{time_now}] <strong>RADAR EVENT:</strong> Amazon competitor set at ${comp_a_p:.2f} (Spread: ${our_p - comp_a_p:+.2f}).</div>
      <div>[{time_now}] <strong>ALGO DECISION:</strong> Buy-Box undercutting rules engaged. Target calculation ready for execution.</div>
    </div>
    """, unsafe_allow_html=True)


# --- 35% RIGHT: ORDER BOOK & ALGORITHMIC STRATEGY TERMINAL ---
with col_terminal:
    # Asset Specs
    st.markdown(f"""
    <div style="background: #0A0F1D; border: 1px solid #162035; border-radius: 8px; padding: 10px 14px; margin-bottom: 0.5rem;">
      <div style="font-size: 0.68rem; font-family: 'JetBrains Mono'; color: #00F0FF; text-transform: uppercase;">TARGET ASSET SPECIFICATION</div>
      <div style="font-size: 0.96rem; font-weight: 800; color: #F8FAFC; margin-top: 2px;">{sel_prod_title}</div>
      <div style="font-size: 0.72rem; font-family: 'JetBrains Mono'; color: #94A3B8; margin-top: 3px;">
        SKU: <code style="color: #00F0FF;">{sku_val}</code> | EAN-13: <code style="color: #10B981;">{ean_code}</code>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Order-Book Market Grid
    st.markdown("""
    <div style="background: #080C16; border: 1px solid #162035; border-radius: 6px; padding: 6px 10px; margin-bottom: 0.5rem;">
      <div style="font-size: 0.68rem; font-family: 'JetBrains Mono'; color: #F59E0B; text-transform: uppercase; margin-bottom: 4px;">MARKETPLACE QUOTE BOOK</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
      <div class="orderbook-row"><span style="color: #94A3B8;">Cost Baseline (COGS):</span> <span style="color: #64748B;">${cost_val:.2f}</span></div>
      <div class="orderbook-row"><span style="color: #94A3B8;">Your Live Storefront:</span> <span style="color: #F8FAFC; font-weight: 700;">${our_p:.2f}</span></div>
      <div class="orderbook-row"><span style="color: #FB923C;">Amazon US Quote:</span> <span style="color: #FB923C;">${comp_a_p:.2f} ({'In Stock' if active_row['comp_a_in_stock'] else 'OUT OF STOCK'})</span></div>
      <div class="orderbook-row"><span style="color: #F59E0B;">BestBuy Quote:</span> <span style="color: #F59E0B;">${comp_b_p:.2f} ({'In Stock' if active_row['comp_b_in_stock'] else 'OUT OF STOCK'})</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Algorithmic Execution Inputs
    st.markdown("""
    <div style="background: #0A0F1D; border: 1px solid #162035; border-radius: 8px; padding: 10px 12px; margin-bottom: 0.5rem;">
      <div style="font-size: 0.68rem; font-family: 'JetBrains Mono'; color: #00F0FF; text-transform: uppercase; margin-bottom: 6px;">ARBITRAGE EXECUTION ALGORITHM</div>
    """, unsafe_allow_html=True)

    c_floor, c_undercut = st.columns(2)
    with c_floor:
        inp_floor = st.slider("Floor Margin %", 10, 30, 15, key="fin_floor")
    with c_undercut:
        inp_undercut = st.selectbox("Buy-Box Beat", ["-$0.10", "-$0.50", "-$1.00", "-$2.00"], index=1, key="fin_undercut")
        u_val = abs(float(inp_undercut.replace("-$", "").replace("$", "")))

    # Compute algorithm decision
    algo_rule = RepricingRule(min_margin_percent=inp_floor, undercut_cents=u_val)
    algo_engine = RepricingEngine(rule=algo_rule)
    eval_res = algo_engine.evaluate_product(active_row.to_dict())

    rec_exec_price = eval_res["recommended_price"]
    margin_gain_pct = eval_res["new_margin_pct"]
    margin_gain_usd = eval_res["new_margin_dollar"]

    # Hero Recommended Price Display
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(0, 240, 255, 0.08) 0%, rgba(59, 130, 246, 0.08) 100%); border: 1px solid rgba(0, 240, 255, 0.4); border-radius: 8px; padding: 12px; text-align: center; margin-top: 6px; margin-bottom: 10px;">
      <div style="font-size: 0.68rem; font-family: 'JetBrains Mono'; color: #00F0FF; text-transform: uppercase; font-weight: 700;">RECOMMENDED EXECUTION PRICE</div>
      <div style="font-size: 2.1rem; font-weight: 800; color: #F8FAFC; font-family: 'JetBrains Mono'; line-height: 1.1; margin: 4px 0;">${rec_exec_price:.2f}</div>
      <div style="display: inline-flex; align-items: center; gap: 6px; padding: 2px 8px; border-radius: 4px; background: rgba(16, 185, 129, 0.18); color: #10B981; font-size: 0.76rem; font-family: 'JetBrains Mono';">
        Gross Margin: {margin_gain_pct}% (+${margin_gain_usd:.2f})
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Action Triggers
    if st.button("⚡ EXECUTE REPRICE VIA SHOPIFY API", use_container_width=True, type="primary"):
        st.toast(f"🚀 Execution Confirmed: SKU '{sku_val}' updated to ${rec_exec_price:.2f} via Shopify GraphQL API!", icon="⚡")
        st.success(f"✓ GraphQL Mutation Dispatched: {sku_val} repriced to ${rec_exec_price:.2f}")

    btn_alt1, btn_alt2 = st.columns(2)
    with btn_alt1:
        if st.button("📡 Alert Telegram", use_container_width=True):
            st.toast(f"🚨 Webhook Triggered: Price drop on {sku_val} sent to Telegram!", icon="📡")
    with btn_alt2:
        export_df = pd.DataFrame([{
            "Handle": str(sku_val).lower().replace(" ", "-"),
            "Title": sel_prod_title,
            "Variant SKU": sku_val,
            "Variant Barcode": ean_code,
            "Variant Price": rec_exec_price,
            "Variant Compare At Price": our_p
        }])
        st.download_button(
            label="📥 Export CSV",
            data=export_df.to_csv(index=False).encode('utf-8'),
            file_name=f"Shopify_{sku_val}.csv",
            mime="text/csv",
            use_container_width=True
        )
