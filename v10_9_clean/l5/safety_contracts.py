# safety_contracts.py
"""
L5 — Safety & Policy Contracts (v10_9)

Defines core schemas for:
    • SafetyReport
    • ArbitrationDecision

These are thin wrappers around shared model types, used to keep
L5 concerns clearly separated from the rest of the runtime.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SafetyReport(BaseModel):
    """
    Generic safety / policy report.

    Fields:
        is_safe: whether the content passes all checks
        redactions: a list of redacted spans or tokens
        warnings: human-readable explanations
        suggested_rewrite: optional safer version of content
        metadata: additional structured info (classifier scores, etc.)
    """

    is_safe: bool
    redactions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggested_rewrite: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ArbitrationDecision(BaseModel):
    """
    Safety arbitration decision.

    Allowed decisions:
        • accept
        • retry
        • replan
        • halt
        • fail
    """

    decision: str
    rationale: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"
        validate_assignment = True
