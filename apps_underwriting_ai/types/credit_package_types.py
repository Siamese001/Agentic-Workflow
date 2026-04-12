"""
Credit Package Types - Domain contracts for credit bureau and scoring data.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, validator


class CreditPackage(BaseModel):
    """
    Credit bureau and scoring information.
    """

    business_bureau_score: Optional[int] = Field(None, ge=0, le=100, description="Business credit score")
    personal_fico_scores: List[int] = Field(
        default_factory=list, description="Personal FICO scores of guarantors"
    )
    delinquencies_24m: int = Field(0, ge=0, description="Delinquencies in last 24 months")
    defaults_ever: int = Field(0, ge=0, description="Defaults ever")
    bankruptcies_ever: int = Field(0, ge=0, description="Bankruptcies ever")
    judgments_or_liens: int = Field(0, ge=0, description="Judgments or tax liens")
    tradeline_utilization_pct: Optional[float] = Field(None, ge=0, le=100, description="Credit utilization")
    credit_narrative_flags: List[str] = Field(default_factory=list, description="Credit narrative flags")

    @validator("personal_fico_scores", each_item=True)
    def validate_fico(cls, v):
        """Validate FICO scores are in valid range."""
        if not 300 <= v <= 850:
            raise ValueError("FICO score must be between 300 and 850")
        return v

    @property
    def min_fico(self) -> Optional[int]:
        """Return minimum FICO score among guarantors."""
        if not self.personal_fico_scores:
            return None
        return min(self.personal_fico_scores)

    @property
    def max_fico(self) -> Optional[int]:
        """Return maximum FICO score among guarantors."""
        if not self.personal_fico_scores:
            return None
        return max(self.personal_fico_scores)

    class Config:
        json_schema_extra = {
            "example": {
                "business_bureau_score": 78,
                "personal_fico_scores": [745, 720],
                "delinquencies_24m": 0,
                "defaults_ever": 0,
                "bankruptcies_ever": 0,
                "judgments_or_liens": 0,
                "tradeline_utilization_pct": 23.5,
                "credit_narrative_flags": [],
            },
        }
