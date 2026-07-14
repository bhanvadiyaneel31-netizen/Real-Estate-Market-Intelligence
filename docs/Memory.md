# Memory.md — Build Progress Log

> Not created at project start. Start filling this in once coding begins. Update it at the end of every work session (or every AI coding session) so a new chat/tool can pick up context instantly instead of re-reading the whole codebase or guessing.

## How to Use This File
- Keep entries short and factual — status, not narrative.
- Always update **Current Phase**, **Completed**, and **Next Steps** before ending a session.
- Log **Key Decisions** any time you deviate from Architecture.md/Rules.md/Phases.md, with the reason.
- Log **Known Issues** so they aren't silently rediscovered later.
- Never delete history — append new entries below old ones.

---

## Current Phase
Phase 3 — ETL / Feature Engineering

## Completed
- Phase 1 — Project Setup (FastAPI scaffolding, config loader, structured logs, tests, Vite React + TS + Tailwind v3 scaffold, folder structure)
- Phase 2 — Scraper (Ames Housing local sandbox server, web crawler with pagination, rate-limiting, and DB raw log storage, Click CLI command, mock unit tests)

## In Progress
- Phase 3 — ETL / Feature Engineering (Cleaner, FeatureEngineer, featured_listings table, CLI integration, and unit tests)

## Next Steps
- Implement `Cleaner` class to clean raw values (types coercion, missing entries, outliers)
- Implement `FeatureEngineer` class (neighborhood, price per sqft, text feature extraction, is_below_market_value)
- Create versioned cleaned features database table `featured_listings`
- Add the `cli clean` command to execute the ETL pipeline
- Write and run unit tests for the ETL pipeline
- **Critical Action Before Phase 4**: Re-run the full scrape (with limit high enough, e.g. 3000, to capture all ~2,930 Ames records) and re-run `cli clean` to generate a proper versioned feature set for training. The 50-row smoke test database is only for verifying code execution and is too noisy/small for neighborhood median target and model training.

## Key Decisions Log
| Date | Decision | Reason |
|---|---|---|
| 2026-07-13 | Python 3.11 installed | Satisfy environment execution guidelines. |
| 2026-07-13 | Strict TypeScript mode enabled | Added `"strict": true` manually to both `tsconfig.app.json` and `tsconfig.node.json` to enforce strict type checking. |
| 2026-07-13 | Added uvicorn & httpx to requirements.txt | Uvicorn is required for serving FastAPI; HTTPX is required for testing. |
| 2026-07-13 | Switched to Local Scraping Sandbox (Ames Housing) | Avoids legal/ToS risks associated with Zillow, Redfin, or Craigslist. Uses authoritative public-domain JSE data served locally as static HTML, preserving realistic pagination, rate-limiting, and DOM-parsing tests. |
| 2026-07-13 | Switched local DB url to SQLite | Allows seamless local development without running local PostgreSQL servers. Dialect can be overridden via `.env`. |
| 2026-07-14 | Target renamed to `is_below_market_value` | The Ames dataset has no days-on-market field. We use a "priced below neighborhood median" flag as a proxy target with no real timing validation. |
| 2026-07-14 | City-wide median fallback for target | For neighborhoods with < 5 listings (e.g. Landmrk, GrnHill), the target is computed against the city-wide median price to avoid noisy/unreliable medians. |
| 2026-07-14 | Defer neighborhood encoding to Phase 4 | Storing location as raw string rather than integer; model-specific encoding (e.g. one-hot for linear/KNN, target/label for trees) avoids false ordinal relationships in linear/distance models. |
| 2026-07-14 | Exclude price/price_per_sqft from class features | Prevents data leakage since `is_below_market_value` is derived directly from price. |

## Known Issues / Blockers
- The Ames Housing dataset has no "days on market" (DOM) field. The "will-sell-in-30-days" classification task in Architecture.md relies on this. We resolved this by adopting the `is_below_market_value` target proxy (see Key Decisions).

## Session Log
### Session 1 — 2026-07-13
- What was done:
  - Created backend layout per Architecture.md and initialized python package structure.
  - Installed Python 3.11 and stood up backend virtualenv.
  - Implemented config loading via python-dotenv / Pydantic Settings, with strict type checking and validation failure tests.
  - Designed structured console logging mapping development/production formats.
  - Stood up FastAPI server with `/health` route and wrote test checks.
  - Scaffolded Vite React + TS + Tailwind v3 frontend and successfully completed compilation checks.
- What broke / had to be fixed:
  - System default python was 3.13, so had to install `python@3.11` via Homebrew first to isolate virtual environment.
  - Added TypeScript `"strict": true` config parameter manually, which was omitted by default Vite templates.
- What's left for next session:
  - Proceed with Phase 2 (Scraper module and database tables creation).

### Session 2 — 2026-07-13
- What was done:
  - Downloaded authoritative Ames Housing dataset from JSE.
  - Implemented `sandbox_server.py` serving static, paginated HTML index and detail pages from Ames data.
  - Built `AmesSandboxScraper` traversing pagination, managing retry backoffs, and parsing list/detail HTML elements.
  - Implemented RawListing SQLAlchemy database structures and click CLI commands (`sandbox`, `scrape`).
  - Created unit tests in `test_scraper.py` testing happy paths, network exceptions, and DB commits (6/6 passing backend tests).
  - Executed end-to-end local crawl of 10 listings and confirmed database records.
- What broke / had to be fixed:
  - Encountered a `StopIteration` test failure during pagination traversal: resolved by appending a final mock response for the trailing page in the tests.
  - Switched the local database URL from PostgreSQL to SQLite for developer environment setup convenience.
- What's left for next session:
  - Proceed with Phase 3 (ETL / Cleaner / FeatureEngineer).
