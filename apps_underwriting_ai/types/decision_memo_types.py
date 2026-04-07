"""
Decision Memo Types - Domain contracts for underwriting decision outputs.
"""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from .underwriting_request_types import DecisionState


class EvidenceItem(BaseModel):
    """Single evidence item supporting a claim."""
    claim_id: str = Field(..., description="Unique claim identifier")
    claim_text: str = Field(..., description="Claim text")
    evidence_type: Literal["document", "structured_metric", "policy_rule"] = Field(..., description="Evidence type")
    source_ref: str = Field(..., description="Source reference (doc_id or field)")
    source_excerpt: Optional[str] = Field(None, description="Relevant excerpt from source")
    confidence: float = Field(0.8, ge=0, le=1, description="Confidence in evidence")


class DecisionMemo(BaseModel):
    """
    Complete underwriting decision memo.
    """
    request_id: str = Field(..., description="Reference to underwriting request")
    recommended_decision: DecisionState = Field(..., description="Recommended decision")
    recommended_amount: Optional[float] = Field(None, description="Recommended loan amount")
    recommended_term_months: Optional[int] = Field(None, description="Recommended term")
    pricing_adjustment_bps: Optional[int] = Field(None, description="Pricing adjustment in basis points")
    conditions_precedent: List[str] = Field(default_factory=list, description="Conditions to close")
    covenants: List[str] = Field(default_factory=list, description="Ongoing covenants")
    key_strengths: List[str] = Field(default_factory=list, description="Key credit strengths")
    key_risks: List[str] = Field(default_factory=list, description="Key credit risks")
    policy_exceptions: List[str] = Field(default_factory=list, description="Policy exceptions requested")
    missing_information: List[str] = Field(default_factory=list, description="Missing information items")
    evidence_register: List[EvidenceItem] = Field(default_factory=list, description="Evidence items")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in recommendation")
    human_review_reason: Optional[str] = Field(None, description="Reason if human review required")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "UW-2024-001234",
                "recommended_decision": "APPROVE_WITH_CONDITIONS",
                "recommended_amount": 2500000.0,
                "recommended_term_months": 60,
                "conditions_precedent": [
                    "Monthly borrowing base certificates required",
                    "First lien UCC filing on AR",
                ],
                "key_strengths": [
                    "Strong DSCR at 3.57x vs policy minimum 1.25x",
                    "Positive deposit trend with 2-year relationship",
                ],
                "key_risks": [
                    "AR concentration at 32% - monitoring required",
                ],
                "confidence_score": 0.82,
            },
        }
