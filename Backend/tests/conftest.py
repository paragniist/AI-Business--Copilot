from unittest.mock import MagicMock
import pytest

@pytest.fixture
def mock_llm(mocker):
    """Replaces every agent's `llm` object with a fake one."""
    fake_llm = MagicMock()
    fake_llm.invoke.return_value.content = "mocked response"

    agent_modules = [
        "agents.router_agent",
        "agents.analyst_agent",
        "agents.dashboard_agent",
        "agents.data_extractor_agent",
        "agents.response_agent",
        "agents.strategy_agent",
        "agents.summary_agent",
        "rag.query_expander",
    ]
    for mod_name in agent_modules:
        try:
            mocker.patch(f"{mod_name}.llm", fake_llm)
        except (AttributeError, ModuleNotFoundError):
            pass
    return fake_llm
@pytest.fixture
def mock_supabase_user(mocker):
    """Makes Supabase auth always succeed with a fixed user id."""
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"id": "test-user-123"}
    return mocker.patch("app.main.httpx.get", return_value=fake_response)


@pytest.fixture
def mock_run_copilot(mocker):
    """Bypasses the real LangGraph workflow when testing /analyze."""
    return mocker.patch(
        "app.main.run_copilot",
        return_value="## Mocked copilot response",
    )