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
Phase 2 — Scraper

## Completed
- Phase 1 — Project Setup (FastAPI scaffolding, config loader, structured logs, tests, Vite React + TS + Tailwind v3 scaffold, folder structure)

## In Progress
- (none)

## Next Steps
- Implement SQLite/PostgreSQL database structures & SQLAlchemy schema in `backend/app/db/`
- Build the `Scraper` class for real estate listings
- Implement CLI command: `cli scrape`

## Key Decisions Log
| Date | Decision | Reason |
|---|---|---|
| 2026-07-13 | Python 3.11 installed | Satisfy environment execution guidelines. |
| 2026-07-13 | Strict TypeScript mode enabled | Added `"strict": true` manually to both `tsconfig.app.json` and `tsconfig.node.json` to enforce strict type checking. |
| 2026-07-13 | Added uvicorn & httpx to requirements.txt | Uvicorn is required for serving FastAPI; HTTPX is required for testing. |

## Known Issues / Blockers
- (none yet)

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
