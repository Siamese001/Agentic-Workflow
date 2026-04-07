"""
Collateral Package Types - Domain contracts for collateral information.
"""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

CollateralType = Literal[
    "ar",
    "inventory",
    "equipment",
    "real_estate",
    "mixed",
    "unsecured",
]

LienPosition = Literal[
    "first",
    "second",
    "junior",
    "none",
]


class CollateralPackage(BaseModel):
    """
    Collateral information for credit underwriting.
    """
    collateral_type: CollateralType = Field(..., description="Primary collateral type")
    estimated_value: Optional[float] = Field(None, ge=0, description="Estimated collateral value")
    advance_rate_pct: Optional[float] = Field(None, ge=0, le=100, description="Advance rate percentage")
    borrowing_base_value: Optional[float] = Field(None, ge=0, description="Borrowing base value")
    lien_position: LienPosition = Field("none", description="Lien position")
    appraisal_date: Optional[str] = Field(None, description="Appraisal date (YYYY-MM-DD)")
    field_exam_date: Optional[str] = Field(None, description="Field exam date (YYYY-MM-DD)")
    collateral_quality_flags: List[str] = Field(default_factory=list, description="Quality flags")

    @property
    def ltv(self) -> Optional[float]:
        """Calculate loan-to-value ratio if data available."""
        if self.estimated_value and self.estimated_value > 0:
            return None  # Requires loan amount from request
        return None

    class Config:
        json_schema_extra = {
            "example": {
                "collateral_type": "ar",
                "estimated_value": 3200000.0,
                "advance_rate_pct": 80.0,
                "borrowing_base_value": 2560000.0,
                "lien_position": "first",
                "appraisal_date": "2024-02-15",
                "field_exam_date": "2024-01-20",
                "collateral_quality_flags": [],
            },
        }
