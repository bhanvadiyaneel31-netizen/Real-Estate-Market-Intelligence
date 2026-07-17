# Architecture.md — Real Estate Market Intelligence Platform

## 1. High-Level Flow
```
Scraper → Raw Store (DB) → Cleaner/ETL → Feature Store (DB) → Model Training
   → Model Registry (saved models + metrics) → FastAPI → React Dashboard
                                                    ↑
                                              Scheduler (retrain/rescrape)
```

## 2. Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| Scraping | `requests` + `BeautifulSoup`; `Selenium` only if a page requires JS rendering | Prefer static scraping first |
| Backend language | Python 3.11+ | Type-hinted throughout |
| Database | PostgreSQL via SQLAlchemy (or MongoDB if data stays semi-structured) | Raw + cleaned tables separated |
| ETL / feature engineering | `pandas`, custom `Cleaner` / `FeatureEngineer` classes | No feature logic inline in scripts |
| ML | `scikit-learn` (Linear, Ridge, Lasso, Logistic, Decision Tree, Random Forest, SVM, Naive Bayes, KNN), `xgboost` | One `Predictor` interface, models swappable |
| API | FastAPI + Pydantic schemas | Async endpoints |
| CLI | `click` | `scrape`, `clean`, `train`, `predict`, `serve` commands |
| Scheduler | APScheduler | Runs scrape + retrain jobs |
| Testing | `pytest` | Unit tests per module |
| Frontend | React + TypeScript | See below |
| Frontend data layer | TanStack Query (React Query) | Caching, loading/error states |
| Frontend charts | Recharts | Market trend + model comparison charts |
| Frontend forms | React Hook Form + Zod | Price predictor input validation |
| Frontend styling | Tailwind CSS | |
| Deployment | Docker + Railway/Render (backend), Vercel/Netlify (frontend) | |
| Config/secrets | `.env` + `python-dotenv`; never hardcoded | |
| Logging | Python `logging` module, structured, no `print()` | |

## 3. Backend Folder Structure
```
backend/
  app/
    api/                # FastAPI routers (predict.py, similar.py, trends.py, metrics.py)
    core/                # config.py, logging.py
    db/                  # models (SQLAlchemy), session, migrations
    scraper/             # Scraper class(es), one per source site
    etl/                 # Cleaner, FeatureEngineer classes
    ml/
      models/            # one module per model, shared BaseModel interface
      registry.py         # loads/saves trained models + metrics
      predictor.py         # unified predict interface used by API
    cli/                  # click commands
    scheduler/            # APScheduler jobs
  tests/                  # mirrors app/ structure
  requirements.txt / pyproject.toml
  Dockerfile
  .env.example
```

## 4. Frontend Folder Structure
```
frontend/
  src/
    api/        # typed API client functions
    components/  # PredictorForm, PriceCard, ModelComparisonChart, ListingTable
    pages/       # Overview, Predictor, Explorer, ModelComparison
    hooks/       # usePrediction, useListings, useModelMetrics
    types/       # TS interfaces mirroring backend Pydantic schemas
  package.json
```

## 5. Data Flow Contracts
- Raw listings table: one row per scrape per listing (keeps history).
- Cleaned/feature table: one row per listing, engineered features only, versioned by `feature_set_version`.
- Model registry: each trained model saved with metadata — algorithm name, training date, metrics (MAE/RMSE for regressors, F1/accuracy for classifiers), feature set version used.
- API responses always include which model produced a prediction, so the dashboard's "Model Comparison" and "Price Predictor" toggle stay consistent with what's actually in the registry.

## 6. Model-to-Task Mapping (for implementers)
| Task | Models |
|---|---|
| Price estimate (regression) | Linear, Ridge, Lasso, Random Forest, XGBoost |
| Under-market value (binary classification) | Logistic Regression |
| Price-tier classification | SVM |
| Explainable price factors | Decision Tree |
| Description text classification | Naive Bayes |
| Similar-property retrieval | KNN |
