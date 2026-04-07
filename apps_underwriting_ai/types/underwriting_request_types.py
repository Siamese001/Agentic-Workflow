"""
Underwriting Request Types - Domain contracts for credit underwriting requests.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, validator

from .banking_package_types import BankingPackage
from .borrower_profile_types import BorrowerProfile
from .collateral_package_types import CollateralPackage
from .credit_package_types import CreditPackage
from .decision_constraints_types import DecisionConstraints
from .document_package_types import DocumentPackage
from .financial_package_types import FinancialPackage
from .policy_context_types import PolicyContext
from .relationship_context_types import RelationshipContext

ProductType = Literal["term_loan", "revolver", "equipment_finance", "sba_like"]

DecisionType = Literal["new", "renewal", "increase", "modification"]

InterestType = Literal["fixed", "floating", "mixed"]

DecisionState = Literal[
    "APPROVE",
    "APPROVE_WITH_CONDITIONS",
    "COUNTER_OFFER",
    "PEND_FOR_INFORMATION",
    "DECLINE",
    "ESCALATE_TO_HUMAN",
]


class RequestedStructure(BaseModel):
    """Loan structure requested by borrower."""

    amortization_months: int | None = Field(None, description="Amortization period in months")
    interest_type: InterestType = Field("floating", description="Fixed, floating, or mixed interest")
    collateral_required: bool = Field(True, description="Whether collateral is required")
    guarantor_required: bool = Field(True, description="Whether personal guaranty is required")


class ExternalSignals(BaseModel):
    """External market and reputation signals."""

    industry_outlook: Literal["positive", "stable", "negative", "unknown"] = Field(
        "unknown", description="Industry outlook from external sources",
    )
    macro_flags: list[str] = Field(default_factory=list, description="Macroeconomic flags")
    fraud_or_identity_signals: list[str] = Field(default_factory=list, description="Fraud detection flags")
    litigation_hits: list[str] = Field(default_factory=list, description="Active litigation flags")
    news_reputation_flags: list[str] = Field(default_factory=list, description="News/reputation flags")


class UnderwritingRequest(BaseModel):
    """
    Primary underwriting request contract.

    Represents a complete credit request package for commercial underwriting decision support.
    """

    request_id: str = Field(..., description="Unique request identifier")
    submission_ts: str = Field(..., description="ISO 8601 timestamp of submission")
    product_type: ProductType = Field(..., description="Type of credit product")
    decision_type: DecisionType = Field(..., description="New, renewal, increase, or modification")
    requested_amount: float = Field(..., gt=0, description="Requested loan amount in USD")
    requested_term_months: int = Field(..., gt=0, description="Requested term in months")
    requested_structure: RequestedStructure = Field(..., description="Loan structure details")
    borrower: BorrowerProfile = Field(..., description="Borrower entity profile")
    financials: FinancialPackage = Field(..., description="Financial data package")
    collateral: CollateralPackage = Field(..., description="Collateral information")
    credit: CreditPackage = Field(..., description="Credit bureau and scoring data")
    banking: BankingPackage = Field(..., description="Banking relationship data")
    documents: DocumentPackage = Field(..., description="Document references and metadata")
    policy_context: PolicyContext = Field(..., description="Applicable policy parameters")
    external_signals: ExternalSignals = Field(
        default_factory=ExternalSignals, description="External market signals",
    )
    relationship_context: RelationshipContext = Field(..., description="Existing relationship context")
    decision_constraints: DecisionConstraints = Field(
        ..., description="Decision authority and timing constraints",
    )

    @validator("submission_ts")
    def validate_timestamp(cls, v):
        """Validate ISO 8601 timestamp format."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError:
            raise ValueError("submission_ts must be valid ISO 8601 format")

    @validator("requested_amount")
    def validate_positive_amount(cls, v):
        """Ensure requested amount is positive."""
        if v <= 0:
            raise ValueError("requested_amount must be positive")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "UW-2024-001234",
                "submission_ts": "2024-03-15T09:30:00Z",
                "product_type": "term_loan",
                "decision_type": "new",
                "requested_amount": 2500000.0,
                "requested_term_months": 60,
                "requested_structure": {
                    "amortization_months": 60,
                    "interest_type": "floating",
                    "collateral_required": True,
                    "guarantor_required": True,
                },
            },
        }
