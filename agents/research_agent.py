from rag.retriever import retrieve_context
from workflows.state import BusinessState

def research_agent(state: BusinessState) -> BusinessState:
    print("[Research] Fetching relevant context via RAG...")
    user_id = state.get("user_id", "default")
    context = retrieve_context(state["query"], user_id=user_id)

    # If no documents uploaded yet
    if context == "NO_DOCUMENTS":
        context = (
            "The user has not uploaded any documents yet. "
            "Please inform them to upload PDFs using the Upload PDF button."
        )

    return {**state, "context": context}