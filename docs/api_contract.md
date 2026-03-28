# API Contract (V1)

Base URL: `http://127.0.0.1:8000`

## Users

### `POST /users`

Create a new onboarding profile.

Request body:

```json
{
  "name": "Ada Lovelace",
  "email": "ada@northstar.example",
  "role": "backend_engineer",
  "team": "payments",
  "level": "mid",
  "manager_name": "Grace Hopper",
  "start_date": "2026-04-01"
}
```

Response:

- user profile fields
- auto-seeded `access_statuses` based on role requirements

### `GET /users/{user_id}`

Get a user profile and current access statuses.

## Access

### `POST /users/{user_id}/access`

Upsert access status for a specific tool.

Request body:

```json
{
  "tool_name": "github",
  "status": "pending",
  "notes": "Invite not received yet"
}
```

### `GET /users/{user_id}/access`

List all access rows for a user.

## Plan

### `POST /users/{user_id}/plan/generate`

Generate personalized tasks from role/team templates.

Behavior:

- idempotent: no duplicate generation if tasks already exist
- resolves template dependency names into `depends_on_task_id`

### `GET /users/{user_id}/plan`

Get generated tasks for a user.

## Chat (RAG)

### `POST /users/{user_id}/chat`

Retrieve and answer onboarding questions with source citations.

Request body:

```json
{
  "message": "I cannot access the repo. What should I do next?"
}
```

Response body:

```json
{
  "user_id": 1,
  "response": "For your role ...",
  "sources": ["github_access_guide.md", "who_to_contact.md"]
}
```

## Blockers

### `POST /users/{user_id}/blockers`

Create and classify blocker.

Request body:

```json
{
  "task_id": 12,
  "description": "Cannot access payments repo and no invite arrived",
  "severity": "high"
}
```

Notes:

- `blocker_type` is optional; auto-inferred if omitted
- response includes:
  - `classification_reason`
  - `recommended_action`
  - `alternate_tasks`

## Tasks

### `PATCH /tasks/{task_id}`

Update task status and/or notes.

## Progress

### `GET /users/{user_id}/progress`

Return progress summary:

- total/completed/blocked/pending task counts
- `current_blocker`
- `recommended_next_action`
- `recommended_alternate_tasks`

## Escalation

### `POST /users/{user_id}/escalation-draft`

Generate escalation draft routed to correct owner/team.

Request body:

```json
{
  "blocker_id": 5,
  "channel": "slack",
  "what_tried": ["Checked invite email", "Verified org visibility"],
  "help_needed": "Please resend invite and confirm team mapping"
}
```

Response body:

```json
{
  "user_id": 1,
  "blocker_id": 5,
  "channel": "slack",
  "recipient_team": "developer_productivity",
  "recipient_owner": "Maya Brooks",
  "destination": "developer-productivity",
  "draft_message": "Hi @Maya Brooks, I need help ..."
}
```

