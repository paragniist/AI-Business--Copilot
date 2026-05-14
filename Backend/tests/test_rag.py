import pytest
from rag.query_expander import expand_query

def test_query_expansion_returns_multiple(mock_llm):
    # Tell the fake llm: when invoke() is called, return this content
    mock_llm.invoke.return_value.content = (
        "what caused the decline in sales\n"
        "reason behind dropping revenue numbers\n"
        "factors driving lower sales performance"
    )

    queries = expand_query("why did sales drop", n=3)

    assert len(queries) == 4
    assert queries[0] == "why did sales drop"