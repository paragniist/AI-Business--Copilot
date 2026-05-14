import pytest
from agents.router_agent import router_agent


def test_dashboard_intent():
    state = {"query": "show me a revenue dashboard", "user_id": "test"}
    result = router_agent(state)
    assert result["intent"] == "dashboard"


def test_lookup_intent():
    state = {"query": "what was the total revenue", "user_id": "test"}
    result = router_agent(state)
    assert result["intent"] == "lookup"


def test_analysis_intent(mock_llm):
    # This query has no matching keyword, so the router falls back to the LLM.
    # We tell the fake LLM to return "analysis" so the test is deterministic.
    mock_llm.invoke.return_value.content = "analysis"

    state = {"query": "why did sales drop last quarter", "user_id": "test"}
    result = router_agent(state)

    assert result["intent"] == "analysis"