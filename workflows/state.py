from typing import TypedDict, Optional, Any

class BusinessState(TypedDict):
    query: str
    user_id: Optional[str]          # ← add this
    intent: Optional[str]
    context: Optional[str]
    analysis: Optional[str]
    recommendations: Optional[str]
    summary: Optional[str]
    final_response: Optional[str]
    extracted_data: Optional[Any]    # ← NEW
    dashboard_code: Optional[str]    # ← NEW