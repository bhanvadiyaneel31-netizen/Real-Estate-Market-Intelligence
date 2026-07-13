# PRD.md — Real Estate Market Intelligence Platform

## 1. Problem Statement
Home buyers, sellers, and agents lack an easy way to check whether a property's asking price is fair, or to see genuine market trends, without relying on opaque single-number estimates from listing sites. This project builds a transparent, explainable price-intelligence tool: it scrapes real listings, trains and compares multiple ML models, and serves predictions with a "why" breakdown through a live dashboard.

## 2. Purpose of This Project
Primary purpose: portfolio piece demonstrating **full-stack Python engineering** (scraping, ETL, OOP design, databases, APIs, CLI tooling, testing, deployment) combined with **applied ML** (8 classical models compared and productionized) — not just a Jupyter notebook.

## 3. Target Users
- **Primary (real):** Recruiters / hiring managers evaluating engineering + ML ability.
- **Secondary (product framing):** A hypothetical home buyer or agent checking if a listing is fairly priced, or exploring market trends in an area.

## 4. Core Features
1. **Scraper** — pulls active listings (price, area, location, bedrooms, amenities, description text) from a public listing source, on a schedule.
2. **ETL Pipeline** — cleans raw scraped data, handles missing values/outliers, engineers features (price/sqft, location encoding, text features from descriptions).
3. **Model Training & Comparison** — trains Linear, Ridge, Lasso, Logistic Regression, Decision Tree, Random Forest, XGBoost, SVM, Naive Bayes, and KNN on relevant sub-tasks (see Architecture.md), logs metrics for each.
4. **Prediction API (FastAPI)**
   - `POST /predict` — price estimate + confidence + top price-driving factors
   - `GET /similar-properties` — KNN-based nearest comparable listings
   - `GET /market-trend` — aggregate stats/trends by area and time
   - `GET /model-metrics` — comparison table of all trained models
5. **React Dashboard**
   - Market Overview (trend charts)
   - Price Predictor (input form → prediction + explanation)
   - Similar Properties (comparable listings)
   - Model Comparison (metrics table/chart)
   - Listing Explorer (searchable/filterable table)
6. **CLI Tooling** — trigger scrape / clean / train / predict without touching code.
7. **Scheduler** — periodic re-scrape and retrain (e.g. daily/weekly).

## 5. Non-Functional Requirements
- Runs entirely on free/open data sources and free-tier hosting.
- Reasonable response time for `/predict` (< 1s).
- Codebase readable and modular enough that a stranger (or an AI assistant) can pick it up mid-build using Memory.md.

## 6. Success Metrics
- All 8 models trained, evaluated, and comparable on a shared metrics table.
- End-to-end flow working: scrape → clean → train → API → dashboard, with no manual steps required after setup.
- At least one deployed, publicly viewable instance (backend + frontend).

## 7. Out of Scope (v1)
- User accounts / auth
- Payment processing or real transactions
- Mobile app (dashboard is web-only, responsive)
- Real-time scraping (batch/scheduled is sufficient)
