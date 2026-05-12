from langchain_groq import ChatGroq
from workflows.state import BusinessState
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(
    model="openai/gpt-oss-120b",  
    temperature=0
)

def summary_agent(state: BusinessState) -> BusinessState:
    print("[Summary] Condensing document context...")

    prompt = f"""
You are a business document summarizer.
Summarize the following content clearly and concisely.

Query: {state['query']}

Document Content:
{state['context']}

Provide:
1. Executive summary (2-3 sentences)
2. Key highlights (bullet points)
3. Important numbers or metrics mentioned
4. Main conclusions or takeaways
"""

    summary = llm.invoke(prompt).content
    print("[Summary] Summary complete")
    return {**state, "summary": summary}