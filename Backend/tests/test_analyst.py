import pytest
from agents.analyst_agent import analyst_agent


def test_analyst_returns_state_with_analysis(mock_llm):
    # Arrange — tell the fake LLM what to return
    mock_llm.invoke.return_value.content = "Q4 revenue dropped due to seasonal slowdown."

    # Set up input state for the agent
    state = {
        "query": "why did Q4 revenue drop",
        "user_id": "test",
        "context": "Q4 revenue was $2.9M, down 8% from Q3.",
    }

    # Act — run the agent
    result = analyst_agent(state)

    # Assert — check the agent did its job
    assert "analysis" in result
    assert result["analysis"] == "Q4 revenue dropped due to seasonal slowdown."
    # Original state values should still be there
    assert result["query"] == "why did Q4 revenue drop"
    assert result["context"] == "Q4 revenue was $2.9M, down 8% from Q3."


def test_analyst_calls_llm_with_context(mock_llm):
    # Make sure the prompt sent to the LLM actually includes the context
    mock_llm.invoke.return_value.content = "some analysis"

    state = {
        "query": "what happened",
        "user_id": "test",
        "context": "REVENUE_NUMBER_42",
    }

    analyst_agent(state)

    # Inspect what the LLM was called with
    mock_llm.invoke.assert_called_once()
    prompt_sent = mock_llm.invoke.call_args[0][0]  # first positional arg
    assert "REVENUE_NUMBER_42" in prompt_sent
    assert "what happened" in prompt_sent