import pytest
from agents.summary_agent import summary_agent


def test_summary_returns_state_with_summary(mock_llm):
    mock_llm.invoke.return_value.content = "Executive summary: revenue declined 8%."

    state = {
        "query": "summarize Q4 results",
        "user_id": "test",
        "context": "Q4 revenue was $2.9M, down from $3.2M.",
    }

    result = summary_agent(state)

    assert result["summary"] == "Executive summary: revenue declined 8%."
    assert result["query"] == "summarize Q4 results"


def test_summary_includes_context_in_prompt(mock_llm):
    mock_llm.invoke.return_value.content = "summary"

    state = {
        "query": "give me highlights",
        "user_id": "test",
        "context": "UNIQUE_MARKER_XYZ",
    }

    summary_agent(state)

    prompt_sent = mock_llm.invoke.call_args[0][0]
    assert "UNIQUE_MARKER_XYZ" in prompt_sent