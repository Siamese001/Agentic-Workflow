"""
Canonical data models for the v10_9 runtime.

This module provides the strongly-typed schemas used across:
  • L1 reasoning (PlanObject)
  • L2 execution (ExecutionResult, ToolCallResult)
  • L3 orchestration (WorkflowState, Phase metadata)
  • L4 state transitions (StatePatch)
  • L5 safety + QA (SafetyReport, QAResult)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .constants import NodeStatus, WorkflowPhase


# ======================================================================
# BASE MODEL (FORWARD COMPATIBLE)
# ======================================================================

class V10Model(BaseModel):
    """Base Pydantic model that tolerates forward-compatible fields."""

    class Config:
        extra = "allow"
        allow_mutation = True
        validate_assignment = True


# ======================================================================
# L1 — PLAN MODEL
# ======================================================================

class PlanObject(V10Model):
    """
    Output of L1 (Cognition Layer).

    Contains:
      • selected tools / actions
      • reasoning summary
      • routing decisions
    """

    plan_id: str
    description: str
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    rationale: Optional[str] = None
    cost_estimate_tokens: Optional[int] = None


# ======================================================================
# L2 — EXECUTION MODELS
# ======================================================================

class ExecutionResult(V10Model):
    """
    Canonical L2 tool result.

    Fields:
      • status
      • output payload
      • error metadata (if any)
    """

    status: NodeStatus
    payload: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None
    error_type: Optional[str] = None
    model: Optional[str] = None
    usage: Dict[str, Any] = Field(default_factory=dict)


class ToolCallResult(V10Model):
    """Wrapper for multi-tool toolchains."""

    results: List[ExecutionResult]
    final_payload: Dict[str, Any] = Field(default_factory=dict)


# ======================================================================
# L3 — WORKFLOW / ORCHESTRATION MODELS
# ======================================================================

class PhaseMetadata(V10Model):
    """Optional metadata for a workflow phase."""

    phase: WorkflowPhase
    note: Optional[str] = None
    timestamp: Optional[float] = None


class WorkflowState(V10Model):
    """
    Canonical state container used by L3 orchestrator.

    Contains:
      • workflow_id
      • current phase
      • node results
      • global working state (L4 StateAdapter holds the authoritative state)
    """

    workflow_id: str
    phase: WorkflowPhase
    nodes: Dict[str, ExecutionResult] = Field(default_factory=dict)
    state: Dict[str, Any] = Field(default_factory=dict)
    phase_metadata: Optional[PhaseMetadata] = None


# ======================================================================
# L4 — STATE PATCH / LOW-LEVEL STATE
# ======================================================================

class StatePatch(V10Model):
    """
    Lightweight deterministic state mutation instruction.

    Fields:
      • key – dotted path or simple key
      • value – replacement value
      • scope – "local", "session", "global"
    """

    key: str
    value: Any
    scope: str = "local"


# ======================================================================
# L5 — SAFETY / QA / ARBITRATION MODELS
# ======================================================================

class QAResult(V10Model):
    """Model for QA agent output."""

    answer: str
    confidence: float = 0.0
    evidence: List[str] = Field(default_factory=list)


class SafetyReport(V10Model):
    """
    Safety / constitutional AI output.

    Fields:
      • is_safe
      • redactions
      • warnings
      • suggested_rewrite
    """

    is_safe: bool
    redactions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggested_rewrite: Optional[str] = None


class ArbitrationDecision(V10Model):
    """
    L5 Arbitration Engine decision.

    Allowed actions:
      • "accept"
      • "retry"
      • "replan"
      • "halt"
      • "fail"
    """

    decision: str
    rationale: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ======================================================================
# GENERAL UTILS
# ======================================================================

def canonical_model_name(model_name: str, aliases: Optional[Dict[str, str]] = None) -> str:
    """Resolve a model name to its canonical identifier."""
    if not model_name:
        return model_name

    aliases = aliases or {}
    lowered = model_name.lower()
    return aliases.get(lowered, model_name)
