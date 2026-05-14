import json
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ── /health ───────────────────────────────────────────────────

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "running"}


# ── /analyze — failure cases ──────────────────────────────────

def test_analyze_without_token():
    response = client.post("/analyze", json={"query": "test"})
    assert response.status_code == 422  # FastAPI returns 422 for missing required header


def test_analyze_with_invalid_token(mocker):
    """When Supabase rejects the token, the API must return 401."""
    fake_response = MagicMock()
    fake_response.status_code = 401  # Supabase says: bad token
    mocker.patch("app.main.httpx.get", return_value=fake_response)

    response = client.post(
        "/analyze",
        json={"query": "test"},
        headers={"Authorization": "Bearer bad-token"},
    )
    assert response.status_code == 401


# ── /analyze — happy paths ────────────────────────────────────

def test_analyze_text_response(mock_supabase_user, mock_run_copilot, mocker):
    """Standard text response path."""
    mock_run_copilot.return_value = "## Here is your analysis"
    mocker.patch("app.main.save_history")  # silence the Supabase history write

    response = client.post(
        "/analyze",
        json={"query": "why did sales drop"},
        headers={"Authorization": "Bearer good-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "text"
    assert body["query"] == "why did sales drop"
    assert body["response"] == "## Here is your analysis"


def test_analyze_dashboard_response(mock_supabase_user, mock_run_copilot, mocker):
    """Dashboard path: run_copilot returns JSON, API must unwrap it."""
    mock_run_copilot.return_value = json.dumps({
        "type": "dashboard",
        "code": "function Dashboard() {}",
        "title": "Q4 Dashboard",
    })
    mocker.patch("app.main.save_history")

    response = client.post(
        "/analyze",
        json={"query": "show me a dashboard"},
        headers={"Authorization": "Bearer good-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "dashboard"
    assert body["dashboard_code"] == "function Dashboard() {}"
    assert body["title"] == "Q4 Dashboard"


# ── /analyze — error case ─────────────────────────────────────

def test_analyze_returns_500_when_workflow_crashes(mock_supabase_user, mock_run_copilot):
    """If run_copilot raises, the API must return 500 with a clean error message."""
    mock_run_copilot.side_effect = RuntimeError("LangGraph exploded")

    response = client.post(
        "/analyze",
        json={"query": "anything"},
        headers={"Authorization": "Bearer good-token"},
    )

    assert response.status_code == 500
    assert "LangGraph exploded" in response.json()["detail"]


# ── /history ──────────────────────────────────────────────────

def test_history_returns_user_history(mock_supabase_user, mocker):
    """GET /history fetches user's past queries from Supabase."""
    fake_history = [
        {"query": "q1", "response": "r1"},
        {"query": "q2", "response": "r2"},
    ]
    mocker.patch("app.main.get_history_from_db", return_value=fake_history)

    response = client.get(
        "/history",
        headers={"Authorization": "Bearer good-token"},
    )

    assert response.status_code == 200
    assert response.json() == fake_history