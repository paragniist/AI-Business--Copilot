import pytest
from agents.research_agent import research_agent


def test_research_stores_retrieved_context(mocker):
    """Happy path: retriever returns docs, agent puts them into state['context']."""
    mocker.patch(
        "agents.research_agent.retrieve_context",
        return_value="Q4 revenue was $2.9M. Q3 was $3.2M.",
    )

    state = {"query": "what is Q4 revenue", "user_id": "user-123"}
    result = research_agent(state)

    assert result["context"] == "Q4 revenue was $2.9M. Q3 was $3.2M."


def test_research_handles_no_documents(mocker):
    """When user has no PDFs uploaded, retriever returns the sentinel 'NO_DOCUMENTS'."""
    mocker.patch(
        "agents.research_agent.retrieve_context",
        return_value="NO_DOCUMENTS",
    )

    state = {"query": "anything", "user_id": "user-123"}
    result = research_agent(state)

    # Agent must replace the sentinel with a user-friendly message
    assert "NO_DOCUMENTS" not in result["context"]
    assert "upload" in result["context"].lower()


def test_research_passes_query_and_user_id(mocker):
    """Verify the agent forwards the right arguments to retrieve_context."""
    mock_retriever = mocker.patch(
        "agents.research_agent.retrieve_context",
        return_value="some context",
    )

    state = {"query": "test query", "user_id": "user-abc"}
    research_agent(state)

    mock_retriever.assert_called_once_with("test query", user_id="user-abc")