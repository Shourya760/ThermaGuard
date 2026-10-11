"""
app/schemas/risk.py

Pydantic schemas for the explainable heat-risk engine.
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class RiskResponse(BaseModel):
    """
    Response schema for the explainable heat-risk engine.
    """
    zone_id: str = Field(description="The zone identifier.")
    
    status: Literal["score_available", "insufficient_data"] = Field(
        description="Whether a reliable score could be calculated from the available data."
    )
    
    score: Optional[float] = Field(
        default=None,
        description="Normalized 0-100 heat risk score. Null if data is insufficient."
    )
    
    category: Optional[str] = Field(
        default=None,
        description="Risk category (e.g., Low, Moderate, High, Extreme). Null if data is insufficient."
    )
    
    methodology_version: str = Field(
        description="Version of the scoring methodology."
    )
    
    methodology_description: str = Field(
        description="Explanation of how the score is calculated and its assumptions."
    )
    
    limitations: List[str] = Field(
        description="Explicit limitations of this modeled indicator."
    )
    
    inputs_used: Dict[str, Any] = Field(
        description="The actual data values used in the calculation."
    )
    
    missing_indicators: List[str] = Field(
        description="List of required indicators that were null or missing."
    )
    
    contributing_factors: Optional[Dict[str, float]] = Field(
        default=None,
        description="Breakdown of how each factor contributed to the final score (if scored)."
    )
