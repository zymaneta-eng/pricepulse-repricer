# 📜 Core Engineering Standards & Upwork Portfolio Rules

> **Status:** MANDATORY COMPLIANCE ACROSS ALL FREELANCE PROJECTS  
> **Target Audience:** Upwork Enterprise Clients, CTOs, Technical Reviewers  

---

## 1. 🚫 Zero Hardcode & Ground-Truth Strictness
1. **Never mock real data:** No fake prices, no hardcoded synthetic emails (`test@test.com`), no fake company names. All records must originate from public, authentic, verifiable endpoints.
2. **Public Data Compliance:** Only collect and display information that is intentionally published in open access (official corporate domains, public government registers, open catalog feeds, JSON-LD schemas, sitemaps).
3. **No Private/Gated Scraping:** Never crawl behind authentication, user walls, or private Facebook/LinkedIn accounts. Only parse publicly indexable web surfaces.
4. **Verifiable URLs (HTTP 200 OK):** Every single link, image, or reference in the application must return a live `200 OK` status. Zero 404 dead links or placeholder mirrors.

---

## 2. 🛡️ Anti-Bot & Network Architecture (2026 Industry Standard)
1. **No Outdated Heavy Selenium/Puppeteer for HTTP APIs:**
   * Modern websites use TLS fingerprinting (JA3/JA4) and behavioral WAFs (Cloudflare Turnstile, DataDome, Akamai).
   * Primary extraction engine must use **`curl-cffi` with Chrome impersonation (`chrome120`+)** or stealth Playwright only when JavaScript execution is strictly required.
2. **Respectful & Resilient Extraction:**
   * Dynamic user-agent and header management (`Accept-Language`, `sec-ch-ua`).
   * Concurrent rate-limiting via `asyncio.Semaphore` to protect host targets from DDoS-like patterns.
   * Graceful fallback when an endpoint is temporarily rate-limited.

---

## 3. 🔍 Product Matching & Data Reconciliation (E-Commerce Standard)
1. **Global Identifiers First:**
   * Primary matching must always rely on international standard identifiers: **UPC**, **EAN-13**, **GTIN**, **ISBN**, or platform-native IDs like **Amazon ASIN**.
2. **Probabilistic / Fuzzy Matching with Confidence Scoring:**
   * Real e-commerce titles differ across merchants (e.g., `"Sony WH-1000XM5 Black"` vs `"Sony WH1000XM5/B Noise Cancelling Headset"`).
   * Implement token-sort ratio / Levenshtein distance with an explicit **Match Confidence Score (0–100%)**.
   * Products below the safe threshold (<80%) must be flagged for human review, never blindly repriced.
3. **Variant-Level Granularity:**
   * Always account for variants (SKU, Color, Size, Storage). Prices must never be mapped from a 128GB version to a 512GB version.

---

## 4. 🎨 Design Language & UX Ergonomics (Linear × Clay Standard)
1. **Zero Empty Spaces or Dead UI Elements:**
   * Compact, cohesive horizontal top-down layout without bulky useless vertical sidebars.
   * Background foundation: Dark Slate `#0B0F17`, elevated card surfaces `#121826`, crisp 1px borders `#1F2937`.
   * High-contrast typography using Inter. Strictly zero oversized or misaligned containers.
2. **Live Telemetry & Instant Actions:**
   * Prominent KPI summary cards at the top (Tracked Items, Spreads, Confidence, Margin Impact).
   * Interactive sorting, filtering, and time-series charting (Plotly).
   * One-click export strictly matching standard ecosystem formats (e.g., official Shopify CSV Import schema).

---

## 5. 📦 Code Quality & Portability (Self-Contained Deployment)
1. **Completely Self-Contained:**
   * Zero hardcoded local machine paths (`C:\Users\...`). Use `Path(__file__).resolve().parent`.
   * Strict `requirements.txt` with pinned compatible versions.
   * One-click local launch and instant Streamlit Cloud deployability with zero configuration overhead.
2. **Production-Ready Logging & Error Boundaries:**
   * All scraping, matching, and calculations must be wrapped in structured try/except blocks with meaningful toast/UI notifications instead of raw stack traces.
