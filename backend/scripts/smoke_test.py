import sys
import time
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)


def auth_headers() -> dict[str, str]:
    suffix = int(time.time())
    signup = c.post(
        "/auth/signup",
        json={
            "name": "Admin User",
            "email": f"admin.{suffix}@northstar.example",
            "password": "password123",
            "organization_name": "Northstar",
            "organization_slug": f"northstar-{suffix}",
            "role": "admin",
            "team": "platform",
            "level": "senior",
            "manager_name": "CTO",
            "start_date": "2026-04-01",
        },
    )
    assert signup.status_code == 201, signup.text
    token = signup.json()["access_token"]
    org_id = signup.json()["organization_id"]
    user_id = signup.json()["user_id"]
    return {"Authorization": f"Bearer {token}"}, org_id, user_id


headers, org_id, _admin_user_id = auth_headers()

# 1. Create user (backend_engineer on payments)
resp = c.post("/users", json={
    "name": "Ada Lovelace",
    "email": "ada@northstar.example",
    "role": "backend_engineer",
    "team": "payments",
    "level": "mid",
    "manager_name": "Grace Hopper",
    "start_date": "2026-04-01",
}, headers=headers)
assert resp.status_code == 201, resp.text
user = resp.json()
uid = user["id"]
print(f"Created user {uid}: {user['name']}, role={user['role']}, team={user['team']}")
print(f"Auto-seeded access statuses: {[a['tool_name'] for a in user['access_statuses']]}")

# 2. Update one access status
resp2 = c.post(
    f"/users/{uid}/access",
    json={"tool_name": "github", "status": "pending", "notes": "invite sent"},
    headers=headers,
)
assert resp2.status_code == 201, resp2.text
print(f"Updated github access -> {resp2.json()['status']}")

# 3. List access statuses
resp3 = c.get(f"/users/{uid}/access", headers=headers)
assert resp3.status_code == 200
print(f"Access list: {[(a['tool_name'], a['status']) for a in resp3.json()]}")

# 4. Generate personalized plan
resp4 = c.post(f"/users/{uid}/plan/generate", headers=headers)
assert resp4.status_code == 200, resp4.text
plan_info = resp4.json()
print(f"Plan: {plan_info['message']}, task_count={plan_info['generated_task_count']}")

# 5. Get plan tasks with dependency info
resp5 = c.get(f"/users/{uid}/plan", headers=headers)
assert resp5.status_code == 200
tasks = resp5.json()
for t in tasks:
    dep = t.get("depends_on_task_id")
    print(f"  [{t['priority']}] {t['task_name']}  (dep={dep}, doc={t['doc_reference']})")

# 6. Test idempotency
resp6 = c.post(f"/users/{uid}/plan/generate", headers=headers)
assert resp6.json()["generated_task_count"] == 0
print(f"Idempotent re-gen: {resp6.json()['message']}")

# 7. Auto-classify blocker + recommendation
first_task_id = tasks[0]["id"]
blocker_resp = c.post(
    f"/users/{uid}/blockers",
    json={
        "task_id": first_task_id,
        "description": "I cannot access the payments repo and no invite has arrived yet.",
        "severity": "high",
    },
    headers=headers,
)
assert blocker_resp.status_code == 201, blocker_resp.text
blocker_body = blocker_resp.json()
print(
    "Blocker classification:",
    blocker_body["blocker_type"],
    "| reason:",
    blocker_body["classification_reason"],
)
print("Recommended action:", blocker_body["recommended_action"])
print("Alternate tasks:", blocker_body["alternate_tasks"])

progress_resp = c.get(f"/users/{uid}/progress", headers=headers)
assert progress_resp.status_code == 200, progress_resp.text
progress = progress_resp.json()
assert progress["recommended_next_action"], "Expected recommended_next_action in progress"
assert progress["recommended_alternate_tasks"], "Expected alternate tasks in progress"
assert progress["blocked_tasks"] >= 1, "Expected blocked count to increase after blocker creation"
print("Progress recommendation:", progress["recommended_next_action"])

# 8. Escalation draft routing + content
esc_resp = c.post(
    f"/users/{uid}/escalation-draft",
    json={
        "blocker_id": blocker_body["id"],
        "channel": "slack",
        "what_tried": ["Checked GitHub invite email", "Verified org visibility in GitHub"],
    },
    headers=headers,
)
assert esc_resp.status_code == 200, esc_resp.text
esc = esc_resp.json()
assert esc["recipient_team"] == "developer_productivity"
assert esc["destination"] == "developer-productivity"
assert "Help needed" in esc["draft_message"]
print("Escalation draft routed to:", esc["recipient_owner"], "via", esc["destination"])

# 9. Frontend engineer gets different plan
resp7 = c.post("/users", json={
    "name": "Bob Frontend",
    "email": "bob@northstar.example",
    "role": "frontend_engineer",
    "team": "payments",
    "level": "junior",
    "manager_name": "Grace Hopper",
    "start_date": "2026-04-01",
}, headers=headers)
uid2 = resp7.json()["id"]
c.post(f"/users/{uid2}/plan/generate", headers=headers)
tasks2 = c.get(f"/users/{uid2}/plan", headers=headers).json()
print(f"Frontend engineer tasks ({len(tasks2)}):")
for t in tasks2:
    print(f"  [{t['priority']}] {t['task_name']}")

# 10. QA engineer gets fallback plan (no template for qa_engineer on payments)
resp8 = c.post("/users", json={
    "name": "Carol QA",
    "email": "carol@northstar.example",
    "role": "qa_engineer",
    "team": "payments",
    "level": "mid",
    "manager_name": "Grace Hopper",
    "start_date": "2026-04-01",
}, headers=headers)
uid3 = resp8.json()["id"]
c.post(f"/users/{uid3}/plan/generate", headers=headers)
tasks3 = c.get(f"/users/{uid3}/plan", headers=headers).json()
print(f"QA engineer fallback tasks ({len(tasks3)}):")
for t in tasks3:
    print(f"  [{t['priority']}] {t['task_name']}")

print("\nAll smoke tests passed.")

# 11. Validate org manager endpoints
org_dash = c.get(f"/organizations/{org_id}/dashboard", headers=headers)
assert org_dash.status_code == 200, org_dash.text
print("Org dashboard:", org_dash.json())
