# Rules.md — Boundaries for AI-Assisted Development

## 1. Libraries — Use
- Backend: `fastapi`, `pydantic`, `sqlalchemy`, `pandas`, `scikit-learn`, `xgboost`, `click`, `apscheduler`, `pytest`, `python-dotenv`, `requests`, `beautifulsoup4`
- Frontend: `react`, `typescript`, `@tanstack/react-query`, `recharts`, `react-hook-form`, `zod`, `tailwindcss`, `axios`

## 2. Libraries — Avoid
- No `Flask` mixed into the same service as FastAPI (pick one backend framework).
- No `Selenium` unless a target site genuinely requires JS rendering — try static scraping first.
- No raw SQL strings scattered through business logic — use SQLAlchemy models/queries.
- No `localStorage`/`sessionStorage` in the dashboard for anything that needs to persist — use the backend DB.
- No jQuery, no class-component React — functional components + hooks only.
- No committing `.env` files or API keys to version control.

## 3. Error Handling
- Backend: every API endpoint wraps DB/model calls in try/except, returns proper HTTP status codes (400 for bad input, 404 for missing resource, 500 with a generic message for unexpected errors — never leak stack traces to the client).
- Scraper: must not crash on a single malformed listing — log and skip, continue the batch.
- ML pipeline: if a model fails to train, log the failure and continue training the remaining models rather than aborting the whole run.
- Frontend: every data-fetching hook must handle loading, error, and empty states explicitly — no silent failures.

## 4. Coding Standards
- Python: PEP 8, type hints on all function signatures, docstrings on public classes/functions.
- One class per responsibility (Scraper, Cleaner, FeatureEngineer, Predictor, ModelRegistry) — no god-classes or god-scripts.
- TypeScript: strict mode on, no `any` unless justified with a comment.
- Every new module gets at least one corresponding `pytest` test file before being considered "done."

## 5. What the AI Should Do
- Follow Phases.md order — do not jump ahead to a later phase before the current one's tasks are checked off in Memory.md.
- Ask before introducing a new library not listed in Architecture.md.
- Keep functions small and single-purpose; refactor rather than let files balloon.
- Update Memory.md at the end of every work session with what changed and what's next.

## 6. What the AI Should Not Do
- Do not hardcode credentials, URLs, or file paths — use config/`.env`.
- Do not silently change the model list, folder structure, or API contract defined in Architecture.md — flag the reasoning if a change seems necessary.
- Do not generate placeholder/fake data and present it as if it were scraped real data.
- Do not skip writing tests "to save time."
- Do not delete or rewrite Memory.md's history — append/update status, don't erase prior context.
