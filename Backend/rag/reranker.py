from sentence_transformers import CrossEncoder
import os

# Load cross-encoder model once at module level
# This model scores (query, passage) pairs for relevance
_model = None

def get_reranker():
    global _model
    if _model is None:
        print("[Reranker] Loading cross-encoder model...")
        _model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2",
            max_length=512
        )
        print("[Reranker] Model loaded")
    return _model

def rerank(query: str, docs: list, top_k: int = 6) -> list:
    """
    Rerank documents by relevance to query using cross-encoder.
    Returns top_k most relevant docs in order.
    """
    if not docs:
        return docs

    print(f"[Reranker] Reranking {len(docs)} chunks...")

    reranker = get_reranker()

    # Create (query, passage) pairs for scoring
    pairs = [(query, doc.page_content) for doc in docs]

    # Score all pairs
    scores = reranker.predict(pairs)

    # Sort docs by score descending
    scored_docs = sorted(
        zip(scores, docs),
        key=lambda x: x[0],
        reverse=True
    )

    # Return top_k docs
    top_docs = [doc for _, doc in scored_docs[:top_k]]

    print(f"[Reranker] Top scores: {[round(float(s), 3) for s, _ in scored_docs[:top_k]]}")
    print(f"[Reranker] Returning top {len(top_docs)} reranked chunks")

    return top_docs