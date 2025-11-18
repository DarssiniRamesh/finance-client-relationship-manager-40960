import os
import tempfile

from fastapi.testclient import TestClient

# Ensure a fresh temporary sqlite DB for test isolation
tmpdir = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(tmpdir.name, 'test.db')}"
os.environ["DEV_AUTH_BYPASS"] = "true"  # not required for signup, but harmless

from src.api.main import app  # noqa: E402

client = TestClient(app)


def test_signup_creates_user_and_returns_201():
    payload = {"email": "newuser@example.com", "password": "strongpass123", "full_name": "New User"}
    r = client.post("/api/v1/auth/signup", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data and isinstance(data["id"], int)
    assert "created_at" in data and "updated_at" in data


def test_signup_duplicate_returns_409():
    payload = {"email": "dup@example.com", "password": "strongpass123", "full_name": "Dup User"}
    r1 = client.post("/api/v1/auth/signup", json=payload)
    assert r1.status_code == 201, r1.text
    r2 = client.post("/api/v1/auth/signup", json=payload)
    assert r2.status_code == 409, r2.text
    assert r2.json()["detail"] == "User already exists"
