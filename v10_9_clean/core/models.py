"""Data models for the v10_7 runtime layer."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .constants import NodeStatus, WorkflowPhase


class V10Model(BaseModel):
    """Base model that tolerates forward-compatible fields."""

    class Config:
        extra = "allow"
        allow_mutation = True


class NodeResult(V10Model):
    """Canonical node execution result for DAG execution."""

    status: NodeStatus
    payload: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None
    error_type: Optional[str] = None
    phase: WorkflowPhase = WorkflowPhase.EXECUTION


class StatePatch(V10Model):
    """Lightweight state mutation payload."""

    key: str
    value: Any
    scope: str = "local"


class MainGraphState(V10Model):
    """Top-level state container for orchestration contexts."""

    workflow_id: str
    phase: WorkflowPhase
    nodes: Dict[str, NodeResult] = Field(default_factory=dict)
    state: Dict[str, Any] = Field(default_factory=dict)


class QAOutputModel(V10Model):
    """Model for QA agent outputs."""

    answer: str
    confidence: float = 0.0
    supporting_evidence: List[str] = Field(default_factory=list)


class StrategyModel(V10Model):
    """Model describing strategy selection results."""

    strategy: str
    rationale: Optional[str] = None
    options: List[str] = Field(default_factory=list)


class RAGModel(V10Model):
    """Model for RAG retrieval responses."""

    query: str
    documents: List[str] = Field(default_factory=list)
    snippets: List[str] = Field(default_factory=list)


class DraftModel(V10Model):
    """Model for draft generation."""

    content: str
    notes: Optional[str] = None
    tokens_used: int = 0


def canonical_model_name(model_name: str, aliases: Optional[Dict[str, str]] = None) -> str:
    """Resolve a model name to its canonical identifier."""

    if aliases is None:
        aliases = {}
    if not model_name:
        return model_name
    lowered = model_name.lower()
    return aliases.get(lowered, model_name)
