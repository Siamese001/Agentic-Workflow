# FILE: models.py
"""
Unified Runtime Models (v10_9) — FULL AGENTIC IMPLEMENTATION

This module defines all canonical data structures used across the
v10_9 agentic architecture:

    • PlanObject          (L1 plan output)
    • ExecutionResult     (L2 execution output)
    • WorkflowState       (L3 orchestration output)
    • StatePatch          (L4 patch container)
    • PhaseMetadata       (L3 phase metadata)
    • NodeStatus          (status enum)
    • WorkflowPhase       (phase enum)

Pure models:
    • NO cognition (L1)
    • NO execution (L2)
    • NO orchestration (L3)
    • NO state mutation (L4)
    • NO safety/policy logic (L5)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional, List, Iterable
import copy
import enum


# =============================================================================
# 1. CANONICAL ENUMS
# =============================================================================

class NodeStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"


class WorkflowPhase(str, enum.Enum):
    INIT       = "init"
    PLANNING   = "planning"
    EXECUTING  = "executing"
    REVIEWING  = "reviewing"
    COMPLETE   = "complete"
    FAILED     = "failed"


# =============================================================================
# 2. BASE DICT-BACKED OBJECT
# =============================================================================

class DictBacked:
    """
    Base class that wraps a Python dict but provides:
        • attribute-style access
        • defensive copying
        • .get(), .set(), .update()
        • .to_dict()
        • deep_clone()
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        object.__setattr__(self, "_data", data or {})

    # --- attribute access -----------------------------------------------------

    def __getattr__(self, key: str) -> Any:
        if key in self._data:
            return self._data[key]
        raise AttributeError(f"{key!r} not found in {type(self).__name__}")

    def __setattr__(self, key: str, value: Any) -> None:
        self._data[key] = value

    # --- mapping style --------------------------------------------------------

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def update(self, other: Dict[str, Any]) -> None:
        self._data.update(other)

    # --- serialization --------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return copy.deepcopy(self._data)

    def deep_clone(self) -> "DictBacked":
        return type(self)(copy.deepcopy(self._data))

    # --- representation -------------------------------------------------------

    def __repr__(self):
        return f"{type(self).__name__}({self._data!r})"


# =============================================================================
# 3. PLAN OBJECT (L1 → L2 contract)
# =============================================================================

class PlanObject(DictBacked):
    """
    Describes the full L1 cognitive plan for L2 execution.

    Examples of required fields (depending on mode):
        • mode: "strategy" | "rag" | "drafting" | ...
        • objective: str
        • steps / branches / checks / rules
        • handoff: {target_layer: "l2", preferred_executor: "..."}
        • injection_framing / injection_reasoning
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        super().__init__(data or {})

    def copy(self) -> "PlanObject":
        return PlanObject(self.to_dict())


# =============================================================================
# 4. EXECUTION RESULT (L2 → L3 contract)
# =============================================================================

class ExecutionResult:
    """
    Normalized deterministic output for all L2 executors.

    Fields:
        • status: "success" | "failure"
        • payload: dict
        • model: str
        • usage: dict
    """

    SUCCESS = "success"
    FAILURE = "failure"

    def __init__(
        self,
        status: str,
        payload: Dict[str, Any],
        model: str,
        usage: Optional[Dict[str, Any]] = None,
    ):
        self.status = status
        self.payload = payload
        self.model = model
        self.usage = usage or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "payload": copy.deepcopy(self.payload),
            "model": self.model,
            "usage": copy.deepcopy(self.usage),
        }

    def __repr__(self):
        return f"ExecutionResult(status={self.status}, model={self.model})"


# =============================================================================
# 5. WORKFLOW STATE (L3 → external API)
# =============================================================================

@dataclass
class WorkflowState:
    """
    Final output of the L3 orchestrator for a single execution pass.

    Fields:
        • workflow_id: str
        • phase: WorkflowPhase
        • nodes: dict (empty in 10_9 but retained for future graph support)
        • state: full context state dict
        • phase_metadata: dict
    """
    workflow_id: str
    phase: str
    nodes: Dict[str, Any]
    state: Dict[str, Any]
    phase_metadata: Dict[str, Any]


# =============================================================================
# 6. STATE PATCH (L4 contract)
# =============================================================================

@dataclass
class StatePatch:
    """
    A typed patch container for L4. This is used to hold structured
    updates from L2/L3 before StateAdapter applies them.
    """
    key: str
    value: Any
    scope: str = "local"   # reserved for multi-agent or multi-session contexts


# =============================================================================
# 7. PHASE METADATA
# =============================================================================

@dataclass
class PhaseMetadata:
    """
    Annotates a workflow phase with context (e.g., reason for transition).
    """
    phase: str
    note: str = ""


# =============================================================================
# 8. TRACE SPAN / OBSERVABILITY (optional)
# =============================================================================

@dataclass
class TraceSpan:
    """
    Simple trace span for L2/L3/L4 observability.
    """
    name: str
    start_ms: float
    end_ms: float
    tags: Dict[str, Any] = field(default_factory=dict)

    def duration_ms(self) -> float:
        return max(0.0, self.end_ms - self.start_ms)


# =============================================================================
# 9. EVENT ENVELOPE (for future unified telemetry)
# =============================================================================

@dataclass
class EventEnvelope:
    """
    Generic event envelope for optional global telemetry integration.
    """
    event: str
    timestamp: float
    payload: Dict[str, Any]
