from langgraph.graph import StateGraph, END
from workflows.state import BusinessState
from agents.router_agent import router_agent
from agents.research_agent import research_agent
from agents.analyst_agent import analyst_agent
from agents.strategy_agent import strategy_agent
from agents.summary_agent import summary_agent
from agents.response_agent import response_agent
from agents.data_extractor_agent import data_extractor_agent
from agents.dashboard_agent import dashboard_agent

def build_graph():
    graph = StateGraph(BusinessState)

    # ── Add all nodes ──────────────────────────────────────────
    graph.add_node("router",              router_agent)
    graph.add_node("research_analysis",   research_agent)
    graph.add_node("research_lookup",     research_agent)
    graph.add_node("research_summarize",  research_agent)
    graph.add_node("research_dashboard",  research_agent)  # ← NEW
    graph.add_node("analyze",             analyst_agent)
    graph.add_node("strategy",            strategy_agent)
    graph.add_node("summarize",           summary_agent)
    graph.add_node("extract_data",        data_extractor_agent)  # ← NEW
    graph.add_node("generate_dashboard",  dashboard_agent)       # ← NEW
    graph.add_node("respond",             response_agent)

    # ── Entry point ────────────────────────────────────────────
    graph.set_entry_point("router")

    # ── Intelligent routing ────────────────────────────────────
    def route_decision(state: BusinessState) -> str:
        return state["intent"]

    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "analysis":  "research_analysis",
            "lookup":    "research_lookup",
            "summarize": "research_summarize",
            "dashboard": "research_dashboard",  # ← NEW
        }
    )

    # ── Path A: Full Analysis ──────────────────────────────────
    graph.add_edge("research_analysis",  "analyze")
    graph.add_edge("analyze",            "strategy")
    graph.add_edge("strategy",           "respond")

    # ── Path B: Quick Lookup ───────────────────────────────────
    graph.add_edge("research_lookup",    "respond")

    # ── Path C: Summarize ─────────────────────────────────────
    graph.add_edge("research_summarize", "summarize")
    graph.add_edge("summarize",          "respond")

    # ── Path D: Dashboard ─────────────────────────────────────
    graph.add_edge("research_dashboard", "extract_data")
    graph.add_edge("extract_data",       "generate_dashboard")
    graph.add_edge("generate_dashboard", "respond")

    # ── All paths converge ─────────────────────────────────────
    graph.add_edge("respond", END)

    return graph.compile()


def run_copilot(query: str, user_id: str = "default") -> str:
    app = build_graph()
    result = app.invoke({
        "query": query,
        "user_id": user_id,
        "intent": None,
        "context": None,
        "analysis": None,
        "recommendations": None,
        "summary": None,
        "extracted_data": None,      # ← NEW
        "dashboard_code": None,      # ← NEW
        "final_response": None,
    })
    return result["final_response"]