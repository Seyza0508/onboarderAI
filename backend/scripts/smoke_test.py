import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)

# 1. Create user (backend_engineer on payments)
resp = c.post("/users", json={
    "name": "Ada Lovelace",
    "email": "ada@northstar.example",
    "role": "backend_engineer",
    "team": "payments",
    "level": "mid",
    "manager_name": "Grace Hopper",
    "start_date": "2026-04-01",
})
assert resp.status_code == 201, resp.text
user = resp.json()
uid = user["id"]
print(f"Created user {uid}: {user['name']}, role={user['role']}, team={user['team']}")
print(f"Auto-seeded access statuses: {[a['tool_name'] for a in user['access_statuses']]}")

# 2. Update one access status
resp2 = c.post(f"/users/{uid}/access", json={"tool_name": "github", "status": "pending", "notes": "invite sent"})
assert resp2.status_code == 201, resp2.text
print(f"Updated github access -> {resp2.json()['status']}")

# 3. List access statuses
resp3 = c.get(f"/users/{uid}/access")
assert resp3.status_code == 200
print(f"Access list: {[(a['tool_name'], a['status']) for a in resp3.json()]}")

# 4. Generate personalized plan
resp4 = c.post(f"/users/{uid}/plan/generate")
assert resp4.status_code == 200, resp4.text
plan_info = resp4.json()
print(f"Plan: {plan_info['message']}, task_count={plan_info['generated_task_count']}")

# 5. Get plan tasks with dependency info
resp5 = c.get(f"/users/{uid}/plan")
assert resp5.status_code == 200
tasks = resp5.json()
for t in tasks:
    dep = t.get("depends_on_task_id")
    print(f"  [{t['priority']}] {t['task_name']}  (dep={dep}, doc={t['doc_reference']})")

# 6. Test idempotency
resp6 = c.post(f"/users/{uid}/plan/generate")
assert resp6.json()["generated_task_count"] == 0
print(f"Idempotent re-gen: {resp6.json()['message']}")

# 7. Frontend engineer gets different plan
resp7 = c.post("/users", json={
    "name": "Bob Frontend",
    "email": "bob@northstar.example",
    "role": "frontend_engineer",
    "team": "payments",
    "level": "junior",
    "manager_name": "Grace Hopper",
    "start_date": "2026-04-01",
})
uid2 = resp7.json()["id"]
c.post(f"/users/{uid2}/plan/generate")
tasks2 = c.get(f"/users/{uid2}/plan").json()
print(f"Frontend engineer tasks ({len(tasks2)}):")
for t in tasks2:
    print(f"  [{t['priority']}] {t['task_name']}")

# 8. QA engineer gets fallback plan (no template for qa_engineer on payments)
resp8 = c.post("/users", json={
    "name": "Carol QA",
    "email": "carol@northstar.example",
    "role": "qa_engineer",
    "team": "payments",
    "level": "mid",
    "manager_name": "Grace Hopper",
    "start_date": "2026-04-01",
})
uid3 = resp8.json()["id"]
c.post(f"/users/{uid3}/plan/generate")
tasks3 = c.get(f"/users/{uid3}/plan").json()
print(f"QA engineer fallback tasks ({len(tasks3)}):")
for t in tasks3:
    print(f"  [{t['priority']}] {t['task_name']}")

print("\nAll smoke tests passed.")
