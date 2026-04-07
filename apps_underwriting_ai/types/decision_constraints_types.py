"""
Decision Constraints Types - Domain contracts for decision authority and timing.
"""

from pydantic import BaseModel, Field


class DecisionConstraints(BaseModel):
    """
    Constraints on underwriting decision authority and timing.
    """

    turnaround_sla_hours: int = Field(72, gt=0, description="SLA turnaround in hours")
    max_auto_approval_amount: float | None = Field(None, ge=0, description="Max auto-approval authority")
    require_human_if_policy_exception: bool = Field(True, description="Require human on policy exception")
    require_human_if_docs_missing: bool = Field(True, description="Require human if docs missing")
    require_human_if_risk_score_borderline: bool = Field(True, description="Require human on borderline risk")

    class Config:
        json_schema_extra = {
            "example": {
                "turnaround_sla_hours": 72,
                "max_auto_approval_amount": 5000000.0,
                "require_human_if_policy_exception": True,
                "require_human_if_docs_missing": True,
                "require_human_if_risk_score_borderline": True,
            },
        }
