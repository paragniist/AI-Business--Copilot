import json
import pytest
from workflows.langgraph_flow import run_copilot


@pytest.fixture(autouse=False)
def mock_retriever(mocker):
    """Stub the RAG retriever so workflow tests don't touch FAISS or the filesystem."""
    return mocker.patch(
        "agents.research_agent.retrieve_context",
        return_value="Q4 revenue was $2.9M, down 8% from Q3.",
    )


def test_workflow_analysis_path(mock_llm, mock_retriever):
    """Query with no matching keyword → router falls to LLM → 'analysis' path."""
    # router's LLM call returns "mocked response" → invalid intent → fallback to 'analysis'
    final = run_copilot("why did sales drop last quarter", user_id="test-user")

    # The analysis path produces a Business Analysis Report
    assert "Business Analysis Report" in final
    assert "Strategic Recommendations" in final


def test_workflow_lookup_path(mock_llm, mock_retriever):
    """Keyword 'what was' → lookup path → research → respond."""
    final = run_copilot("what was the total revenue", user_id="test-user")

    assert "Quick Lookup Result" in final
    assert "Answer" in final


def test_workflow_summarize_path(mock_llm, mock_retriever):
    """Keyword 'summarize' → summarize path → research → summary → respond."""
    final = run_copilot("summarize the Q4 report", user_id="test-user")

    assert "Document Summary" in final
    assert "Summary" in final


def test_workflow_dashboard_path(mock_llm, mock_retriever):
    """Keyword 'show me a' → dashboard path → research → extract → dashboard → respond."""
    final = run_copilot("show me a revenue dashboard", user_id="test-user")

    # Dashboard path returns a JSON string, not markdown
    parsed = json.loads(final)
    assert parsed["type"] == "dashboard"
    assert "code" in parsed
    assert "title" in parsed


def test_workflow_passes_user_id_to_retriever(mock_llm, mock_retriever):
    """Verify the workflow correctly threads user_id through to the RAG layer."""
    run_copilot("what was the revenue", user_id="user-abc-789")

    mock_retriever.assert_called()
    # retrieve_context is called with (query, user_id=...)
    call_kwargs = mock_retriever.call_args.kwargs
    assert call_kwargs.get("user_id") == "user-abc-789"