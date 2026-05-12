from langchain_groq import ChatGroq
from workflows.state import BusinessState
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

def router_agent(state: BusinessState) -> BusinessState:
    print(f"[Router] Query: {state['query']}")

    query = state['query'].lower()

    # ── Keyword-based routing first (fast + reliable) ─────────
    dashboard_keywords = [
        "dashboard", "chart", "plot", "graph", "visualize",
        "visualization", "visual", "kpi", "metrics chart",
        "show me a", "generate a chart", "bar chart",
        "line chart", "pie chart", "trend chart"
    ]

    lookup_keywords = [
        "what was", "what is", "how much", "how many",
        "what were", "tell me the", "give me the number",
        "what percentage", "how did"
    ]

    summarize_keywords = [
        "summarize", "summary", "summarise", "condense",
        "brief", "overview", "highlight", "key points",
        "tldr", "give me highlights"
    ]

    # Check dashboard first
    if any(kw in query for kw in dashboard_keywords):
        intent = "dashboard"

    # Then summarize
    elif any(kw in query for kw in summarize_keywords):
        intent = "summarize"

    # Then lookup
    elif any(kw in query for kw in lookup_keywords):
        intent = "lookup"

    # Fall back to LLM for ambiguous queries
    else:
        prompt = f"""Classify this business query into exactly one word:
- analysis → complex why/how questions needing deep investigation
- lookup → simple factual questions needing a number or fact
- summarize → requests to condense or summarize documents
- dashboard → requests to visualize, chart, or plot data

Query: {state['query']}

Reply with ONLY one word:"""

        intent = llm.invoke(prompt).content.strip().lower()

        if intent not in ["analysis", "lookup", "summarize", "dashboard"]:
            intent = "analysis"

    print(f"[Router] Intent detected: {intent}")
    return {**state, "intent": intent}