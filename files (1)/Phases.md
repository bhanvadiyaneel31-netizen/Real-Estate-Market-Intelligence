# Phases.md — Build Plan

Work through phases in order. Do not start a phase until the previous one's checklist is complete in Memory.md.

## Phase 1 — Project Setup
- Repo structure (backend/ + frontend/) per Architecture.md
- Virtual env, requirements.txt / package.json
- `.env.example`, config loading, logging setup
- Empty FastAPI app running with a health-check endpoint

## Phase 2 — Scraper
- Build `Scraper` class for one listing source
- Store raw listings in DB (raw table)
- Handle pagination, rate-limiting, malformed listings (skip + log)
- CLI command: `cli scrape`

## Phase 3 — ETL / Feature Engineering
- `Cleaner` class: handle missing values, outliers, type coercion
- `FeatureEngineer` class: price/sqft, location encoding, text features from descriptions
- Write cleaned+featured data to feature table, versioned
- CLI command: `cli clean`

## Phase 4 — Model Training (all 8 models)
- Shared `BaseModel` interface (fit/predict/evaluate)
- Implement and train: Linear, Ridge, Lasso, Logistic, Decision Tree, Random Forest, XGBoost, SVM, Naive Bayes, KNN — per the task mapping in Architecture.md
- Log metrics (MAE/RMSE or F1/accuracy) per model to the registry
- CLI command: `cli train`

## Phase 5 — FastAPI Backend
- `/predict`, `/similar-properties`, `/market-trend`, `/model-metrics` endpoints
- Pydantic request/response schemas
- Error handling per Rules.md
- Basic pytest coverage for each endpoint

## Phase 6 — CLI Completion
- `cli predict` (test predictions from terminal)
- `cli serve` (run the API)

## Phase 7 — Scheduler
- APScheduler job: rescrape + retrain on a set interval
- Logs each scheduled run's outcome

## Phase 8 — React Dashboard
- Typed API client + TS types mirroring backend schemas
- Pages: Market Overview, Price Predictor, Similar Properties, Model Comparison, Listing Explorer
- Loading/error states, responsive layout

## Phase 9 — Testing Pass
- Backend: pytest coverage for scraper, ETL, ML, API
- Frontend: at least smoke tests for key components

## Phase 10 — Deployment
- Dockerfile for backend
- Deploy backend (Railway/Render) and frontend (Vercel/Netlify)
- Confirm scheduled retrain works in the deployed environment

## Phase 11 — Polish / Portfolio Packaging
- README with architecture diagram, screenshots, model comparison table
- Short write-up: problem, approach, results, tradeoffs
