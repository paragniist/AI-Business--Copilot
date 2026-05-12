from langchain_groq import ChatGroq
from workflows.state import BusinessState
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(
    model="openai/gpt-oss-120b",  
    temperature=0
)

def analyst_agent(state: BusinessState) -> BusinessState:
    print("[Analyst] Analyzing retrieved context...")

    prompt = f"""
You are a senior business analyst.
Based on the context below, analyze the query thoroughly.

Query: {state['query']}

Context from documents:
{state['context']}

Provide:
1. Root cause analysis
2. Key patterns or issues identified  
3. Supporting data points from the context
4. Any risks or concerns

Be specific and data-backed.
"""

    analysis = llm.invoke(prompt).content
    print("[Analyst] Analysis complete")
    return {**state, "analysis": analysis}