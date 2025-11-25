"""Core DAG execution models for workflow orchestration."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, UTC
from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Generic

from l4.types import StateSnapshot, StateTransition
from l5.types import PolicyDecision, Verdict


T = TypeVar("T")


class NodeStatus(str, Enum):
    """Execution status of a workflow node."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"  # Blocked by safety check


@dataclass
class NodeExecutionResult(Generic[T]):
    """Result of executing a single node in the workflow DAG."""

    node_id: str
    status: NodeStatus
    output: Optional[T] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

    # L4 integration: state linkage
    state_snapshot_id: Optional[str] = None
    state_transition_id: Optional[str] = None

    # L5 integration: safety decision for this node
    safety_decision: Optional[PolicyDecision] = None

    @property
    def duration_seconds(self) -> Optional[float]:
        """Execution duration in seconds, if both endpoints are present."""

        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class DAGResult:
    """Result of executing a workflow DAG, including L4 and L5 integration."""

    workflow_id: str
    status: str
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    node_results: Dict[str, NodeExecutionResult[Any]] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)

    # L4 integration
    state_snapshots: Dict[str, StateSnapshot] = field(default_factory=dict)
    state_transitions: List[StateTransition] = field(default_factory=list)

    # L5 integration
    safety_decisions: Dict[str, PolicyDecision] = field(default_factory=dict)
    safety_verdict: Verdict = Verdict.ALLOW

    def __post_init__(self) -> None:
        if self.end_time is None:
            self.end_time = datetime.now(UTC)

        if self.safety_decisions:
            if any(decision.verdict == Verdict.BLOCK for decision in self.safety_decisions.values()):
                self.safety_verdict = Verdict.BLOCK
            elif any(decision.verdict == Verdict.REVIEW for decision in self.safety_decisions.values()):
                self.safety_verdict = Verdict.REVIEW
            else:
                self.safety_verdict = Verdict.ALLOW

    @property
    def is_successful(self) -> bool:
        """True if the workflow completed and was not blocked by safety."""

        return self.status == "completed" and self.safety_verdict != Verdict.BLOCK

    @property
    def duration_seconds(self) -> float:
        """Total DAG execution duration in seconds."""

        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()

    def add_node_result(self, node_id: str, result: NodeExecutionResult[Any]) -> None:
        """Register a node execution result and update safety aggregation."""

        self.node_results[node_id] = result

        if result.safety_decision is not None:
            self.safety_decisions[node_id] = result.safety_decision
            # Re-evaluate aggregate verdict
            self.__post_init__()

    def to_dict(self) -> Dict[str, Any]:
        """Shallow serialization helper for logging/telemetry."""

        return {
            "workflow_id": self.workflow_id,
            "status": self.status,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "is_successful": self.is_successful,
            "safety_verdict": self.safety_verdict.value,
            "node_count": len(self.node_results),
            "metrics": self.metrics,
            "node_results": {
                nid: {
                    "status": r.status.value,
                    "duration_seconds": r.duration_seconds,
                    "error": r.error,
                    "safety_verdict": (
                        r.safety_decision.verdict.value if r.safety_decision else None
                    ),
                }
                for nid, r in self.node_results.items()
            },
        }



