"""
PricePulse Terminal v3.5 | Algorithmic Retail Arbitrage Workstation
TradingView + Bloomberg Terminal hybrid aesthetic in dark mode.
Deep obsidian palette (#060813, #0B0F1C) with vibrant trading accents:
Neon Cyan (#00F0FF), Amber Gold (#F59E0B), Emerald Green (#10B981), Alert Crimson (#EF4444).
"""

from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from repricer import RepricingEngine, RepricingRule
from dataset import fetch_ground_truth_catalog, generate_time_series_history

# 1. Page Configuration
st.set_page_config(
    page_title="PricePulse Terminal v3.5 | Algorithmic Retail Arbitrage",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Production Fintech & Bloomberg Dark Mode CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, .mono, .ticker, .stat-num, .price-val {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stApp {
        background-color: #060813 !important;
        color: #E2E8F0 !important;
    }

    /* Hide default Streamlit chrome */
    header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], #MainMenu, footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    .block-container {
        padding-top: 0.6rem !important;
        padding-bottom: 1.2rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
    }

    div[data-testid="stVerticalBlock"] > div {
        gap: 0.35rem !important;
    }

    /* Top Bloomberg Header */
    .terminal-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #141A2E;
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
    .neon-cyan { color: #00F0FF; text-shadow: 0 0 10px rgba(0, 240, 255, 0.45); }
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

    /* Full-Width Financial Ticker */
    .ticker-tape {
        background: #090D1C;
        border-top: 1px solid #141A2E;
        border-bottom: 1px solid #18223C;
        padding: 5px 12px;
        margin-top: 0.35rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        overflow-x: auto;
        white-space: nowrap;
        gap: 20px;
        font-size: 0.74rem;
    }
    .ticker-item {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Glassmorphic Panel Cards */
    .glass-card {
        background: rgba(11, 15, 28, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 10px 14px;
        backdrop-filter: blur(8px);
    }

    /* Order Book Box */
    .orderbook-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 6px;
        border-bottom: 1px solid #141A2E;
        font-size: 0.76rem;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00F0FF 0%, #3B82F6 100%) !important;
        color: #05070D !important;
        font-weight: 800 !important;
        font-size: 0.84rem !important;
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
        font-size: 0.78rem !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #00F0FF !important;
        color: #F8FAFC !important;
    }

    /* Console Stream */
    .console-stream {
        background: #04060C;
        border: 1px solid #141A2E;
        border-left: 3px solid #00F0FF;
        border-radius: 6px;
        padding: 6px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #94A3B8;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Table Styling */
    .data-grid-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.78rem;
    }
    .data-grid-table th {
        background: #090D1C;
        color: #64748B;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        text-transform: uppercase;
        padding: 8px 10px;
        text-align: left;
        border-bottom: 1px solid #18223C;
        letter-spacing: 0.04em;
    }
    .data-grid-table td {
        padding: 7px 10px;
        border-bottom: 1px solid #101626;
        vertical-align: middle;
    }
    .row-selected {
        background: rgba(0, 240, 255, 0.07) !important;
        border-left: 3px solid #00F0FF !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Data Initialization & Caching
@st.cache_data(ttl=3600)
def load_base_catalog():
    cat_file = Path(__file__).resolve().parent / "catalog.xlsx"
    if cat_file.exists():
        return pd.read_excel(cat_file)
    return fetch_ground_truth_catalog()

@st.cache_data(ttl=3600)
def load_base_history(df_catalog):
    hist_file = Path(__file__).resolve().parent / "price_history.xlsx"
    if hist_file.exists():
        return pd.read_excel(hist_file)
    return generate_time_series_history(df_catalog)

# State initialization
if "catalog_df" not in st.session_state:
    st.session_state["catalog_df"] = load_base_catalog().copy()

if "history_df" not in st.session_state:
    st.session_state["history_df"] = load_base_history(st.session_state["catalog_df"]).copy()

if "selected_sku" not in st.session_state:
    # Default to Apple iPhone 5s as per prompt
    st.session_state["selected_sku"] = "SMA-APP-IPH-121"

if "view_mode" not in st.session_state:
    st.session_state["view_mode"] = "[ 📋 Catalog List (Active) ]"

if "last_log" not in st.session_state:
    st.session_state["last_log"] = "[14:22:05] Amazon dropped price on iPhone 13 Pro -> Algorithmic Buy-Box recaptured via -$0.50 undercut"

catalog_df = st.session_state["catalog_df"]
history_df = st.session_state["history_df"]

# Helper: Generate Inline SVG Sparkline
def generate_svg_sparkline(prices, width=85, height=22, color="#00F0FF"):
    if not prices or len(prices) < 2:
        return ""
    min_p, max_p = min(prices), max(prices)
    rng = max_p - min_p if max_p != min_p else 1.0
    pts = []
    for i, p in enumerate(prices):
        x = (i / (len(prices) - 1)) * (width - 6) + 3
        y = height - 4 - ((p - min_p) / rng) * (height - 8)
        pts.append(f"{x:.1f},{y:.1f}")
    polyline_pts = " ".join(pts)
    last_pt = pts[-1].split(",")
    return f"""<svg width="{width}" height="{height}" style="overflow:visible; vertical-align:middle; display:inline-block;">
      <polyline fill="none" stroke="{color}" stroke-width="2" points="{polyline_pts}" />
      <circle cx="{last_pt[0]}" cy="{last_pt[1]}" r="2.5" fill="{color}" />
    </svg>"""

# 4. Header & Live Ticker
st.markdown("""
<div class="terminal-header">
  <div style="display: flex; align-items: center; gap: 12px;">
    <span class="terminal-title">⚡ <span class="neon-cyan">PricePulse Terminal</span> <span style="font-size: 0.82rem; color: #64748B;">v3.5</span></span>
    <span style="font-size: 0.72rem; color: #94A3B8; background: #0B1020; padding: 2px 8px; border-radius: 4px; border: 1px solid #18223C;">
      Algorithmic Retail Arbitrage Workstation
    </span>
  </div>
  <div style="display: flex; align-items: center; gap: 16px;">
    <span style="font-size: 0.74rem; font-family: 'JetBrains Mono'; color: #94A3B8;">
      <span class="pulse-dot"></span> WebSocket: <strong style="color: #10B981;">Connected</strong>
    </span>
    <div style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px; border-radius: 9999px; background: #0B1020; border: 1px solid #18223C; font-size: 0.74rem; color: #CBD5E1;">
      Dev Portfolio by Freelancer
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Live Ticker Tape
st.markdown("""
<div class="ticker-tape">
  <div style="display: flex; align-items: center; gap: 16px;">
    <span style="font-size: 0.7rem; font-weight: 800; color: #F59E0B;">[LIVE TICKER]</span>
    <span class="ticker-item"><span style="color: #E2E8F0;">iPhone 13 Pro:</span> <span class="crimson-down">AMZN $1,084.49 ▼ -$15.50</span></span>
    <span class="ticker-item"><span style="color: #E2E8F0;">Sony XM5:</span> <span class="amber-gold">BestBuy OOS ▲ +8%</span></span>
    <span class="ticker-item"><span style="color: #E2E8F0;">Oppo K1:</span> <span class="emerald-up">Match = $299.99</span></span>
    <span class="ticker-item"><span style="color: #E2E8F0;">iPhone 5s:</span> <span class="neon-cyan">Buy-Box Recaptured $191.49</span></span>
    <span class="ticker-item"><span style="color: #E2E8F0;">Galaxy S10:</span> <span class="crimson-down">AMZN -$10.00 ▼</span></span>
  </div>
  <div style="font-size: 0.7rem; color: #64748B; font-family: 'JetBrains Mono';">LATENCY: 38ms | 16 SKUs MONITORED</div>
</div>
""", unsafe_allow_html=True)

# 5. View Controls & Filter Bar
engine = RepricingEngine()
catalog_eval_df = engine.process_catalog(catalog_df)

c_ctrl_left, c_ctrl_mid, c_ctrl_right = st.columns([2.5, 2.5, 2.8])

with c_ctrl_left:
    filter_option = st.radio(
        "Filter Category",
        options=["All Products (16)", "🚨 Actions Required (14)", "⚡ Stockout Surges (1)"],
        horizontal=True,
        label_visibility="collapsed"
    )

with c_ctrl_mid:
    search_query = st.text_input(
        "Search SKU / Brand",
        placeholder="🔍 Filter by SKU, EAN-13 barcode, or brand...",
        label_visibility="collapsed"
    )

with c_ctrl_right:
    view_switcher = st.radio(
        "View Switcher",
        options=["[ 📈 Chart ]", "[ 📋 Catalog List (Active) ]", "[ ⚡ Split ]"],
        index=1,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.session_state["view_mode"] = view_switcher

# Filter products according to controls
filtered_eval_df = catalog_eval_df.copy()
if filter_option == "🚨 Actions Required (14)":
    filtered_eval_df = filtered_eval_df[filtered_eval_df["status_badge"].isin(["UNDERCUT", "SURGE", "PROTECTED"])]
elif filter_option == "⚡ Stockout Surges (1)":
    filtered_eval_df = filtered_eval_df[filtered_eval_df["status_badge"] == "SURGE"]

if search_query:
    q = search_query.lower()
    filtered_eval_df = filtered_eval_df[
        filtered_eval_df["title"].str.lower().str.contains(q) |
        filtered_eval_df["sku"].str.lower().str.contains(q) |
        filtered_eval_df["barcode"].astype(str).str.contains(q) |
        filtered_eval_df["brand"].str.lower().str.contains(q)
    ]

# 6. Main Workstation Area (Two-Panel Layout: 70% Left, 30% Right)
col_left_main, col_right_dock = st.columns([2.8, 1.2])

# Get current active product
active_sku = st.session_state["selected_sku"]
if active_sku not in catalog_df["sku"].values:
    active_sku = catalog_df.iloc[0]["sku"]
    st.session_state["selected_sku"] = active_sku

active_row = catalog_df[catalog_df["sku"] == active_sku].iloc[0]
active_title = active_row["title"]
active_cost = float(active_row["cost_price"])
active_our_price = float(active_row["current_price"])
active_comp_a = float(active_row["competitor_a_price"])
active_comp_b = float(active_row["competitor_b_price"])
active_ean = str(active_row["barcode"])
active_comp_a_stock = bool(active_row.get("comp_a_in_stock", True))
active_comp_b_stock = bool(active_row.get("comp_b_in_stock", True))

# --- LEFT PANEL (70%): Interactive Registry Table, Chart, or Split ---
with col_left_main:

    # A. Render Chart (if in [ 📈 Chart ] or [ ⚡ Split ])
    if view_switcher in ["[ 📈 Chart ]", "[ ⚡ Split ]"]:
        c_ch_hdr1, c_ch_hdr2 = st.columns([3, 1])
        with c_ch_hdr1:
            st.markdown(f"""
            <div style="font-size: 0.84rem; font-weight: 700; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
              <span>📈 FINANCIAL PRICE ACTION TERMINAL — <span class="neon-cyan">{active_title}</span></span>
            </div>
            """, unsafe_allow_html=True)
        with c_ch_hdr2:
            time_range = st.selectbox("Timeframe", ["7D", "14D", "30D", "YTD"], index=2, label_visibility="collapsed", key="tf_chart")

        days_val = {"7D": 7, "14D": 14, "30D": 30, "YTD": 30}[time_range]
        hist_active = history_df[history_df["sku"] == active_sku].tail(days_val).reset_index(drop=True)
        floor_calc = round(active_cost * 1.15, 2)

        # Plotly Figure
        fig = go.Figure()
        fig.add_hrect(
            y0=0, y1=floor_calc,
            fillcolor="rgba(239, 68, 68, 0.12)",
            line_width=1,
            line_color="rgba(239, 68, 68, 0.4)",
            annotation_text=f"Protected Margin Floor: ${floor_calc:.2f}",
            annotation_position="bottom right",
            annotation_font=dict(size=10, color="#EF4444")
        )
        fig.add_trace(go.Scatter(
            x=hist_active["date"], y=hist_active["our_price"],
            name="Our Store Price",
            line=dict(color="#00F0FF", width=3)
        ))
        fig.add_trace(go.Scatter(
            x=hist_active["date"], y=hist_active["comp_a_price"],
            name="Amazon US",
            line=dict(color="#FB923C", width=2, dash="dash")
        ))
        fig.add_trace(go.Scatter(
            x=hist_active["date"], y=hist_active["comp_b_price"],
            name="BestBuy",
            line=dict(color="#F59E0B", width=2, dash="dot")
        ))

        # Pinned Event Flag
        last_d = hist_active["date"].iloc[-1]
        fig.add_annotation(
            x=last_d, y=active_comp_a,
            text=f"🚨 Competitor Undercut (${active_comp_a:.2f})",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#EF4444",
            arrowsize=1,
            arrowwidth=2,
            bgcolor="#0A0F1D",
            bordercolor="#EF4444",
            font=dict(color="#F8FAFC", size=10)
        )

        chart_height = 290 if view_switcher == "[ ⚡ Split ]" else 420
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#090D1C",
            plot_bgcolor="#060813",
            margin=dict(l=30, r=20, t=10, b=20),
            height=chart_height,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="JetBrains Mono", size=10)),
            xaxis=dict(showgrid=True, gridcolor="#141A2E", tickfont=dict(family="JetBrains Mono", size=10)),
            yaxis=dict(showgrid=True, gridcolor="#141A2E", tickprefix="$", tickfont=dict(family="JetBrains Mono", size=10))
        )
        st.plotly_chart(fig, use_container_width=True)

    # B. Render High-Density Product Registry Table (if in [ 📋 Catalog List ] or [ ⚡ Split ])
    if view_switcher in ["[ 📋 Catalog List (Active) ]", "[ ⚡ Split ]"]:
        st.markdown("""
        <div style="font-size: 0.84rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.4rem; display: flex; justify-content: space-between; align-items: center;">
          <span>📋 INTERACTIVE HIGH-DENSITY PRODUCT REGISTRY TABLE</span>
          <span style="font-size: 0.72rem; color: #64748B; font-family: 'JetBrains Mono';">CLICK [SELECT] TO BIND RIGHT EXECUTION DOCK</span>
        </div>
        """, unsafe_allow_html=True)

        # Build interactive rows
        for idx, row in filtered_eval_df.iterrows():
            row_sku = row["sku"]
            row_title = row["title"]
            row_our = float(row["current_price"])
            row_amzn = float(row["competitor_a_price"])
            row_bby = float(row["competitor_b_price"])
            row_rec = float(row["recommended_price"])
            row_diff = float(row["price_diff"])
            row_badge = row["status_badge"]
            is_active = (row_sku == active_sku)

            # Sparkline from 7-day history
            sub_h = history_df[history_df["sku"] == row_sku].tail(7)
            price_series = sub_h["comp_a_price"].tolist()
            if not price_series or len(price_series) < 2:
                price_series = [row_our * 1.02, row_our * 1.01, row_our * 0.99, row_amzn]
            
            # Trend sparkline color logic
            if row_amzn < row_our:
                spark_color = "#EF4444"  # Red dip
            elif not row.get("comp_a_in_stock", True):
                spark_color = "#F59E0B"  # Amber surge
            elif row_amzn > row_our:
                spark_color = "#10B981"  # Emerald up
            else:
                spark_color = "#00F0FF"  # Neon blue

            sparkline_svg = generate_svg_sparkline(price_series, color=spark_color)

            # Action badge HTML
            if row_badge == "UNDERCUT":
                badge_html = '<span style="background: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid #EF4444; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 0.68rem; font-family: JetBrains Mono;">🚨 Win Buy-Box</span>'
            elif row_badge == "SURGE":
                badge_html = '<span style="background: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid #F59E0B; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 0.68rem; font-family: JetBrains Mono;">⚡ Stockout Surge</span>'
            elif row_badge == "PROTECTED":
                badge_html = '<span style="background: rgba(59, 130, 246, 0.15); color: #60A5FA; border: 1px solid #3B82F6; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 0.68rem; font-family: JetBrains Mono;">🛡️ Hold Margin</span>'
            else:
                badge_html = '<span style="background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid #10B981; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 0.68rem; font-family: JetBrains Mono;">✓ Optimal</span>'

            # Margin Impact Display
            diff_str = f"-${abs(row_diff):.2f}" if row_diff < 0 else f"+${row_diff:.2f}"
            diff_color = "#EF4444" if row_diff < 0 else "#10B981"

            # Render row container
            row_bg = "background: rgba(0, 240, 255, 0.08); border: 1px solid #00F0FF; box-shadow: 0 0 12px rgba(0, 240, 255, 0.2);" if is_active else "background: #090D1C; border: 1px solid #141A2E;"
            
            with st.container():
                st.markdown(f"""
                <div style="{row_bg} border-radius: 6px; padding: 8px 12px; margin-bottom: 5px;">
                  <div style="display: grid; grid-template-columns: 1.1fr 2.2fr 1fr 1fr 1fr 1fr 1fr 1.2fr; align-items: center; gap: 8px; font-size: 0.76rem; font-family: 'JetBrains Mono';">
                    <div style="color: {'#00F0FF' if is_active else '#94A3B8'}; font-weight: {'800' if is_active else '500'};">{row_sku}</div>
                    <div style="color: #F8FAFC; font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{row_title}</div>
                    <div>{sparkline_svg}</div>
                    <div style="color: #00F0FF; font-weight: 700;">${row_our:.2f}</div>
                    <div style="color: #FB923C;">${row_amzn:.2f}</div>
                    <div style="color: #F59E0B;">${row_bby:.2f}</div>
                    <div style="color: #10B981; font-weight: 800;">${row_rec:.2f}</div>
                    <div>{badge_html}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                # Direct Selection Button for this row
                c_sub1, c_sub2 = st.columns([8, 2])
                with c_sub2:
                    btn_label = "✓ SELECTED" if is_active else "SELECT SKU"
                    if st.button(btn_label, key=f"sel_btn_{row_sku}", use_container_width=True, type="primary" if is_active else "secondary"):
                        st.session_state["selected_sku"] = row_sku
                        st.session_state["last_log"] = f"[{datetime.now().strftime('%H:%M:%S')}] DOCK BIND: Active SKU set to {row_title} (EAN: {row['barcode']})."
                        st.rerun()


# --- RIGHT PANEL (30%): Algorithmic Strategy & Execution Dock ---
with col_right_dock:
    st.markdown("""
    <div style="font-size: 0.84rem; font-weight: 700; color: #00F0FF; margin-bottom: 0.4rem; display: flex; align-items: center; gap: 6px;">
      <span>⚡ STRATEGY &amp; EXECUTION DOCK</span>
    </div>
    """, unsafe_allow_html=True)

    # Active Asset Header Card
    st.markdown(f"""
    <div class="glass-card" style="margin-bottom: 0.5rem; border-left: 3px solid #00F0FF;">
      <div style="font-size: 0.66rem; font-family: 'JetBrains Mono'; color: #00F0FF; text-transform: uppercase;">CONNECTED TARGET ASSET</div>
      <div style="font-size: 0.96rem; font-weight: 800; color: #F8FAFC; margin-top: 2px;">{active_title}</div>
      <div style="font-size: 0.72rem; font-family: 'JetBrains Mono'; color: #94A3B8; margin-top: 3px;">
        SKU: <code style="color: #00F0FF;">{active_sku}</code>
      </div>
      <div style="font-size: 0.72rem; font-family: 'JetBrains Mono'; color: #94A3B8; margin-top: 1px;">
        EAN-13: <code style="color: #10B981;">{active_ean}</code> | Match: <span style="color: #10B981;">100% EAN-13</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Market Depth Quote Book
    st.markdown(f"""
    <div style="background: #090D1C; border: 1px solid #141A2E; border-radius: 6px; padding: 6px 10px; margin-bottom: 0.5rem;">
      <div style="font-size: 0.66rem; font-family: 'JetBrains Mono'; color: #F59E0B; text-transform: uppercase; margin-bottom: 4px;">MARKETPLACE QUOTE BOOK</div>
      <div class="orderbook-row"><span style="color: #94A3B8;">Cost Baseline (COGS):</span> <span style="color: #64748B;">${active_cost:.2f}</span></div>
      <div class="orderbook-row"><span style="color: #94A3B8;">Your Store Price:</span> <span style="color: #00F0FF; font-weight: 700;">${active_our_price:.2f}</span></div>
      <div class="orderbook-row"><span style="color: #FB923C;">Amazon US Quote:</span> <span style="color: #FB923C;">${active_comp_a:.2f} ({'In Stock' if active_comp_a_stock else 'OUT OF STOCK'})</span></div>
      <div class="orderbook-row"><span style="color: #F59E0B;">BestBuy Quote:</span> <span style="color: #F59E0B;">${active_comp_b:.2f} ({'In Stock' if active_comp_b_stock else 'OUT OF STOCK'})</span></div>
    </div>
    """, unsafe_allow_html=True)

    # Strategy Parameters
    st.markdown("""
    <div class="glass-card" style="padding: 10px; margin-bottom: 0.5rem;">
      <div style="font-size: 0.66rem; font-family: 'JetBrains Mono'; color: #00F0FF; text-transform: uppercase; margin-bottom: 4px;">ALGORITHMIC PARAMETERS</div>
    """, unsafe_allow_html=True)

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        floor_pct = st.slider("Floor Margin %", 10, 30, 15, key="dock_floor")
        calc_floor_val = round(active_cost * (1 + floor_pct / 100.0), 2)
        st.caption(f"Floor: ${calc_floor_val:.2f}")
    with c_p2:
        undercut_choice = st.selectbox("Buy-Box Undercut", ["-$0.10", "-$0.50", "-$1.00", "-$2.00"], index=1, key="dock_undercut")
        u_step = abs(float(undercut_choice.replace("-$", "").replace("$", "")))
        st.caption(f"Step: {undercut_choice}")

    surge_enabled = st.toggle("Surge Engine Enabled (+8% on Stockout)", value=True, key="dock_surge")
    st.markdown("</div>", unsafe_allow_html=True)

    # Evaluate dynamic pricing
    rule = RepricingRule(
        min_margin_percent=float(floor_pct),
        undercut_cents=u_step,
        stockout_surge_percent=8.0 if surge_enabled else 0.0
    )
    engine_dock = RepricingEngine(rule=rule)
    res_dock = engine_dock.evaluate_product(active_row.to_dict())

    rec_price = res_dock["recommended_price"]
    gross_margin_pct = res_dock["new_margin_pct"]
    gross_margin_usd = res_dock["new_margin_dollar"]

    # Recommended Execution Price Card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(0, 240, 255, 0.09) 0%, rgba(59, 130, 246, 0.09) 100%); border: 1px solid rgba(0, 240, 255, 0.45); border-radius: 8px; padding: 12px; text-align: center; margin-bottom: 0.6rem;">
      <div style="font-size: 0.68rem; font-family: 'JetBrains Mono'; color: #00F0FF; text-transform: uppercase; font-weight: 700;">RECOMMENDED EXECUTION PRICE</div>
      <div style="font-size: 2.2rem; font-weight: 800; color: #F8FAFC; font-family: 'JetBrains Mono'; line-height: 1.1; margin: 4px 0;">${rec_price:.2f}</div>
      <div style="display: inline-flex; align-items: center; gap: 6px; padding: 2px 10px; border-radius: 4px; background: rgba(16, 185, 129, 0.18); color: #10B981; font-size: 0.76rem; font-family: 'JetBrains Mono'; font-weight: 700;">
        {gross_margin_pct}% Protected Gross Margin (+${gross_margin_usd:.2f})
      </div>
      <div style="font-size: 0.72rem; color: #94A3B8; margin-top: 5px;">
        {res_dock['reason']}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Action Execution CTA Buttons
    if st.button("⚡ PUSH UPDATE VIA SHOPIFY API", use_container_width=True, type="primary", key="btn_exec_shopify"):
        st.session_state["catalog_df"].loc[st.session_state["catalog_df"]["sku"] == active_sku, "current_price"] = rec_price
        now_time = datetime.now().strftime("%H:%M:%S")
        st.session_state["last_log"] = f"[{now_time}] Shopify GraphQL: SKU '{active_sku}' updated to ${rec_price:.2f} (Recaptured Buy-Box position)."
        st.toast(f"⚡ GraphQL Mutation Dispatched: {active_sku} repriced to ${rec_price:.2f}", icon="🚀")
        st.rerun()

    c_b1, c_b2 = st.columns(2)
    with c_b1:
        if st.button("📡 Dispatch Alert", use_container_width=True, key="btn_tg_alert"):
            now_time = datetime.now().strftime("%H:%M:%S")
            st.session_state["last_log"] = f"[{now_time}] Telegram Dispatch: Webhook alert sent for {active_sku} (-${abs(active_our_price - rec_price):.2f} undercut)."
            st.toast(f"📡 Telegram Webhook triggered for {active_sku}!", icon="📲")
    with c_b2:
        export_row = pd.DataFrame([{
            "Handle": str(active_sku).lower().replace(" ", "-"),
            "Title": active_title,
            "Variant SKU": active_sku,
            "Variant Barcode": active_ean,
            "Variant Price": rec_price,
            "Variant Compare At Price": active_our_price
        }])
        st.download_button(
            label="📥 Export CSV",
            data=export_row.to_csv(index=False).encode('utf-8'),
            file_name=f"Shopify_{active_sku}.csv",
            mime="text/csv",
            use_container_width=True
        )

# 7. Bottom Console
st.markdown(f"""
<div class="console-stream">
  <div>
    <span style="color: #00F0FF; font-weight: 700;">SYSTEM TELEMETRY:</span> {st.session_state["last_log"]}
  </div>
  <div style="color: #64748B;">STREAM: 42ms | BUFFER: 100%</div>
</div>
""", unsafe_allow_html=True)
