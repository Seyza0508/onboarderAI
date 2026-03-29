import sys
import time
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient

from app.main import app
from app.rag.ingestion import build_index


def main() -> None:
    build_index(force_rebuild=True)
    client = TestClient(app)
    suffix = int(time.time())

    signup = client.post(
        "/auth/signup",
        json={
            "name": "RAG Admin",
            "email": f"rag.admin.{suffix}@northstar.example",
            "password": "password123",
            "organization_name": "Rag Org",
            "organization_slug": f"rag-org-{suffix}",
            "role": "admin",
            "team": "platform",
            "level": "senior",
            "manager_name": "CTO",
            "start_date": "2026-04-03",
        },
    )
    assert signup.status_code == 201, signup.text
    headers = {"Authorization": f"Bearer {signup.json()['access_token']}"}

    user_resp = client.post(
        "/users",
        json={
            "name": "Rag Tester",
            "email": f"rag.tester.{suffix}@northstar.example",
            "role": "backend_engineer",
            "team": "payments",
            "level": "mid",
            "manager_name": "Grace Hopper",
            "start_date": "2026-04-03",
        },
        headers=headers,
    )
    assert user_resp.status_code == 201, user_resp.text
    user_id = user_resp.json()["id"]

    question = "I cannot access the repo and I need to know what to do next."
    chat_resp = client.post(f"/users/{user_id}/chat", json={"message": question}, headers=headers)
    assert chat_resp.status_code == 200, chat_resp.text
    body = chat_resp.json()
    assert body["sources"], "Expected at least one source citation"
    assert "github_access_guide.md" in body["sources"] or "who_to_contact.md" in body["sources"]

    print("RAG smoke test passed.")
    print("Sources:", body["sources"])
    print("Response preview:", body["response"][:220], "...")


if __name__ == "__main__":
    main()
