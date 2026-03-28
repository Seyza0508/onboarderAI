# OnboardAI - Agentic Developer Onboarding Assistant

OnboardAI is a portfolio project that demonstrates a practical, stateful, agentic AI system for engineering onboarding.

It helps new hires move from "day 1 confusion" to productive onboarding by combining profile context, plan generation, retrieval-grounded answers, blocker intelligence, escalation drafting, and progress tracking.

## Why this project is agentic

The system runs an explicit onboarding loop:

1. **Context**: captures role, team, level, manager, start date, and access status.
2. **Planning**: generates personalized onboarding tasks with dependencies.
3. **Action + tool/data use**: retrieves from onboarding docs and structured playbooks.
4. **Feedback**: records interactions, task status updates, and blockers.
5. **Adaptation**: classifies blockers, recommends next-best action, proposes alternate tasks, and drafts escalations.

This is intentionally more than a one-shot chatbot.

## Core features (V1)

- New hire profile setup and persisted onboarding context
- Personalized onboarding plan generation from role/team templates
- RAG-based onboarding Q&A with source citations
- Blocker detection and classification (`access`, `environment`, `documentation`, `dependency`, `ownership`)
- Next-best-action recommendation and alternate productive tasks
- Escalation draft generation with owner/team routing for Slack or email
- Progress dashboard with task counts, current blocker, and recommended action

## Tech stack

- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI, SQLAlchemy
- **Agent/workflow design**: modular service layer + stateful persistence (LangGraph-ready architecture)
- **RAG**: local ingestion + TF-IDF retrieval pipeline (embedding provider swappable)
- **Database**: SQLite
- **Storage**: local `storage/` artifacts (`app.db`, `rag_index.pkl`)

## Repository layout

```text
backend/     FastAPI API, DB models, services, RAG, scripts
frontend/    Next.js UI for intake, assistant chat, dashboard
data/        Structured and unstructured onboarding knowledge assets
storage/     Runtime artifacts (SQLite DB, RAG index)
docs/        Architecture notes, API contracts, demo script
```

## Quick start

## 1) Backend setup

```bash
python -m pip install -r backend/requirements.txt
python backend/scripts/init_db.py
python backend/scripts/ingest_docs.py
uvicorn backend.app.main:app --reload
```

Backend endpoints will be available at `http://127.0.0.1:8000`, docs at `http://127.0.0.1:8000/docs`.

## 2) Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at `http://localhost:3000`.

Use `frontend/.env.example` to override API URL if needed.

## Testing and smoke checks

Run from repo root:

```bash
python backend/scripts/init_db.py
python backend/scripts/ingest_docs.py
python backend/scripts/smoke_test.py
python backend/scripts/rag_smoke_test.py
```

These scripts validate:

- profile and access flows
- personalized plan generation
- blocker classification and progress recommendations
- escalation routing and draft generation
- retrieval-grounded chat with sources

## API highlights

Implemented endpoints:

- `POST /users`
- `POST /users/{user_id}/access`
- `GET /users/{user_id}/access`
- `GET /users/{user_id}`
- `POST /users/{user_id}/plan/generate`
- `GET /users/{user_id}/plan`
- `POST /users/{user_id}/chat`
- `POST /users/{user_id}/blockers`
- `PATCH /tasks/{task_id}`
- `GET /users/{user_id}/progress`
- `POST /users/{user_id}/escalation-draft`

## Demo story (short version)

1. Create a backend engineer profile on the payments team.
2. Auto-seed access status and generate role/team-specific onboarding plan.
3. Ask onboarding questions in chat and review cited sources.
4. Log an access blocker; system classifies it and recommends next action.
5. Generate a routed Slack escalation draft to the right owner.
6. Open dashboard to show progress metrics and alternate tasks while blocked.

## V1 vs future upgrades

### In V1 now

- single-user local deployment
- SQLite persistence
- retrieval with local vectorization and source-backed responses
- deterministic blocker/escalation logic from structured playbooks

### Good V2 extensions

- provider-swappable LLM answer synthesis
- Postgres + auth + multi-tenant org support
- LangGraph orchestration for explicit graph nodes/retries/handoff
- manager-level dashboard and onboarding risk scoring

## Documentation

- `docs/architecture.md`
- `docs/api_contract.md`
- `docs/demo_script.md`

