from langchain_groq import ChatGroq
from workflows.state import BusinessState
from dotenv import load_dotenv
import json
import re

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

def clean_output(text: str) -> str:
    """Clean LLM output — fix common formatting issues."""
    if not text:
        return text
    # Replace <br> tags with actual newlines
    text = text.replace("<br>", "\n")
    text = text.replace("<br/>", "\n")
    text = text.replace("<br />", "\n")
    # Remove any other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def response_agent(state: BusinessState) -> BusinessState:
    print("[Response] Formatting final output...")

    intent = state.get("intent", "analysis")

    # ── Analysis path ─────────────────────────────────────────
    if intent == "analysis":
        final = f"""## Business Analysis Report

### Query
{state['query']}

### Analysis
{clean_output(state.get('analysis', ''))}

### Strategic Recommendations
{clean_output(state.get('recommendations', ''))}

---
*Generated using RAG over your business documents*"""

    # ── Lookup path ───────────────────────────────────────────
    elif intent == "lookup":
        prompt = f"""You are a business analyst. Answer this question clearly and concisely 
using ONLY the context provided below.

Rules:
- Give a direct answer in 2-4 sentences maximum
- Extract only the relevant facts
- Do not dump raw text or repeat yourself
- If the answer has a number or metric, highlight it clearly
- Do not use HTML tags like <br> in your response

Question: {state['query']}

Context:
{state['context']}

Give a clean, direct answer:"""

        clean_answer = llm.invoke(prompt).content
        clean_answer = clean_output(clean_answer)

        final = f"""## Quick Lookup Result

### Query
{state['query']}

### Answer
{clean_answer}

---
*Retrieved directly from your business documents*"""

    # ── Summarize path ────────────────────────────────────────
    elif intent == "summarize":
        final = f"""## Document Summary

### Request
{state['query']}

### Summary
{clean_output(state.get('summary', ''))}

---
*Summarized from your business documents*"""

    # ── Dashboard path ────────────────────────────────────────
    elif intent == "dashboard":
        dashboard_code = state.get("dashboard_code", "")
        data = state.get("extracted_data", {})
        final = json.dumps({
            "type": "dashboard",
            "code": dashboard_code,
            "title": data.get("title", "Business Dashboard")
        })

    # ── Fallback ──────────────────────────────────────────────
    else:
        final = f"""## Response

### Query
{state['query']}

### Answer
{clean_output(state.get('analysis') or state.get('context') or 'No response generated.')}

---
*Generated using RAG over your business documents*"""

    return {**state, "final_response": final.strip()}