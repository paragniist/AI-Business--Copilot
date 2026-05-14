import pytest
from agents.data_extractor_agent import data_extractor_agent


def test_extractor_parses_valid_json(mock_llm):
    """Happy path: LLM returns clean JSON, agent parses it."""
    mock_llm.invoke.return_value.content = '{"title": "Q4 Report", "metrics": [{"label": "Revenue", "value": "$10M"}], "charts": []}'

    state = {"query": "build dashboard", "user_id": "test", "context": "some data"}
    result = data_extractor_agent(state)

    assert result["extracted_data"]["title"] == "Q4 Report"
    assert len(result["extracted_data"]["metrics"]) == 1
    assert result["extracted_data"]["metrics"][0]["value"] == "$10M"


def test_extractor_strips_markdown_fences(mock_llm):
    """LLM sometimes wraps JSON in ```json``` blocks — agent must strip them."""
    mock_llm.invoke.return_value.content = (
        "```json\n"
        '{"title": "Fenced", "metrics": [], "charts": []}\n'
        "```"
    )

    state = {"query": "x", "user_id": "test", "context": ""}
    result = data_extractor_agent(state)

    assert result["extracted_data"]["title"] == "Fenced"


def test_extractor_falls_back_when_llm_returns_garbage(mock_llm):
    """If LLM returns unparseable text, agent must NOT crash — use fallback data."""
    mock_llm.invoke.return_value.content = "I'm sorry, I cannot help with that."

    state = {"query": "x", "user_id": "test", "context": ""}
    result = data_extractor_agent(state)

    # Must produce SOME valid extracted_data structure, not crash
    assert "extracted_data" in result
    assert "title" in result["extracted_data"]
    assert "metrics" in result["extracted_data"]
    assert "charts" in result["extracted_data"]