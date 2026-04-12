"""
Risk Feature Types - Domain contracts for derived risk features.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

RiskGrade = Literal["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]


class CapacityFeatures(BaseModel):
    """Debt service capacity features."""

    dscr_ttm: Optional[float] = Field(None, description="TTM DSCR")
    debt_to_ebitda_ttm: Optional[float] = Field(None, description="TTM Debt/EBITDA")
    ebitda_margin_ttm: Optional[float] = Field(None, description="TTM EBITDA margin")
    revenue_trend_score: float = Field(0.5, ge=0, le=1, description="Revenue trend score")
    earnings_stability_score: float = Field(0.5, ge=0, le=1, description="Earnings stability score")


class LiquidityFeatures(BaseModel):
    """Liquidity and cash flow features."""

    current_ratio: Optional[float] = Field(None, description="Current ratio")
    quick_ratio: Optional[float] = Field(None, description="Quick ratio")
    cash_buffer_months: Optional[float] = Field(None, description="Months of cash coverage")
    deposit_stability_score: float = Field(0.5, ge=0, le=1, description="Deposit stability score")


class CollateralFeatures(BaseModel):
    """Collateral coverage features."""

    ltv: Optional[float] = Field(None, ge=0, le=1, description="Loan-to-value ratio")
    borrowing_base_coverage: Optional[float] = Field(None, description="Borrowing base / requested amount")
    collateral_quality_score: float = Field(0.5, ge=0, le=1, description="Collateral quality score")


class CreditFeatures(BaseModel):
    """Credit bureau and scoring features."""

    personal_fico_min: Optional[int] = Field(None, description="Minimum FICO score")
    business_credit_score: Optional[int] = Field(None, description="Business credit score")
    derogatory_event_score: float = Field(0.0, ge=0, le=1, description="Derogatory event risk score")
    delinquencies_24m: int = Field(0, ge=0, description="Delinquencies in last 24 months")


class OperatingRiskFeatures(BaseModel):
    """Operating and business risk features."""

    industry_risk_score: float = Field(0.5, ge=0, le=1, description="Industry risk score")
    customer_concentration_score: Optional[float] = Field(
        None, ge=0, le=1, description="Customer concentration risk"
    )
    supplier_concentration_score: Optional[float] = Field(
        None, ge=0, le=1, description="Supplier concentration risk"
    )
    years_in_business_score: float = Field(0.5, ge=0, le=1, description="Business tenure score")


class RelationshipFeatures(BaseModel):
    """Relationship and behavioral features."""

    tenure_score: float = Field(0.5, ge=0, le=1, description="Customer tenure score")
    deposit_relationship_score: float = Field(0.0, ge=0, le=1, description="Deposit relationship score")
    historical_performance_score: float = Field(0.5, ge=0, le=1, description="Historical performance score")


class DocumentationFeatures(BaseModel):
    """Documentation and data quality features."""

    document_completeness_score: float = Field(0.0, ge=0, le=1, description="Document completeness score")
    data_consistency_score: float = Field(0.5, ge=0, le=1, description="Data consistency score")
    staleness_score: float = Field(0.0, ge=0, le=1, description="Document staleness score")


class PolicyFeatures(BaseModel):
    """Policy compliance features."""

    policy_exception_count: int = Field(0, ge=0, description="Number of policy exceptions")
    prohibited_attribute_detected: bool = Field(False, description="Prohibited attributes detected")
    mandatory_review_triggered: bool = Field(False, description="Mandatory human review triggered")


class CompositeFeatures(BaseModel):
    """Aggregated composite risk features."""

    raw_risk_score: float = Field(0.5, ge=0, le=1, description="Raw composite risk score")
    normalized_risk_grade: RiskGrade = Field("5", description="Normalized risk grade 1-10")
    confidence_score: float = Field(0.5, ge=0, le=1, description="Confidence in risk assessment")


class RiskFeatures(BaseModel):
    """
    Complete derived risk feature set for underwriting.
    """

    capacity: CapacityFeatures = Field(default_factory=CapacityFeatures)
    liquidity: LiquidityFeatures = Field(default_factory=LiquidityFeatures)
    collateral: CollateralFeatures = Field(default_factory=CollateralFeatures)
    credit: CreditFeatures = Field(default_factory=CreditFeatures)
    operating_risk: OperatingRiskFeatures = Field(default_factory=OperatingRiskFeatures)
    relationship: RelationshipFeatures = Field(default_factory=RelationshipFeatures)
    documentation: DocumentationFeatures = Field(default_factory=DocumentationFeatures)
    policy: PolicyFeatures = Field(default_factory=PolicyFeatures)
    composite: CompositeFeatures = Field(default_factory=CompositeFeatures)

    class Config:
        json_schema_extra = {
            "example": {
                "capacity": {
                    "dscr_ttm": 3.57,
                    "debt_to_ebitda_ttm": 1.87,
                    "ebitda_margin_ttm": 0.15,
                    "revenue_trend_score": 0.65,
                    "earnings_stability_score": 0.70,
                },
                "composite": {
                    "raw_risk_score": 0.35,
                    "normalized_risk_grade": "3",
                    "confidence_score": 0.85,
                },
            },
        }
