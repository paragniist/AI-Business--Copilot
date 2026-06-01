from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from workflows.langgraph_flow import run_copilot
from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram
from fastapi.responses import StreamingResponse
import asyncio

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
        "https://ai-business-copilot-3483.vercel.app",
    ],
    allow_origin_regex=r"https://ai-business-copilot-3483-.*\.vercel\.app",
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


import json
from fastapi.responses import StreamingResponse


# Map your existing graph node names to friendly status messages
NODE_STATUS = {
    "router": "Categorizing query...",
    "research_analysis": "Searching your documents...",
    "research_lookup": "Searching your documents...",
    "research_summarize": "Searching your documents...",
    "research_dashboard": "Searching your documents...",
    "analyze": "Analyzing data...",
    "strategy": "Generating recommendations...",
    "summarize": "Summarizing documents...",
    "extract_data": "Extracting metrics...",
    "generate_dashboard": "Building dashboard...",
    "respond": "Formatting response...",
}


@app.post("/analyze/stream")
async def analyze_stream(request: QueryRequest, authorization: str = Header(...)):
    from workflows.langgraph_flow import build_graph

    user_id = get_user_id(authorization)
    llm_requests_total.inc()

    graph = build_graph()
    initial_state = {
        "query": request.query,
        "user_id": user_id,
        "intent": None,
        "context": None,
        "analysis": None,
        "recommendations": None,
        "summary": None,
        "extracted_data": None,
        "dashboard_code": None,
        "final_response": None,
    }

    def sse(event_type: str, **kwargs) -> str:
        return f"data: {json.dumps({'type': event_type, **kwargs})}\n\n"

    async def event_stream():
        full_response = ""
        try:
            async for event in graph.astream_events(initial_state, version="v2"):
                kind = event["event"]
                node_name = event.get("name", "")

                # Status update when a known node starts
                if kind == "on_chain_start" and node_name in NODE_STATUS:
                    yield sse("status", text=NODE_STATUS[node_name])

                # When the router finishes, broadcast the detected intent
                elif kind == "on_chain_end" and node_name == "router":
                    output = event.get("data", {}).get("output", {})
                    intent = output.get("intent") if isinstance(output, dict) else None
                    if intent:
                        yield sse("intent", intent=intent)

                # Token-by-token LLM streaming
                elif kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    token = getattr(chunk, "content", "") or ""
                    if token:
                        full_response += token
                        yield sse("content", text=token)

            # Save history once stream completes
            save_history(user_id, request.query, full_response)
            yield sse("done")

        except Exception as e:
            llm_errors_total.inc()
            yield sse("error", text=str(e))

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no"},
    )




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