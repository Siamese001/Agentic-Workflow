"""
Policy Context Types - Domain contracts for underwriting policy parameters.
"""

from pydantic import BaseModel, Field


class CollateralRules(BaseModel):
    """Collateral-specific policy rules."""

    min_ltv: float | None = Field(None, ge=0, le=1, description="Minimum LTV")
    max_ltv: float | None = Field(None, ge=0, le=1, description="Maximum LTV")
    eligible_collateral: list[str] = Field(default_factory=list, description="Eligible collateral types")


class PolicyContext(BaseModel):
    """
    Underwriting policy context and constraints.
    """

    policy_version: str = Field("POL-2024-DEFAULT", description="Policy version identifier")
    min_dscr: float | None = Field(None, gt=0, description="Minimum DSCR requirement")
    max_debt_to_ebitda: float | None = Field(None, gt=0, description="Maximum Debt/EBITDA")
    min_fico: int | None = Field(None, ge=300, le=850, description="Minimum FICO requirement")
    restricted_industries: list[str] = Field(default_factory=list, description="NAICS codes restricted")
    prohibited_jurisdictions: list[str] = Field(
        default_factory=list,
        description="Prohibited states/countries",
    )
    max_single_customer_concentration_pct: float | None = Field(
        None,
        ge=0,
        le=100,
        description="Max customer concentration",
    )
    collateral_rules: CollateralRules = Field(default_factory=CollateralRules)
    exception_rules: list[str] = Field(default_factory=list, description="Exception categories")
    human_review_triggers: list[str] = Field(
        default_factory=list,
        description="Auto-trigger for human review",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "policy_version": "POL-2024-Q1-v2",
                "min_dscr": 1.25,
                "max_debt_to_ebitda": 3.5,
                "min_fico": 680,
                "restricted_industries": ["7132", "7211"],
                "prohibited_jurisdictions": [],
                "max_single_customer_concentration_pct": 30.0,
                "collateral_rules": {
                    "min_ltv": None,
                    "max_ltv": 0.85,
                    "eligible_collateral": ["ar", "inventory", "equipment", "real_estate"],
                },
                "exception_rules": ["DSCR_1.15_to_1.25_with_strong_collateral"],
                "human_review_triggers": ["dscr_below_1.25", "debt_to_ebitda_above_3.5", "fico_below_680"],
            },
        }
