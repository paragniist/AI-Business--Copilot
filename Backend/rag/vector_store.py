from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
import pickle

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        encode_kwargs={'normalize_embeddings': True}
    )

def build_vector_store_for_user(user_id: str, pdf_paths: list[str]):
    """Build or update FAISS index + save chunks for BM25."""
    index_path = f"faiss_indexes/{user_id}"
    os.makedirs(index_path, exist_ok=True)

    docs = []
    for path in pdf_paths:
        print(f"[VectorStore] Loading: {path}")
        loader = PyPDFLoader(path)
        docs.extend(loader.load())

    if not docs:
        raise ValueError("No content found in PDFs")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    new_chunks = splitter.split_documents(docs)
    print(f"[VectorStore] New chunks: {len(new_chunks)}")

    embeddings = get_embeddings()
    chunks_path = f"{index_path}/chunks.pkl"

    # ── Update existing index ──────────────────────────────────
    if os.path.exists(f"{index_path}/index.faiss"):
        print("[VectorStore] Updating existing index...")
        existing = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        existing.add_documents(new_chunks)
        existing.save_local(index_path)

        # Append to existing chunks for BM25
        if os.path.exists(chunks_path):
            with open(chunks_path, "rb") as f:
                existing_chunks = pickle.load(f)
            all_chunks = existing_chunks + new_chunks
        else:
            all_chunks = new_chunks

    # ── Create new index ───────────────────────────────────────
    else:
        print("[VectorStore] Creating new index...")
        store = FAISS.from_documents(new_chunks, embeddings)
        store.save_local(index_path)
        all_chunks = new_chunks

    # Save all chunks for BM25
    with open(chunks_path, "wb") as f:
        pickle.dump(all_chunks, f)

    print(f"[VectorStore] Saved {len(all_chunks)} total chunks")
    print(f"[VectorStore] Index saved to {index_path}/")

def load_vector_store_for_user(user_id: str):
    """Load user's personal FAISS index."""
    index_path = f"faiss_indexes/{user_id}"

    if not os.path.exists(f"{index_path}/index.faiss"):
        raise ValueError(
            "No documents found for this user. "
            "Please upload PDFs first using the Upload PDF button."
        )

    embeddings = get_embeddings()
    return FAISS.load_local(
        index_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

def user_has_documents(user_id: str) -> bool:
    """Check if user has any ingested documents."""
    index_path = f"faiss_indexes/{user_id}"
    return os.path.exists(f"{index_path}/index.faiss")