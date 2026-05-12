from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)

def expand_query(query: str, n: int = 3) -> list[str]:
    """
    Generate n variations of the query for better retrieval.
    Returns original query + n variations.
    """
    print(f"[QueryExpander] Expanding: '{query}'")

    prompt = f"""You are a query expansion specialist for a business document search system.
Given a user query, generate {n} different variations that capture the same intent
but use different words, synonyms, and phrasings.

Rules:
- Each variation must seek the same information as the original
- Use business terminology synonyms
- Vary the phrasing but keep the meaning
- Keep each variation concise (under 15 words)
- Return ONLY the variations, one per line
- No numbering, no bullets, no explanation

Original query: {query}

Generate {n} variations:"""

    response = llm.invoke(prompt).content.strip()

    # Parse variations — one per line
    variations = [
        line.strip()
        for line in response.split("\n")
        if line.strip() and len(line.strip()) > 5
    ][:n]

    # Always include original query
    all_queries = [query] + variations
    print(f"[QueryExpander] Generated {len(all_queries)} queries:")
    for i, q in enumerate(all_queries):
        print(f"  {i+1}. {q}")

    return all_queries