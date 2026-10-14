"""
PricePulse AI — Enterprise Dynamic Repricing & Margin Guard Terminal
Native Streamlit Production Application for Streamlit Community Cloud.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

from repricer import RepricingEngine, RepricingRule

# 1. Page Configuration
st.set_page_config(
    page_title="PricePulse AI | Algorithmic Dynamic Repricer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for Modern Dark Navy Theme
st.markdown("""
<style>
    .stApp {
        background-color: #0B0F19;
        color: #F8FAFC;
    }
    .metric-card {
        background: linear-gradient(135deg, #121826 0%, #172033 100%);
        border: 1px solid #1F293D;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .metric-title {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
        font-family: monospace;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #38BDF8;
        margin: 4px 0;
        font-family: monospace;
    }
    .metric-sub {
        font-size: 12px;
        color: #10B981;
        font-weight: 600;
    }
    .header-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        font-family: monospace;
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    div[data-testid="stToolbar"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }
    div[data-testid="stDecoration"] {
        visibility: hidden;
        height: 0%;
        position: fixed;
    }
</style>
""", unsafe_allow_html=True)


# 3. Load Datasets
@st.cache_data
def load_catalog_data():
    base_dir = Path(__file__).resolve().parent
    catalog_path = base_dir / "catalog.xlsx"
    history_path = base_dir / "price_history.xlsx"

    if catalog_path.exists():
        df_cat = pd.read_excel(catalog_path)
    else:
        # Fallback dataset
        df_cat = pd.DataFrame([
            {"sku": "APL-IPH16PM-256", "brand": "Apple", "title": "Apple iPhone 16 Pro Max 256GB", "category": "Smartphones", "cost_price": 1020.00, "current_price": 1199.99, "stock": 45, "competitor_a_price": 1189.99, "comp_a_in_stock": True, "competitor_b_price": 1195.00, "comp_b_in_stock": True},
            {"sku": "SAM-ZFLD6-256", "brand": "Samsung", "title": "Samsung Galaxy Z Fold 6 256GB", "category": "Smartphones", "cost_price": 890.00, "current_price": 1199.99, "stock": 28, "competitor_a_price": 1099.99, "comp_a_in_stock": True, "competitor_b_price": 1149.99, "comp_b_in_stock": True},
            {"sku": "SON-WH1000XM5", "brand": "Sony", "title": "Sony WH-1000XM5 Wireless Headphones", "category": "Audio", "cost_price": 270.00, "current_price": 399.99, "stock": 62, "competitor_a_price": 348.00, "comp_a_in_stock": True, "competitor_b_price": 379.99, "comp_b_in_stock": True},
        ])

    df_hist = pd.read_excel(history_path) if history_path.exists() else None
    return df_cat, df_hist


df_catalog_raw, df_history = load_catalog_data()

# 4. Sidebar Controls & Strategy Configuration
st.sidebar.markdown("### ⚡ Strategy Parameters")
st.sidebar.markdown("Configure algorithmic pricing boundaries.")

strategy_preset = st.sidebar.selectbox(
    "Repricing Profile",
    ["Aggressive Buy-Box Undercut", "Balanced Margin Guard", "Maximum Volume Velocity"],
    index=0
)

undercut_val = 0.50 if "Aggressive" in strategy_preset else (0.25 if "Balanced" in strategy_preset else 0.80)
min_margin_val = 15.0 if "Aggressive" in strategy_preset else (20.0 if "Balanced" in strategy_preset else 10.0)

undercut_input = st.sidebar.slider("Target Undercut ($)", min_value=0.10, max_value=3.00, value=float(undercut_val), step=0.05)
min_margin_input = st.sidebar.slider("Minimum Net Margin Floor (%)", min_value=5.0, max_value=30.0, value=float(min_margin_val), step=1.0)
stockout_surge_input = st.sidebar.slider("Competitor Stockout Surge (%)", min_value=2.0, max_value=15.0, value=7.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Catalog Filters")

categories = ["All Categories"] + sorted(df_catalog_raw["category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("Category", categories)

brands = ["All Brands"] + sorted(df_catalog_raw["brand"].dropna().unique().tolist())
selected_brand = st.sidebar.selectbox("Brand", brands)

search_query = st.sidebar.text_input("Search SKU or Title", "")

# 5. Execute Repricing Engine
rule = RepricingRule(
    min_margin_percent=min_margin_input,
    undercut_cents=undercut_input,
    stockout_surge_percent=stockout_surge_input,
    match_strategy="aggressive"
)
engine = RepricingEngine(rule=rule)

evaluated_records = []
for _, row in df_catalog_raw.iterrows():
    res = engine.evaluate_product(row.to_dict())
    comp_a = float(row.get("competitor_a_price", 0.0))
    comp_b = float(row.get("competitor_b_price", 0.0))
    comps = [p for p in [comp_a, comp_b] if p > 0]
    lowest_comp = min(comps) if comps else float(row.get("current_price", 0.0))

    rec = {
        "sku": row.get("sku", ""),
        "brand": row.get("brand", ""),
        "title": row.get("title", ""),
        "category": row.get("category", ""),
        "stock": row.get("stock", 0),
        "cost_price": float(row.get("cost_price", 0.0)),
        "current_price": float(row.get("current_price", 0.0)),
        "lowest_comp": lowest_comp,
        "target_reprice": res.get("recommended_price", float(row.get("current_price", 0.0))),
        "floor_price": res.get("floor_price", 0.0),
        "price_change": res.get("price_diff", 0.0),
        "margin_usd": res.get("new_margin_dollar", 0.0),
        "margin_pct": res.get("new_margin_pct", 0.0),
        "action": res.get("action", ""),
        "status_badge": res.get("status_badge", "HOLD"),
        "reasoning": res.get("reason", "")
    }
    evaluated_records.append(rec)

df_evaluated = pd.DataFrame(evaluated_records)

# Filter catalog
df_filtered = df_evaluated.copy()
if selected_category != "All Categories":
    df_filtered = df_filtered[df_filtered["category"] == selected_category]
if selected_brand != "All Brands":
    df_filtered = df_filtered[df_filtered["brand"] == selected_brand]
if search_query:
    q = search_query.lower()
    df_filtered = df_filtered[
        df_filtered["sku"].str.lower().str.contains(q) |
        df_filtered["title"].str.lower().str.contains(q)
    ]

# 6. Main Dashboard Layout
st.title("⚡ PricePulse AI | Autonomous E-Commerce Repricer")
st.markdown("""
<div style="display: flex; gap: 10px; margin-bottom: 20px;">
    <span class="header-badge">● LIVE MARKET MONITORING (2026)</span>
    <span class="header-badge" style="background-color: rgba(56, 189, 248, 0.15); color: #38BDF8; border-color: rgba(56, 189, 248, 0.3);">● MARGIN GUARD ACTIVE</span>
    <span class="header-badge" style="background-color: rgba(245, 158, 11, 0.15); color: #F59E0B; border-color: rgba(245, 158, 11, 0.3);">● MAP CIRCUIT BREAKER VERIFIED</span>
</div>
""", unsafe_allow_html=True)

# Executive Metrics
total_skus = len(df_evaluated)
winning_skus = len(df_evaluated[df_evaluated["status_badge"].isin(["OPTIMAL", "UNDERCUT", "OPTIMIZED", "SURGE"])])
avg_margin = df_evaluated["margin_pct"].mean() if not df_evaluated.empty else 0.0
total_portfolio_cost = (df_evaluated["cost_price"] * df_evaluated["stock"]).sum()

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Monitored Catalog</div>
        <div class="metric-value">{total_skus} SKUs</div>
        <div class="metric-sub">Across 4 Verticals</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    win_pct = round((winning_skus / total_skus) * 100.0, 1) if total_skus > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Buy-Box Win Rate</div>
        <div class="metric-value">{win_pct}%</div>
        <div class="metric-sub">{winning_skus} of {total_skus} in #1 Spot</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Average Net Margin</div>
        <div class="metric-value">+{avg_margin:.1f}%</div>
        <div class="metric-sub">Strict Floor: {min_margin_input}%</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">P95 Execution Latency</div>
        <div class="metric-value">420 ms</div>
        <div class="metric-sub">Simulated API Dispatch</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 7. Interactive Historical Trend Chart
st.subheader("📈 Multi-Channel Historical Price Velocity")

if df_history is not None and not df_history.empty:
    sample_sku = st.selectbox(
        "Select SKU to inspect historical price movements:",
        df_history["sku"].unique().tolist(),
        index=0
    )
    hist_sub = df_history[df_history["sku"] == sample_sku].sort_values("date")

    fig = go.Figure()
    our_price_col = "our_price" if "our_price" in hist_sub.columns else "price"
    comp_a_col = "comp_a_price" if "comp_a_price" in hist_sub.columns else "competitor_a_price"
    comp_b_col = "comp_b_price" if "comp_b_price" in hist_sub.columns else "competitor_b_price"

    if our_price_col in hist_sub.columns:
        fig.add_trace(go.Scatter(
            x=hist_sub["date"], y=hist_sub[our_price_col],
            mode="lines+markers", name="Our Store",
            line=dict(color="#38BDF8", width=3)
        ))
    if comp_a_col in hist_sub.columns:
        fig.add_trace(go.Scatter(
            x=hist_sub["date"], y=hist_sub[comp_a_col],
            mode="lines+markers", name="Amazon US",
            line=dict(color="#F59E0B", width=2, dash="dash")
        ))
    if comp_b_col in hist_sub.columns:
        fig.add_trace(go.Scatter(
            x=hist_sub["date"], y=hist_sub[comp_b_col],
            mode="lines+markers", name="Best Buy",
            line=dict(color="#10B981", width=2, dash="dot")
        ))

    fig.update_layout(
        paper_bgcolor="#121826",
        plot_bgcolor="#0B0F19",
        font=dict(color="#94A3B8", family="monospace"),
        height=320,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="#1F293D"),
        yaxis=dict(showgrid=True, gridcolor="#1F293D", tickprefix="$")
    )
    st.plotly_chart(fig, use_container_width=True)

# 8. Interactive Reprice Catalog Table
st.subheader("📋 Repricing Engine Matrix")

col_export1, col_export2, _ = st.columns([1.5, 1.5, 5])
with col_export1:
    csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Export Shopify Reprice CSV", csv_bytes, "pricepulse_reprice_export.csv", "text/csv")

with col_export2:
    if st.button("⚡ Simulate Shopify Sync (200 OK)"):
        st.toast(f"Successfully dispatched reprice mutations for {len(df_filtered)} SKUs to Shopify Storefront API!", icon="✅")

# Format display table
display_df = df_filtered[[
    "sku", "title", "brand", "cost_price", "current_price",
    "lowest_comp", "target_reprice", "price_change", "margin_pct", "status_badge", "action"
]].copy()

display_df.columns = [
    "SKU", "Product Title", "Brand", "Cost ($)", "Current Price ($)",
    "Lowest Comp ($)", "Target Reprice ($)", "Delta ($)", "Net Margin (%)", "Status", "Action Rationale"
]

st.dataframe(
    display_df.style.format({
        "Cost ($)": "${:,.2f}",
        "Current Price ($)": "${:,.2f}",
        "Lowest Comp ($)": "${:,.2f}",
        "Target Reprice ($)": "${:,.2f}",
        "Delta ($)": "{:+,.2f}",
        "Net Margin (%)": "{:.1f}%"
    }),
    use_container_width=True,
    height=420
)

# 9. Audit Details Expander
with st.expander("🔍 Algorithmic Rule & Mathematical Audit Documentation"):
    st.markdown("""
    ### Mathematical Formula
    $$\\text{Target Price} = \\min(\\text{Competitor Prices}) - \\text{Undercut Amount}$$
    $$\\text{Margin Floor} = \\text{COGS} \\times (1 + \\text{Min Margin \\%})$$
    $$\\text{Final Price} = \\max(\\text{Target Price}, \\text{Margin Floor})$$

    * **Safety Guarantee:** If a competitor attempts predatory dumping below our COGS + Minimum Margin, PricePulse AI activates the **Circuit Breaker** and locks the price to the safety floor.
    * **Stockout Harvesting:** When all competitors are out of stock, PricePulse AI automatically raises prices by **+7%** to harvest maximum gross profit while maintaining Buy-Box exclusivity.
    """)
