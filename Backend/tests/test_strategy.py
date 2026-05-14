import pytest
from agents.strategy_agent import strategy_agent


def test_strategy_returns_state_with_recommendations(mock_llm):
    mock_llm.invoke.return_value.content = "1. Cut costs. 2. Expand into new market."

    state = {
        "query": "what should we do",
        "user_id": "test",
        "analysis": "Revenue declined 8% in Q4 due to seasonal effects.",
    }

    result = strategy_agent(state)

    assert result["recommendations"] == "1. Cut costs. 2. Expand into new market."
    assert result["analysis"] == "Revenue declined 8% in Q4 due to seasonal effects."


def test_strategy_uses_analysis_in_prompt(mock_llm):
    mock_llm.invoke.return_value.content = "recs"

    state = {
        "query": "advise",
        "user_id": "test",
        "analysis": "MARKER_FROM_ANALYST_42",
    }

    strategy_agent(state)

    prompt_sent = mock_llm.invoke.call_args[0][0]
    assert "MARKER_FROM_ANALYST_42" in prompt_sent