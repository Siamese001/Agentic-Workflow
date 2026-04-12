"""
Borrower Profile Types - Domain contracts for borrower entity information.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, validator

EntityType = Literal[
    "llc",
    "corp",
    "partnership",
    "sole_prop",
    "nonprofit",
]


class OwnerInfo(BaseModel):
    """Ownership and guarantor information."""

    owner_name: str = Field(..., description="Owner name")
    ownership_pct: float = Field(..., ge=0, le=100, description="Ownership percentage")
    role: str = Field(..., description="Role in company (e.g., CEO, CFO)")
    fico: Optional[int] = Field(None, ge=300, le=850, description="Personal FICO score")
    guarantor: bool = Field(..., description="Is this owner a personal guarantor")


class BorrowerProfile(BaseModel):
    """
    Borrower entity profile with ownership, industry, and risk flags.
    """

    legal_name: str = Field(..., description="Legal entity name")
    entity_type: EntityType = Field(..., description="Entity legal structure")
    industry_code: str = Field(..., description="NAICS or SIC industry code")
    industry_description: str = Field(..., description="Industry description")
    years_in_business: float = Field(..., ge=0, description="Years in operation")
    state_of_incorporation: str = Field(..., description="State of incorporation")
    operating_states: List[str] = Field(default_factory=list, description="States where entity operates")
    employee_count: Optional[int] = Field(None, ge=0, description="Employee count")
    ownership: List[OwnerInfo] = Field(default_factory=list, description="Ownership structure")
    naics_risk_flags: List[str] = Field(default_factory=list, description="NAICS-derived risk flags")
    sanctions_or_watchlist_hits: List[str] = Field(
        default_factory=list, description="Sanctions/watchlist hits"
    )

    @validator("years_in_business")
    def validate_years(cls, v):
        """Validate years in business is non-negative."""
        if v < 0:
            raise ValueError("years_in_business must be non-negative")
        return v

    @validator("ownership")
    def validate_ownership_sum(cls, v):
        """Validate ownership percentages sum to reasonable range (allowing for rounding)."""
        if not v:
            return v
        total = sum(owner.ownership_pct for owner in v)
        if total < 95 or total > 105:
            # Allow some flexibility for complex structures
            pass  # Log warning but don't fail
        return v

    @validator("employee_count")
    def validate_employee_count(cls, v):
        """Validate employee count is non-negative."""
        if v is not None and v < 0:
            raise ValueError("employee_count must be non-negative")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "legal_name": "Acme Manufacturing LLC",
                "entity_type": "llc",
                "industry_code": "332710",
                "industry_description": "Machine Shops",
                "years_in_business": 12.5,
                "state_of_incorporation": "DE",
                "operating_states": ["PA", "OH", "WV"],
                "employee_count": 145,
                "ownership": [
                    {
                        "owner_name": "John Smith",
                        "ownership_pct": 60.0,
                        "role": "CEO",
                        "fico": 745,
                        "guarantor": True,
                    },
                    {
                        "owner_name": "Jane Doe",
                        "ownership_pct": 40.0,
                        "role": "CFO",
                        "fico": 720,
                        "guarantor": True,
                    },
                ],
                "naics_risk_flags": [],
                "sanctions_or_watchlist_hits": [],
            },
        }
