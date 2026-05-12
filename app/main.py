from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from workflows.langgraph_flow import run_copilot
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram

import httpx
import os
import tempfile
import json

load_dotenv()

app = FastAPI(title="AI Business Copilot")

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Prometheus Metrics ───────────────────────────────────────

# Total AI requests
llm_requests_total = Counter(
    "llm_requests_total",
    "Total LLM Requests"
)

# Failed AI requests
llm_errors_total = Counter(
    "llm_errors_total",
    "Total LLM Errors"
)

# LLM response latency
llm_response_seconds = Histogram(
    "llm_response_seconds",
    "LLM Response Time"
)

# RAG retrieval latency
rag_retrieval_seconds = Histogram(
    "rag_retrieval_seconds",
    "RAG Retrieval Time"
)

# PDF uploads
pdf_upload_total = Counter(
    "pdf_upload_total",
    "Total PDF Uploads"
)

# Register Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# ── Supabase config ───────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# ── Models ────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str

# ── Helpers ───────────────────────────────────────────────────
def get_user_id(authorization: str) -> str:

    token = authorization.replace("Bearer ", "")

    res = httpx.get(
        f"{SUPABASE_URL}/auth/v1/user",
        headers={
            "Authorization": f"Bearer {token}",
            "apikey": SUPABASE_SERVICE_KEY,
        }
    )

    if res.status_code != 200:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return res.json()["id"]


def save_history(user_id: str, query: str, response: str):

    try:

        httpx.post(
            f"{SUPABASE_URL}/rest/v1/query_history",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            json={
                "user_id": user_id,
                "query": query,
                "response": response,
            }
        )

    except Exception:
        pass


def get_history_from_db(user_id: str):

    try:

        res = httpx.get(
            f"{SUPABASE_URL}/rest/v1/query_history",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            },
            params={
                "select": "*",
                "user_id": f"eq.{user_id}",
                "order": "created_at.desc",
                "limit": "50",
            }
        )

        return res.json()

    except Exception:
        return []

# ── Routes ────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "running"}


@app.post("/analyze")
async def analyze(
    request: QueryRequest,
    authorization: str = Header(...)
):

    # 1. Verify user
    user_id = get_user_id(authorization)

    # 2. Track total AI requests
    llm_requests_total.inc()

    # 3. Run LangGraph copilot with latency tracking
    try:

        with llm_response_seconds.time():

            result = run_copilot(
                request.query,
                user_id=user_id
            )

    except Exception as e:

        llm_errors_total.inc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    # 4. Check if dashboard response
    try:

        parsed = json.loads(result)

        if parsed.get("type") == "dashboard":

            save_history(
                user_id,
                request.query,
                "Dashboard generated"
            )

            return {
                "query": request.query,
                "response": "Dashboard generated from your documents",
                "type": "dashboard",
                "dashboard_code": parsed.get("code", ""),
                "title": parsed.get("title", "Business Dashboard")
            }

    except Exception:
        pass

    # 5. Regular text response
    save_history(user_id, request.query, result)

    return {
        "query": request.query,
        "response": result,
        "type": "text"
    }


@app.get("/history")
async def get_history(
    authorization: str = Header(...)
):

    user_id = get_user_id(authorization)

    return get_history_from_db(user_id)


@app.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
    authorization: str = Header(...)
):

    from rag.vector_store import build_vector_store_for_user

    # 1. Verify user
    user_id = get_user_id(authorization)

    # 2. Save file temporarily
    suffix = f"_{file.filename}"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as tmp:

        content = await file.read()

        tmp.write(content)

        tmp_path = tmp.name

    # 3. Build FAISS index
    try:

        # Track uploads
        pdf_upload_total.inc()

        # Track ingestion latency
        with rag_retrieval_seconds.time():

            build_vector_store_for_user(
                user_id,
                [tmp_path]
            )

        print(
            f"[Ingest] PDF ingested for user "
            f"{user_id}: {file.filename}"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        os.unlink(tmp_path)

    return {
        "status": "success",
        "filename": file.filename,
        "message": f"{file.filename} has been ingested successfully"
    }