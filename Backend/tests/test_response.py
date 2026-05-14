import json
import pytest
from agents.response_agent import response_agent


def test_response_analysis_path_no_llm_call(mock_llm):
    """Analysis path just formats existing state — should NOT call the LLM."""
    state = {
        "query": "why did sales drop",
        "user_id": "test",
        "intent": "analysis",
        "analysis": "Sales fell due to seasonality.",
        "recommendations": "Run a Q1 promo.",
    }

    result = response_agent(state)

    assert "Business Analysis Report" in result["final_response"]
    assert "Sales fell due to seasonality." in result["final_response"]
    assert "Run a Q1 promo." in result["final_response"]
    mock_llm.invoke.assert_not_called()  # critical: no LLM call on this path


def test_response_lookup_path_calls_llm(mock_llm):
    """Lookup path DOES call the LLM to produce a clean direct answer."""
    mock_llm.invoke.return_value.content = "Total revenue was $12.4M."

    state = {
        "query": "what was total revenue",
        "user_id": "test",
        "intent": "lookup",
        "context": "FY2025 revenue: $12.4M total.",
    }

    result = response_agent(state)

    assert "Quick Lookup Result" in result["final_response"]
    assert "Total revenue was $12.4M." in result["final_response"]
    mock_llm.invoke.assert_called_once()


def test_response_dashboard_path_returns_json(mock_llm):
    """Dashboard path returns a JSON string, not markdown."""
    state = {
        "query": "show me a dashboard",
        "user_id": "test",
        "intent": "dashboard",
        "dashboard_code": "function Dashboard() { return <div/>; }",
        "extracted_data": {"title": "Q4 Dashboard"},
    }

    result = response_agent(state)

    parsed = json.loads(result["final_response"])  # must be valid JSON
    assert parsed["type"] == "dashboard"
    assert parsed["title"] == "Q4 Dashboard"
    assert "function Dashboard()" in parsed["code"]
    mock_llm.invoke.assert_not_called()