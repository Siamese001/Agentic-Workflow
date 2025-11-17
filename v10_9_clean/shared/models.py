# models.py
"""
Shared Models — v10_9

Defines core data structures used across L1–L5:
    • V10Model (base)
    • PlanObject (L1)
    • ExecutionResult, ToolCallResult (L2)
    • WorkflowState, PhaseMetadata (L3)
    • StatePatch (L4)
    • BudgetConfig, Message (L4 memory)
    • Safety + QA contracts (L5)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .constants import NodeStatus, WorkflowPhase


# ======================================================================
# BASE MODEL
# ======================================================================

class V10Model(BaseModel):
    class Config:
        extra = "allow"
        allow_mutation = True
        validate_assignment = True


# ======================================================================
# MEMORY SUPPORT TYPES
# ======================================================================

class Message(V10Model):
    role: str
    content: str


class BudgetConfig(V10Model):
    max_messages: int = 50
    max_rag_items: int = 30
    max_world_items: int = 50
    max_summary_chars: int = 2000
    max_prompt_tokens: int = 4000
    max_retrieval_tokens: int = 4000


# ======================================================================
# L1 PLAN OBJECT (structure only)
# ======================================================================

class PlanObject(V10Model):
    plan_id: str
    description: str
    steps: List[Dict[str, Any]] = Field(default_factory=list)

    rationale: Optional[str] = None
    layer: Optional[str] = None
    mode: Optional[str] = None

    objective: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    sections: List[str] = Field(default_factory=list)

    tone: Optional[str] = None
    audience: Optional[str] = None

    retrieval: Dict[str, Any] = Field(default_factory=dict)
    ranking: Dict[str, Any] = Field(default_factory=dict)
    retrieval_metadata: Dict[str, Any] = Field(default_factory=dict)

    injection_framing: Dict[str, Any] = Field(default_factory=dict)
    injection_reasoning: Dict[str, Any] = Field(default_factory=dict)
    safety_metadata: Dict[str, Any] = Field(default_factory=dict)

    handoff: Dict[str, Any] = Field(default_factory=dict)


# ======================================================================
# L2 RESULTS
# ======================================================================

class ExecutionResult(V10Model):
    status: NodeStatus
    payload: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None
    error_type: Optional[str] = None
    model: Optional[str] = None
    usage: Dict[str, Any] = Field(default_factory=dict)


class ToolCallResult(V10Model):
    results: List[ExecutionResult]
    final_payload: Dict[str, Any] = Field(default_factory=dict)


# ======================================================================
# L3 WORKFLOW STATE
# ======================================================================

class PhaseMetadata(V10Model):
    phase: WorkflowPhase
    note: Optional[str] = None
    timestamp: Optional[float] = None


class WorkflowState(V10Model):
    workflow_id: str
    phase: WorkflowPhase
    nodes: Dict[str, ExecutionResult] = Field(default_factory=dict)
    state: Dict[str, Any] = Field(default_factory=dict)
    phase_metadata: Optional[PhaseMetadata] = None


# ======================================================================
# L4 PATCH
# ======================================================================

class StatePatch(V10Model):
    key: str
    value: Any
    scope: str = "local"


# ======================================================================
# L5 CONTRACTS (LIGHTWEIGHT)
# ======================================================================

class QAResult(V10Model):
    answer: str
    confidence: float = 0.0
    evidence: List[str] = Field(default_factory=list)


class SafetyReport(V10Model):
    is_safe: bool
    redactions: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggested_rewrite: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ArbitrationDecision(V10Model):
    decision: str
    rationale: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
