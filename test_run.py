from rag.vector_store import build_vector_store_for_user
from workflows.langgraph_flow import run_copilot
from dotenv import load_dotenv

load_dotenv()

# Step 1 — Build index for test user using your existing PDFs
print("Building test index...")
build_vector_store_for_user("test", [
    "data/your_pdf_name.pdf"   # ← replace with your actual PDF filename
])

# Step 2 — Test dashboard
print("="*60)
result = run_copilot("Show me a revenue dashboard", user_id="test")
print(result[:500])