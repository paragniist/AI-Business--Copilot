from langchain_community.retrievers import BM25Retriever
from rag.vector_store import (
    load_vector_store_for_user,
    user_has_documents
)
from rag.query_expander import expand_query
from rag.reranker import rerank
import os
import pickle

def get_all_chunks_for_user(user_id: str):
    """Load saved chunks for BM25 retriever."""
    chunks_path = f"faiss_indexes/{user_id}/chunks.pkl"
    if not os.path.exists(chunks_path):
        return None
    with open(chunks_path, "rb") as f:
        return pickle.load(f)

def retrieve_context(query: str, user_id: str, k: int = 6) -> str:
    """
    Full advanced RAG pipeline:
    1. Query expansion  — multiple query variations
    2. Hybrid search    — BM25 + FAISS for each variation
    3. Deduplicate      — remove duplicate chunks
    4. Rerank           — cross-encoder scores true relevance
    5. Return top k     — best chunks as context
    """

    if not user_has_documents(user_id):
        return "NO_DOCUMENTS"

    chunks = get_all_chunks_for_user(user_id)

    # ── Step 1: Query expansion ────────────────────────────────
    expanded_queries = expand_query(query, n=3)

    # ── Step 2: Hybrid search with all queries ─────────────────
    store = load_vector_store_for_user(user_id)
    all_docs = []

    for q in expanded_queries:
        # FAISS semantic search
        faiss_docs = store.similarity_search(q, k=4)
        all_docs.extend(faiss_docs)

        # BM25 keyword search
        if chunks:
            bm25 = BM25Retriever.from_documents(chunks)
            bm25.k = 4
            bm25_docs = bm25.invoke(q)
            all_docs.extend(bm25_docs)

    print(f"[Retriever] Raw docs from {len(expanded_queries)} queries: {len(all_docs)}")

    # ── Step 3: Deduplicate ────────────────────────────────────
    seen = set()
    unique_docs = []
    for doc in all_docs:
        content_hash = hash(doc.page_content[:100])
        if content_hash not in seen:
            seen.add(content_hash)
            unique_docs.append(doc)

    print(f"[Retriever] Unique after dedup: {len(unique_docs)}")

    if not unique_docs:
        return "No relevant content found in your documents."

    # ── Step 4: Rerank by true relevance ──────────────────────
    # Only rerank if we have more docs than needed
    if len(unique_docs) > k:
        reranked_docs = rerank(query, unique_docs, top_k=k)
    else:
        reranked_docs = unique_docs
        print(f"[Retriever] Skipping rerank — only {len(unique_docs)} docs")

    # ── Step 5: Format context ─────────────────────────────────
    context = "\n\n".join([
        f"[Doc {i+1}]: {d.page_content}"
        for i, d in enumerate(reranked_docs)
    ])

    print(f"[Retriever] Final context: {len(reranked_docs)} chunks")
    return context