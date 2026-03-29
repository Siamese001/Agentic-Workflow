"""
Decision Packet Types - Domain contracts for decision output packages.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from .underwriting_request_types import DecisionState
from .risk_feature_types import RiskFeatures


class DecisionPacket(BaseModel):
    """
    Machine-readable decision packet for downstream systems.
    """
    request_id: str = Field(..., description="Reference to request")
    decision_state: DecisionState = Field(..., description="Decision outcome")
    recommended_structure: Dict[str, Any] = Field(default_factory=dict, description="Recommended structure")
    pricing_adjustment_bps: Optional[int] = Field(None, description="Pricing adjustment in bps")
    conditions: List[str] = Field(default_factory=list, description="Conditions precedent")
    covenants: List[str] = Field(default_factory=list, description="Ongoing covenants")
    exception_flags: List[str] = Field(default_factory=list, description="Exception flags")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence score")
    review_required: bool = Field(..., description="Human review required")
    review_reason: Optional[str] = Field(None, description="Reason for human review")


class AuditTrace(BaseModel):
    """
    Complete audit trace for compliance and replay.
    """
    request_id: str = Field(..., description="Request ID")
    trace_id: str = Field(..., description="Trace ID from core")
    policy_hash: Optional[str] = Field(None, description="Policy version hash")
    derived_features: RiskFeatures = Field(..., description="Derived risk features")
    evidence_refs: List[Dict[str, Any]] = Field(default_factory=list, description="Evidence references")
    validators_run: List[str] = Field(default_factory=list, description="Validators executed")
    routing_outcome: Optional[str] = Field(None, description="Core routing outcome")
    decision_proposal: str = Field(..., description="Proposed decision")
    human_review_triggered: bool = Field(False, description="Human review triggered")
    determinism_digest: Optional[str] = Field(None, description="Determinism digest from core")

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "UW-2024-001234",
                "trace_id": "trace-abc-123",
                "policy_hash": "sha256:xyz789",
                "decision_proposal": "APPROVE_WITH_CONDITIONS",
                "human_review_triggered": False
            }
        }
