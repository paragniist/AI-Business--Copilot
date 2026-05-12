from langchain_groq import ChatGroq
from workflows.state import BusinessState
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(
    model="openai/gpt-oss-120b",  
    temperature=0
)
def strategy_agent(state: BusinessState) -> BusinessState:
    print("[Strategy] Generating recommendations...")

    prompt = f"""
You are a business strategy consultant.
Based on the analysis below, generate clear actionable recommendations.

Original Query: {state['query']}

Analysis:
{state['analysis']}

Provide:
1. Top 3-5 prioritized recommendations
2. Short-term actions (this week/month)
3. Long-term strategic moves
4. Expected impact of each recommendation

Keep recommendations specific, realistic and business-focused.
"""

    recommendations = llm.invoke(prompt).content
    print("[Strategy] Recommendations ready")
    return {**state, "recommendations": recommendations}