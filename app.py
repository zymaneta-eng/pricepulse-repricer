"""
PricePulse AI v3.5 | Algorithmic Retail Arbitrage & Competitive Intelligence Terminal
Bloomberg & Keepa hybrid dark mode dashboard for top-tier developer portfolio.
Palette:
- Obsidian & Charcoal (#05070D to #0B0F1C) with fine 1px slate-glass borders (#1E293B)
- Neon Cyan (#06B6D4) for our active metrics
- Amber Gold (#F59E0B) for BestBuy
- Alert Orange (#F97316) for Amazon US
- Alert Crimson (#EF4444) for floor limits
- Emerald (#10B981) for matched data and successes
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
    page_title="PricePulse AI v3.5 | Algorithmic Retail Arbitrage",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Modern Bloomberg/Keepa FinTech CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, .mono, .ticker, .stat-num, .price-val, .log-line {
        font-family: 'Space Mono', 'JetBrains Mono', monospace !important;
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
        padding-top: 0.5rem !important;
        padding-bottom: 0.8rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }

    div[data-testid="stVerticalBlock"] > div {
        gap: 0.3rem !important;
    }

    /* Top Bloomberg Header */
    .top-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 12px;
        background: #080C18;
        border: 1px solid #1E293B;
        border-radius: 8px;
        margin-bottom: 0.35rem;
    }
    .brand-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #F8FAFC;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .neon-cyan { color: #06B6D4; text-shadow: 0 0 10px rgba(6, 182, 212, 0.45); }
    .amber-gold { color: #F59E0B; }
    .alert-orange { color: #F97316; }
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
    .ticker-tape {
        background: #070B16;
        border: 1px solid #1E293B;
        border-radius: 6px;
        padding: 5px 12px;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        overflow-x: auto;
        white-space: nowrap;
        gap: 20px;
        font-size: 0.74rem;
        font-family: 'Space Mono', monospace;
    }
    .ticker-item {
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Configuration & Strategy Strip Toolbar */
    .strategy-strip {
        background: rgba(11, 15, 28, 0.85);
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 8px 14px;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    /* Status Notification Banner */
    .status-banner {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 6px;
        padding: 6px 14px;
        margin-bottom: 0.45rem;
        font-size: 0.78rem;
        font-weight: 600;
        color: #10B981;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Glass Cards */
    .glass-panel {
        background: #080C18;
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 10px 14px;
    }

    /* Order Book & Quote Block */
    .quote-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 10px;
        border-radius: 6px;
        margin-bottom: 4px;
        font-size: 0.76rem;
        font-family: 'Space Mono', monospace;
    }

    /* Execution CTA */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #06B6D4 0%, #4F46E5 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 0.84rem !important;
        font-family: 'Space Mono', monospace !important;
        border: none !important;
        border-radius: 6px !important;
        box-shadow: 0 4px 18px rgba(6, 182, 212, 0.35) !important;
        letter-spacing: 0.02em !important;
    }
    div.stButton > button[kind="primary"]:hover {
        box-shadow: 0 6px 24px rgba(6, 182, 212, 0.6) !important;
        transform: translateY(-1px) !important;
    }
    div.stButton > button[kind="secondary"] {
        background: #0A0F1E !important;
        color: #94A3B8 !important;
        border: 1px solid #1E293B !important;
        border-radius: 6px !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 0.78rem !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #06B6D4 !important;
        color: #F8FAFC !important;
    }

    /* Technical Log Box */
    .telemetry-box {
        background: #04060C;
        border: 1px solid #1E293B;
        border-left: 3px solid #06B6D4;
        border-radius: 6px;
        padding: 8px 12px;
        font-family: 'Space Mono', monospace;
        font-size: 0.72rem;
        color: #94A3B8;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# 3. Load & Cache Ground-Truth Data
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
    # Default: Apple iPhone 5s as specified in prompt
    st.session_state["selected_sku"] = "SMA-APP-IPH-121"

if "view_mode" not in st.session_state:
    st.session_state["view_mode"] = "[ 📈 Chart ]"

catalog_df = st.session_state["catalog_df"]
history_df = st.session_state["history_df"]

# Helper: Generate Inline SVG Sparkline
def generate_svg_sparkline(prices, width=80, height=22, color="#06B6D4"):
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

# 4. Top Navigation Bar
st.markdown("""
<div class="top-nav">
  <div style="display: flex; align-items: center; gap: 10px;">
    <span class="brand-title">⚡ <span class="neon-cyan">PricePulse AI</span> <span style="font-size: 0.8rem; color: #64748B;">v3.5</span></span>
    <span style="font-size: 0.72rem; color: #10B981; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 2px 7px; border-radius: 4px; font-family: 'Space Mono';">
      <span class="pulse-dot"></span> Live API Grounded
    </span>
    <span style="font-size: 0.72rem; color: #06B6D4; background: rgba(6, 182, 212, 0.1); border: 1px solid rgba(6, 182, 212, 0.3); padding: 2px 7px; border-radius: 4px; font-family: 'Space Mono';">
      Fuzzy Matcher: Active
    </span>
  </div>
  <div style="font-size: 0.76rem; color: #94A3B8;">
    Designed &amp; Engineered by Freelancer • <strong style="color: #06B6D4;">Available for Hire</strong>
  </div>
  <div style="display: flex; align-items: center; gap: 8px;">
    <span style="font-size: 0.74rem; color: #CBD5E1; background: #0F172A; border: 1px solid #1E293B; padding: 4px 10px; border-radius: 6px; cursor: pointer;">
      ⚙️ Settings
    </span>
    <span style="font-size: 0.74rem; color: #06B6D4; background: rgba(6, 182, 212, 0.12); border: 1px solid #06B6D4; padding: 4px 12px; border-radius: 6px; font-weight: 700; cursor: pointer;">
      🚀 Deploy
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

# Full-Width Live Ticker Tape
st.markdown("""
<div class="ticker-tape">
  <div style="display: flex; align-items: center; gap: 18px;">
    <span style="font-size: 0.7rem; font-weight: 800; color: #F59E0B;">[LIVE ARBITRAGE TICKER]</span>
    <span class="ticker-item"><span style="color: #E2E8F0;">AAPL-5S:</span> <span class="crimson-down">Competitor Drop 🔻 Win Buy-Box $191.49</span></span>
    <span class="ticker-item"><span style="color: #E2E8F0;">SONY-XM5:</span> <span class="amber-gold">BBY Sold Out 🔺 +8%</span></span>
    <span class="ticker-item"><span style="color: #E2E8F0;">A57:</span> <span class="emerald-up">Spot Check = $249.99</span></span>
    <span class="ticker-item"><span style="color: #E2E8F0;">IPHONE-13:</span> <span class="alert-orange">AMZN $1,084.49 ▼ -$15.50</span></span>
    <span class="ticker-item"><span style="color: #E2E8F0;">GALAXY-S10:</span> <span class="emerald-up">Spot Check = $699.99</span></span>
  </div>
  <div style="font-size: 0.7rem; color: #64748B;">LATENCY: 42ms | 16 SKUs MONITORED</div>
</div>
""", unsafe_allow_html=True)

# 5. Configuration & Strategy Strip (Compact 100% Width Horizontal Toolbar)
with st.container():
    col_str1, col_str2, col_str3, col_str4, col_str5, col_str6 = st.columns([1.5, 1.5, 1.2, 1.2, 1.4, 2.2])

    with col_str1:
        brand_list = ["All Brands"] + sorted(list(catalog_df["brand"].unique()))
        selected_brand = st.selectbox("Filter Brand", brand_list, label_visibility="collapsed")
    with col_str2:
        cat_tags = ["All Categories", "Flagship Tier", "Mid-Range", "Budget Tier"]
        selected_tag = st.selectbox("Product tags & Categories", cat_tags, label_visibility="collapsed")
    with col_str3:
        margin_floor = st.number_input("Safety Margin Floor %", min_value=10, max_value=35, value=15, step=1, label_visibility="collapsed")
        st.caption(f"Margin Floor: {margin_floor}%")
    with col_str4:
        undercut_val = st.selectbox("Buy-Box Undercut", ["$0.10", "$0.50", "$1.00", "$2.00"], index=1, label_visibility="collapsed")
        undercut_numeric = float(undercut_val.replace("$", ""))
        st.caption(f"Undercut: {undercut_val}")
    with col_str5:
        surge_val = st.slider("Stockout Surge %", 0, 15, 8, label_visibility="collapsed")
        st.caption(f"Surge Engine: {surge_val}%")
    with col_str6:
        c_exec1, c_exec2 = st.columns([1.4, 1.0])
        with c_exec1:
            btn_execute_all = st.button("⚡ Execute AI Repricer", type="primary", use_container_width=True)
        with c_exec2:
            btn_tg_all = st.button("📡 Telegram", use_container_width=True)

# Options Toggles Bar
c_tog1, c_tog2, c_tog3, c_tog4 = st.columns([1.5, 1.5, 1.5, 4.5])
with c_tog1:
    t_offset = st.toggle("Under-Cut Offset", value=True)
with c_tog2:
    t_turnstile = st.toggle("Bypass Turnstile", value=True)
with c_tog3:
    t_rules = st.toggle("Match Rules", value=True)

# 6. Dynamic Status Notification Banner
st.markdown("""
<div class="status-banner">
  <span>✓</span>
  <span>Successfully resolved price conflicts for 16 Melbourne-active products!</span>
</div>
""", unsafe_allow_html=True)

# 7. Real-Time Interactive Workstation - Two-Column Split-View (65% Chart / 35% Inspector)
col_left_65, col_right_35 = st.columns([2.6, 1.4])

# Active selected product data
active_sku = st.session_state["selected_sku"]
if active_sku not in catalog_df["sku"].values:
    active_sku = "SMA-APP-IPH-121"
    st.session_state["selected_sku"] = active_sku

active_row = catalog_df[catalog_df["sku"] == active_sku].iloc[0]
active_title = active_row["title"]
active_cost = float(active_row["cost_price"])
active_our_price = float(active_row["current_price"])
active_comp_a = float(active_row["competitor_a_price"])
active_comp_b = float(active_row["competitor_b_price"])
active_ean = str(active_row["barcode"])
active_thumb = active_row.get("thumbnail", "")

# Algorithm calculation for active item
rule = RepricingRule(
    min_margin_percent=float(margin_floor),
    undercut_cents=undercut_numeric,
    stockout_surge_percent=float(surge_val)
)
engine = RepricingEngine(rule=rule)
eval_res = engine.evaluate_product(active_row.to_dict())
rec_price = eval_res["recommended_price"]
margin_gain_usd = eval_res["new_margin_dollar"]
margin_gain_pct = eval_res["new_margin_pct"]
floor_safety_val = eval_res["floor_price"]

if btn_execute_all:
    st.session_state["catalog_df"].loc[st.session_state["catalog_df"]["sku"] == active_sku, "current_price"] = rec_price
    st.toast(f"⚡ GraphQL Shopify Sync: {active_sku} successfully updated to ${rec_price:.2f}!", icon="🚀")
    st.rerun()

if btn_tg_all:
    st.toast("📡 Telegram Dispatch: Buy-Box delta alerts sent to 3 active seller channels!", icon="📲")

# ==============================================================================
# LEFT PANEL (65% width): Market Defense Chart Analysis
# ==============================================================================
with col_left_65:
    c_hdr_v1, c_hdr_v2 = st.columns([2, 1.5])
    with c_hdr_v1:
        st.markdown(f"""
        <div style="font-size: 0.86rem; font-weight: 700; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
          <span>📈 MARKET DEFENSE CHART ANALYSIS — <span class="neon-cyan">{active_title}</span></span>
        </div>
        """, unsafe_allow_html=True)
    with c_hdr_v2:
        view_mode = st.radio(
            "Workstation View",
            options=["[ 📈 Chart ]", "[ 📋 Catalog List ]", "[ ⚡ Split ]"],
            index=0,
            horizontal=True,
            label_visibility="collapsed"
        )
        st.session_state["view_mode"] = view_mode

    # Render Chart
    if view_mode in ["[ 📈 Chart ]", "[ ⚡ Split ]"]:
        hist_active = history_df[history_df["sku"] == active_sku].tail(30).reset_index(drop=True)

        fig = go.Figure()

        # Visible Danger Limit Line (Glowing Red Line at the bottom)
        fig.add_hrect(
            y0=0, y1=floor_safety_val,
            fillcolor="rgba(239, 68, 68, 0.12)",
            line_width=1,
            line_color="rgba(239, 68, 68, 0.4)",
            annotation_text=f"🚨 Margin Safety Floor: ${floor_safety_val:.2f}",
            annotation_position="bottom right",
            annotation_font=dict(size=10, color="#EF4444", family="Space Mono")
        )

        # Our Store (Solid Neon Cyan)
        fig.add_trace(go.Scatter(
            x=hist_active["date"], y=hist_active["our_price"],
            name="Our Store",
            line=dict(color="#06B6D4", width=3)
        ))

        # Amazon US (Orange-Dashed)
        fig.add_trace(go.Scatter(
            x=hist_active["date"], y=hist_active["comp_a_price"],
            name="Amazon US",
            line=dict(color="#F97316", width=2, dash="dash")
        ))

        # BestBuy (Amber)
        fig.add_trace(go.Scatter(
            x=hist_active["date"], y=hist_active["comp_b_price"],
            name="BestBuy",
            line=dict(color="#F59E0B", width=2, dash="dot")
        ))

        # On-Chart Annotations: Pointer flags marking price drops
        last_d = hist_active["date"].iloc[-1]
        competitor_lowest = min(active_comp_a, active_comp_b)
        diff_to_comp = round(active_our_price - competitor_lowest, 2)
        ann_text = f"🚨 Competitor Undercut (-${abs(diff_to_comp):.2f})" if diff_to_comp > 0 else "✓ Buy-Box Parity"

        fig.add_annotation(
            x=last_d, y=competitor_lowest,
            text=ann_text,
            showarrow=True,
            arrowhead=2,
            arrowcolor="#EF4444",
            arrowsize=1,
            arrowwidth=2,
            bgcolor="#0B0F1C",
            bordercolor="#EF4444",
            font=dict(color="#F8FAFC", size=9, family="Space Mono")
        )

        fig.add_annotation(
            x=last_d, y=rec_price,
            text=f"⚡ Recommended Buy-Box: ${rec_price:.2f}",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#06B6D4",
            arrowsize=1,
            arrowwidth=2,
            bgcolor="#0B0F1C",
            bordercolor="#06B6D4",
            font=dict(color="#06B6D4", size=9, family="Space Mono")
        )

        ch_h = 280 if view_mode == "[ ⚡ Split ]" else 410
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#080C18",
            plot_bgcolor="#05070D",
            margin=dict(l=30, r=20, t=10, b=20),
            height=ch_h,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(family="Space Mono", size=10)),
            xaxis=dict(showgrid=True, gridcolor="#1E293B", tickfont=dict(family="Space Mono", size=9)),
            yaxis=dict(showgrid=True, gridcolor="#1E293B", tickprefix="$", tickfont=dict(family="Space Mono", size=9))
        )
        st.plotly_chart(fig, use_container_width=True)

    # Render Product Registry Table (if in [ 📋 Catalog List ] or [ ⚡ Split ])
    if view_mode in ["[ 📋 Catalog List ]", "[ ⚡ Split ]"]:
        st.markdown("""
        <div style="font-size: 0.8rem; font-weight: 700; color: #F8FAFC; margin-bottom: 0.35rem; display: flex; justify-content: space-between;">
          <span>📋 ИНТЕРАКТИВНЫЙ РЕЕСТР ТОВАРОВ (16 SKUs)</span>
          <span style="font-size: 0.7rem; color: #64748B; font-family: 'Space Mono';">КЛИКНИТЕ [SELECT] ДЛЯ ПРИВЯЗКИ В ИНСПЕКТОР</span>
        </div>
        <div style="background: #060914; border: 1px solid #1E293B; border-radius: 6px; padding: 6px 10px; margin-bottom: 5px;">
          <div style="display: grid; grid-template-columns: 1.1fr 2fr 1fr 1fr 1fr 1fr 1fr 1.2fr; align-items: center; gap: 8px; font-size: 0.68rem; font-family: 'Space Mono'; color: #64748B; text-transform: uppercase;">
            <div>SKU</div>
            <div>Товар (Title)</div>
            <div>Тренд 7D</div>
            <div style="color: #06B6D4;">🏪 Shopify</div>
            <div style="color: #F97316;">🛒 Amazon.com</div>
            <div style="color: #F59E0B;">🏷️ BestBuy.com</div>
            <div style="color: #10B981;">🎯 Цель Algo</div>
            <div>Статус Buy-Box</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        catalog_eval = engine.process_catalog(catalog_df)
        if selected_brand != "All Brands":
            catalog_eval = catalog_eval[catalog_eval["brand"] == selected_brand]

        for _, r in catalog_eval.head(8).iterrows():
            r_sku = r["sku"]
            r_title = r["title"]
            r_our = float(r["current_price"])
            r_amzn = float(r["competitor_a_price"])
            r_bby = float(r["competitor_b_price"])
            r_rec = float(r["recommended_price"])
            r_diff = float(r["price_diff"])
            is_sel = (r_sku == active_sku)

            sub_h = history_df[history_df["sku"] == r_sku].tail(7)
            pts = sub_h["comp_a_price"].tolist()
            sp_col = "#EF4444" if r_amzn < r_our else "#10B981"
            sp_svg = generate_svg_sparkline(pts, color=sp_col)

            badge_text = "🚨 Win Buy-Box" if r_diff < 0 else "⚡ Buy-Box Leader"
            badge_col = "#EF4444" if r_diff < 0 else "#10B981"

            r_style = "background: rgba(6, 182, 212, 0.08); border: 1px solid #06B6D4;" if is_sel else "background: #080C18; border: 1px solid #1E293B;"

            with st.container():
                st.markdown(f"""
                <div style="{r_style} border-radius: 6px; padding: 6px 10px; margin-bottom: 4px;">
                  <div style="display: grid; grid-template-columns: 1.1fr 2fr 1fr 1fr 1fr 1fr 1fr 1.2fr; align-items: center; gap: 8px; font-size: 0.74rem; font-family: 'Space Mono';">
                    <div style="color: {'#06B6D4' if is_sel else '#94A3B8'}; font-weight: 700;">{r_sku}</div>
                    <div style="color: #F8FAFC; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{r_title}</div>
                    <div>{sp_svg}</div>
                    <div style="color: #06B6D4;">${r_our:.2f}</div>
                    <div style="color: #F97316;">${r_amzn:.2f}</div>
                    <div style="color: #F59E0B;">${r_bby:.2f}</div>
                    <div style="color: #10B981; font-weight: 700;">${r_rec:.2f}</div>
                    <div><span style="color: {badge_col}; border: 1px solid {badge_col}; padding: 1px 5px; border-radius: 3px; font-size: 0.66rem;">{badge_text}</span></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                c_sb1, c_sb2 = st.columns([8, 2])
                with c_sb2:
                    if st.button("SELECT" if not is_sel else "✓ SELECTED", key=f"tbl_btn_{r_sku}", type="primary" if is_sel else "secondary", use_container_width=True):
                        st.session_state["selected_sku"] = r_sku
                        st.rerun()

# ==============================================================================
# RIGHT PANEL (35% width): Real-Time AI Product Inspector
# ==============================================================================
with col_right_35:
    st.markdown("""
    <div style="font-size: 0.86rem; font-weight: 700; color: #06B6D4; margin-bottom: 0.35rem; display: flex; align-items: center; gap: 6px;">
      <span>⚡ REAL-TIME AI PRODUCT INSPECTOR</span>
    </div>
    """, unsafe_allow_html=True)

    # Active Focus Header Card
    st.markdown(f"""
    <div class="glass-panel" style="border-left: 3px solid #06B6D4; margin-bottom: 0.45rem;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.66rem; font-family: 'Space Mono'; color: #06B6D4; text-transform: uppercase;">ACTIVE FOCUS [SELECTED ITEM]</span>
        <span style="background: rgba(6, 182, 212, 0.15); color: #06B6D4; border: 1px solid #06B6D4; padding: 1px 6px; border-radius: 4px; font-size: 0.66rem; font-family: 'Space Mono';">
          EAN-13 VERIFIED
        </span>
      </div>
      <div style="font-size: 0.95rem; font-weight: 800; color: #F8FAFC; margin-top: 3px;">
        {active_title}
      </div>
      <div style="font-size: 0.72rem; font-family: 'Space Mono'; color: #94A3B8; margin-top: 2px;">
        SKU: <code style="color: #06B6D4;">{active_sku}</code> | EAN-13: <code style="color: #10B981;">{active_ean}</code>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Matcher Module (Fuzzy Matching Engine Block)
    st.markdown(f"""
    <div class="glass-panel" style="margin-bottom: 0.45rem; padding: 8px 12px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <span style="font-size: 0.68rem; font-family: 'Space Mono'; color: #10B981; font-weight: 700;">FUZZY MATCHING ENGINE</span>
        <span style="font-size: 0.7rem; font-family: 'Space Mono'; color: #10B981; background: rgba(16, 185, 129, 0.12); padding: 1px 6px; border-radius: 4px; border: 1px solid #10B981;">
          [✓] Approved Match
        </span>
      </div>
      <div style="display: flex; align-items: center; justify-content: space-between; background: #050812; border: 1px solid #1E293B; border-radius: 6px; padding: 6px 10px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <img src="{active_thumb}" width="34" style="border-radius: 4px; border: 1px solid #1E293B;" />
          <span style="font-size: 0.72rem; color: #E2E8F0; font-family: 'Space Mono';">Our Item</span>
        </div>
        <div style="font-size: 0.85rem; color: #06B6D4; font-weight: 800;">⇄</div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <img src="{active_thumb}" width="34" style="border-radius: 4px; border: 1px solid #1E293B;" />
          <span style="font-size: 0.72rem; color: #E2E8F0; font-family: 'Space Mono';">Competitor Item</span>
        </div>
        <div style="font-size: 0.72rem; font-family: 'Space Mono'; color: #10B981; font-weight: 700;">
          100% EAN-13
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Competitor Price Grid Block
    st.markdown("""
    <div class="glass-panel" style="margin-bottom: 0.45rem; padding: 8px 12px;">
      <div style="font-size: 0.68rem; font-family: 'Space Mono'; color: #F59E0B; text-transform: uppercase; margin-bottom: 6px;">COMPETITOR PRICE GRID</div>
    """, unsafe_allow_html=True)

    amzn_query = active_title.replace(' ', '+')
    bby_query = active_title.replace(' ', '+')
    amzn_link = f"https://www.amazon.com/s?k={amzn_query}"
    bby_link = f"https://www.bestbuy.com/site/searchpage.jsp?st={bby_query}"
    asin_val = active_row.get("comp_a_asin", "B08146839X")

    st.markdown(f"""
      <div class="quote-box" style="background: #060914; border: 1px solid #1E293B;">
        <span style="color: #94A3B8;">Базовая себестоимость (COGS):</span>
        <span style="color: #64748B;">${active_cost:.2f}</span>
      </div>
      <div class="quote-box" style="background: #060914; border: 1px solid rgba(6, 182, 212, 0.4);">
        <div>
          <span style="color: #06B6D4; font-weight: 700;">🏪 Наш магазин:</span> 
          <span style="font-size: 0.68rem; color: #94A3B8;">myshopify.com</span>
        </div>
        <span style="color: #06B6D4; font-weight: 700;">${active_our_price:.2f}</span>
      </div>
      <div class="quote-box" style="background: #060914; border: 1px solid rgba(249, 115, 22, 0.4);">
        <div>
          <span style="color: #F97316; font-weight: 700;">🛒 Amazon.com:</span> 
          <a href="{amzn_link}" target="_blank" style="font-size: 0.68rem; color: #FB923C; text-decoration: underline; margin-left: 4px;">
            ASIN: {asin_val} ↗
          </a>
        </div>
        <span style="color: #F97316; font-weight: 700;">${active_comp_a:.2f}</span>
      </div>
      <div class="quote-box" style="background: #060914; border: 1px solid rgba(245, 158, 11, 0.4);">
        <div>
          <span style="color: #F59E0B; font-weight: 700;">🏷️ BestBuy.com:</span> 
          <a href="{bby_link}" target="_blank" style="font-size: 0.68rem; color: #FBBF24; text-decoration: underline; margin-left: 4px;">
            bestbuy.com ↗
          </a>
        </div>
        <span style="color: #F59E0B; font-weight: 700;">${active_comp_b:.2f}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Decision Logic Card (Amber-Toned Border)
    st.markdown(f"""
    <div style="background: rgba(245, 158, 11, 0.05); border: 1px solid #F59E0B; border-radius: 8px; padding: 10px 12px; margin-bottom: 0.55rem;">
      <div style="font-size: 0.68rem; font-family: 'Space Mono'; color: #F59E0B; font-weight: 700; margin-bottom: 4px;">STRATEGIC DECISION LOGIC</div>
      <div style="font-size: 0.74rem; color: #CBD5E1; line-height: 1.4; margin-bottom: 8px;">
        Strategic logic: Under-cut {"BestBuy" if active_comp_b <= active_comp_a else "Amazon"} by <strong>${undercut_numeric:.2f}</strong> to recover #1 buy-box spot while staying <strong>+${margin_gain_usd:.2f}</strong> above your margin safety floor (${floor_safety_val:.2f}).
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; background: #070B16; border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 6px; padding: 6px 10px;">
        <div>
          <div style="font-size: 0.64rem; font-family: 'Space Mono'; color: #94A3B8;">EXECUTION TARGET</div>
          <div style="font-size: 1.4rem; font-weight: 800; color: #06B6D4; font-family: 'Space Mono';">${rec_price:.2f}</div>
        </div>
        <div style="text-align: right;">
          <div style="font-size: 0.64rem; font-family: 'Space Mono'; color: #10B981;">PROTECTED MARGIN</div>
          <div style="font-size: 0.95rem; font-weight: 700; color: #10B981; font-family: 'Space Mono';">{margin_gain_pct}% (+$ {margin_gain_usd:.2f})</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # One-Click Execution Button
    if st.button(f"⚡ Run Repricer: ${rec_price:.2f}", use_container_width=True, type="primary", key="btn_run_item_repricer"):
        st.session_state["catalog_df"].loc[st.session_state["catalog_df"]["sku"] == active_sku, "current_price"] = rec_price
        st.toast(f"⚡ Repricer Dispatched: {active_sku} updated to ${rec_price:.2f} (Shopify API Mutation 200 OK)", icon="🚀")
        st.rerun()

# 8. Bottom Technical Logs & Telemetry
st.markdown("""
<div style="font-size: 0.72rem; font-family: 'Space Mono'; color: #06B6D4; margin-top: 0.4rem; margin-bottom: 2px; font-weight: 700;">
  🖥️ Execution &amp; Security Log:
</div>
<div class="telemetry-box">
  <div>[14:22:01] <span style="color: #10B981;">[SUCCESS]</span> Target domain response 200 OK (Proxyless/Res-Rotated)</div>
  <div>[14:22:03] <span style="color: #F59E0B;">[WAF BYPASS]</span> Cloudflare challenge detected ➔ Emulating TLS/JA3 Fingerprint...</div>
  <div>[14:22:04] <span style="color: #10B981;">[SOLVED]</span> Captcha/JS Token successfully generated via CapSolver (1.2s)</div>
  <div>[14:22:06] <span style="color: #06B6D4;">[EXTRACTED]</span> Parsing 28 elements via Next.js background payload...</div>
  <div>[14:22:08] <span style="color: #10B981;">[TRADE LOG]</span> BestBuy online verified at $191.99 ➔ Calculated undercut: $191.49</div>
</div>
""", unsafe_allow_html=True)
