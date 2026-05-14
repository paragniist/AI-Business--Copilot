import pytest
from agents.dashboard_agent import dashboard_agent


def test_dashboard_stores_code_in_state(mock_llm):
    """Happy path: LLM returns clean React code, agent stores it in state."""
    mock_llm.invoke.return_value.content = "function Dashboard() { return <div>Hi</div>; }"

    state = {
        "query": "show dashboard",
        "user_id": "test",
        "extracted_data": {"title": "Test", "metrics": [], "charts": []},
    }

    result = dashboard_agent(state)

    assert "function Dashboard()" in result["dashboard_code"]


def test_dashboard_strips_markdown_fences(mock_llm):
    """LLM may wrap code in ```jsx``` blocks — fences must be removed."""
    mock_llm.invoke.return_value.content = (
        "```jsx\n"
        "function Dashboard() { return null; }\n"
        "```"
    )

    state = {"query": "x", "user_id": "test", "extracted_data": {}}
    result = dashboard_agent(state)

    assert "```" not in result["dashboard_code"]
    assert "function Dashboard()" in result["dashboard_code"]


def test_dashboard_strips_imports_and_exports(mock_llm):
    """LLM may add import/export despite being told not to — must be stripped."""
    mock_llm.invoke.return_value.content = (
        "import React from 'react';\n"
        "function Dashboard() { return null; }\n"
        "export default Dashboard;"
    )

    state = {"query": "x", "user_id": "test", "extracted_data": {}}
    result = dashboard_agent(state)

    assert "import " not in result["dashboard_code"]
    assert "export " not in result["dashboard_code"]
    assert "function Dashboard()" in result["dashboard_code"]