"""Data models used across the consolidated workflow."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    role: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyPlan:
    summary: str
    steps: List[str] = field(default_factory=list)


@dataclass
class RAGPlan:
    query: str
    sources: List[str] = field(default_factory=list)


@dataclass
class BulletPlan:
    bullets: List[str] = field(default_factory=list)


@dataclass
class DraftPlan:
    sections: List[str] = field(default_factory=list)


@dataclass
class QAResult:
    passed: bool
    findings: List[str] = field(default_factory=list)


@dataclass
class SafetyReport:
    safe: bool
    issues: List[str] = field(default_factory=list)


@dataclass
class HILDecision:
    requires_human: bool
    rationale: str = ""


@dataclass
class WorkflowConfig:
    model: str
    temperature: float
    max_tokens: int


@dataclass
class NodeResult:
    success: bool
    patch: Dict[str, Any] = field(default_factory=dict)
    message: str = ""


@dataclass
class MainGraphState:
    messages: List[Message] = field(default_factory=list)
    rag_history: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    world: List[Dict[str, Any]] = field(default_factory=list)
    session: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    phase: str = "init"
    phase_metadata: Dict[str, Any] = field(default_factory=dict)


StatePatch = Dict[str, Any]


__all__ = [
    "Message",
    "StrategyPlan",
    "RAGPlan",
    "BulletPlan",
    "DraftPlan",
    "QAResult",
    "SafetyReport",
    "HILDecision",
    "WorkflowConfig",
    "NodeResult",
    "MainGraphState",
    "StatePatch",
]
