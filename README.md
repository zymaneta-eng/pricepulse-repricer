# ⚡ PricePulse AI v3.5 | Algorithmic Retail Arbitrage & Margin Defense Terminal

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Shopify GraphQL](https://img.shields.io/badge/Shopify-GraphQL%20Admin%20API-95BF47?style=flat&logo=shopify&logoColor=white)](https://shopify.dev/)
[![TLS/JA3 Resilient](https://img.shields.io/badge/Engine-TLS%2FJA3%20Bypass-06B6D4?style=flat)](https://curl-cffi.readthedocs.io/)
[![Tailwind CSS](https://img.shields.io/badge/UI-Tailwind%20%2B%20Lucide-0EA5E9?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)

An ultra-modern, high-fidelity algorithmic e-commerce repricing workstation UI (Bloomberg Terminal + Keepa hybrid in dark mode) designed for high-volume retail arbitrage, Amazon/Shopify margin defense, and automated Buy-Box recapture.

---

## 🎯 Executive Overview

Off-the-shelf SaaS repricers charge heavy monthly subscriptions while locking merchants into rigid rules. They blindly chase competitor price drops into margin-negative territory, fail against Cloudflare/Akamai bot detection during peak events, and trigger false-positive undercuts against refurbished inventory.

**PricePulse AI Terminal** solves this by delivering an autonomous, proprietary trading desk:
1. **Resilient Data Ingestion:** Asynchronous pipeline utilizing `curl-cffi` with browser TLS fingerprinting (JA3/JA4 impersonation) to bypass Cloudflare Turnstile and retail WAFs with sub-50ms sync cycles.
2. **Deterministic EAN-13 & AI Semantic Guard:** 100% barcode matching coupled with LLM condition validation (`Brand New | Zero Hallucination`), preventing accidental matching against refurbished competitor stock.
3. **Gross Margin Safety Floor:** Mathematical repricing algorithms that guarantee sales never dip below merchant cost floors, with automated stockout price surge triggers pushed via Shopify GraphQL mutations.

---

## 🖥️ Workstation Architecture & Features

### 1. Header & Live Telemetry Ticker
- **Navigation Bar:** Live status badges (`🟢 Live API Grounded`, `Fuzzy Matcher: Active`, `🛠️ Simulation: ACTIVE`), settings, and instant deploy triggers.
- **Continuous Arbitrage Ticker Tape:** Real-time ticker streaming market movements (`AAPL-5s: Competitor Drop -$8.50 🔻 Win Buy-Box $191.49`, `Sony XM5: BestBuy Sold Out 🔺 Surge +8%`).

### 2. Strategy & Parameter Strip
- **Safety Margin Floor %:** Configurable cost-floor defense (e.g., 15%).
- **Buy-Box Undercut Offset:** Dynamic delta (e.g., -$0.50) to reclaim the #1 buy-box.
- **Stockout Surge %:** Automatically ramps prices when competitors deplete inventory.
- **Execution Triggers:** Sandbox Shopify GraphQL mutation push and Slack webhook alerts.

### 3. Responsive Flex Dual-Panel Workstation
- **Left Panel (65%):**
  - **30-Day Market Defense Chart:** Chart.js trend analysis comparing Our Price, Amazon US, BestBuy, and the Protected Margin Floor.
  - **High-Density Catalog Registry Table:** Financial data-grid with dedicated checkbox column, no-wrap SKU badges, 7-day sparkline charts, and multi-select bulk actions.
  - **Segmented View Switcher:** Seamlessly toggles between `[📈 Chart]`, `[📋 Catalog List]`, and `[⚡ Split]` views.
- **Right Panel (35% — AI Product Inspector):**
  - **Fuzzy Matching Engine:** High-resolution device miniatures with `100% EAN-13 Match` and `AI Semantic Guard` badges.
  - **Competitor Price Grid:** Instant spread comparison between COGS, Store Price, Amazon, and BestBuy.
  - **Strategic Decision Logic (AI Cognitive Guard):** Dynamic strategy breakdown with interactive `[ ✨ AI Rationale ]` popover explaining price velocity and stockout predictions.
  - **Permanently Anchored Execution Bar:** Dedicated `⚡ Run Repricer` action button pinned to the bottom of the dock.

---

## 🛠️ Tech Stack

- **Core Engine:** Python 3.11, Asyncio, Pydantic v2
- **Networking & Anti-Bot:** Curl-CFFI (TLS/JA3 impersonation), Residential Proxy Pools
- **Storefront Integration:** Shopify Admin GraphQL & REST API mutations
- **Frontend Workstation:** Tailwind CSS (Slate/Navy #0B0F19 palette), Lucide Icons, Chart.js
- **Presentation Layer:** Streamlit (full-width single-page responsive wrapper)

---

## 🚀 Quick Start

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/pricepulse-repricer.git
cd pricepulse-repricer
pip install -r requirements.txt
```

### 2. Run the Terminal
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501` to test the terminal.

---

## 💼 Developer Portfolio Attribution
Designed & Engineered by Freelancer • Available for Hire on Upwork for custom e-commerce automation, data pipelines, and trading terminal development.
