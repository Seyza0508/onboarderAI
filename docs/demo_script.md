# Demo Script (5-8 minutes)

## Objective

Show that OnboardAI behaves like an agentic onboarding coordinator, not a generic chatbot.

## Setup

Run:

```bash
python backend/scripts/init_db.py
python backend/scripts/ingest_docs.py
uvicorn backend.app.main:app --reload
cd frontend
npm install
npm run dev
```

## Flow

## 1) Intake and context memory

On `http://localhost:3000/intake`:

- Create profile for:
  - role: `backend_engineer`
  - team: `payments`
  - start date: current/future date
- Submit form and generate plan.

Callout:

- system persists user context
- access statuses are initialized and tracked

## 2) Personalized plan generation

Open dashboard and load user ID.

Callout:

- plan is role/team-specific
- tasks include categories, priorities, and dependencies

## 3) Retrieval-grounded assistance

Open assistant page and ask:

- "I cannot access the repo, what should I do?"

Callout:

- response includes source citations from onboarding docs
- advice is personalized to role/team context

## 4) Blocker intelligence and adaptation

Create blocker via API docs (`/docs`) or scripted flow:

- description with access issue

Callout:

- blocker is auto-classified (`access`)
- reason and next-best-action are generated
- alternate productive tasks are suggested while waiting

## 5) Escalation drafting

Generate escalation draft for current blocker.

Callout:

- routes to correct owner/team using contact directory
- generates Slack/email style message with:
  - what is blocked
  - what has been tried
  - what help is needed

## 6) Dashboard summary

Show:

- total/completed/blocked/pending counts
- current blocker
- recommended next action
- alternate tasks

## Key talking points

- stateful onboarding memory across interactions
- deterministic + retrieval-grounded decisioning
- clear adaptation loop: blocker -> recommendation -> escalation -> continued progress
- practical architecture that can scale to LangGraph orchestration and enterprise integrations

