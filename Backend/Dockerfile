# ── Base image: Python 3.11 on a slim Ubuntu ───────────────────────────────
FROM python:3.11-slim

# ── Install uv (the same package manager you use locally) ──────────────────
RUN pip install --no-cache-dir uv

# ── Set working directory inside the container ────────────────────────────
WORKDIR /app

# ── Copy ONLY dependency files first (for layer caching) ──────────────────
# These rarely change. As long as they don't, Docker reuses the deps layer.
COPY pyproject.toml uv.lock .python-version ./

# ── Install production dependencies only (no pytest/pytest-mock) ──────────
# --frozen   = install exact versions from uv.lock (reproducible)
# --no-dev   = skip the [dependency-groups].dev block (tests aren't needed
#              in production — smaller image, less attack surface)
RUN uv sync --frozen --no-dev

# ── Make the venv's binaries (like uvicorn) reachable as commands ─────────
ENV PATH="/app/.venv/bin:$PATH"

# ── Now copy your actual code ──────────────────────────────────────────────
# Only the directories you need at runtime. NOT tests, NOT .venv,
# NOT data PDFs, NOT htmlcov.
COPY app ./app
COPY agents ./agents
COPY rag ./rag
COPY workflows ./workflows

# ── Tell readers/Docker the app listens on port 8080 ──────────────────────
EXPOSE 8080

# ── Default command: start the FastAPI server ──────────────────────────────
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]