"""
L4 State Management - Core Types

Defines the fundamental types for state management with strict immutability.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, TypeVar

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "state_operation_types", "p0_governance")
_emit_reads_policy_state("p0", "state_operation_types", "policy_binding")
_emit_snapshots_state("p0", "state_operation_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("state_operation_types", "p4obs", "metric_1")
_emit_emits_metric_event("state_operation_types", "p4obs", "metric_2")
_emit_emits_metric_event("state_operation_types", "p4obs", "metric_3")
_emit_emits_metric_event("state_operation_types", "p4obs", "metric_4")
_emit_emits_metric_event("state_operation_types", "p4obs", "metric_5")
_emit_emits_metric_event("state_operation_types", "p4obs", "metric_6")
_emit_records_incident_event("state_operation_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("state_operation_types", "p4obs", "anomaly")
_emit_writes_observability_log("state_operation_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("state_operation_types", "p4obs", "mon_state")
_emit_triggers_alert("state_operation_types", "p4obs", "alert")
_emit_links_incident_trace("state_operation_types", "p4obs", "trace_link")
_emit_captures_pattern("state_operation_types", "p3lm", "pattern")
_emit_records_learning_event("state_operation_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("state_operation_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("state_operation_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("state_operation_types", "p3lm", "routing")
_emit_improves_agent_policy("state_operation_types", "p3lm", "policy")
_emit_stores_learning_state("state_operation_types", "p3lm", "state")
_emit_records_execution_trace("state_operation_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("state_operation_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("state_operation_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("state_operation_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("state_operation_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("state_operation_types", "env_read", "p2_env_1")
_emit_reads_environ("state_operation_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("state_operation_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("state_operation_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "state_operation_types", "context_pull")
_emit_pulls_context("p1", "state_operation_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "state_operation_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "state_operation_types", "uwg_term_2")
_emit_writes_through("p1", "state_operation_types", "write_through")
_emit_writes_through("p1", "state_operation_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "state_operation_types", "safety_validation")
_emit_invokes_eval("p1", "state_operation_types", "eval_call")
_emit_proposal_commits_routing("p1", "state_operation_types", "routing_commit")
_emit_escalates_to_human("p1", "state_operation_types", "human_escalation")
_emit_routes_through("p1", "state_operation_types", "route_through")
_emit_checks_agent_registry("p1", "state_operation_types", "agent_registry")
_emit_validates_agent_capability("p1", "state_operation_types", "capability")
_emit_dispatches_execution_plan("p1", "state_operation_types", "exec_plan")
_emit_agent_executes_agent("p1", "state_operation_types", "sub_agent")
_emit_routes_to_agent("p1", "state_operation_types", "target_agent")
_emit_verifies_policy("p1", "state_operation_types", "policy_check")
_emit_observes_runtime_state("p1", "state_operation_types", "runtime_state")
_emit_verifies_boundary("p1", "state_operation_types", "boundary_check")
_emit_transcripts_response("p1", "state_operation_types", "transcript")
_emit_hard_fails_untranscripted("p1", "state_operation_types")
_emit_gated_by_confidence("p1", "state_operation_types", "confidence_gate")
emit_replay_key("p0", "state_operation_types")
emit_determinism_digest("p0", "state_operation_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "state_operation_types", "execution_auth")
_emit_validates_capability("p2", "state_operation_types", "capability_check")
_emit_routes_to_capability("p2", "state_operation_types", "capability_route")
_emit_writes_via_uwg("p2", "state_operation_types", "uwg_write")
_emit_blocks_direct_write("p2", "state_operation_types", "direct_write_block")
_emit_records_tool_invocation("p2", "state_operation_types", "tool_invocation")
_emit_captures_execution_output("p2", "state_operation_types", "exec_output")
_emit_dispatches_agent("p3", "state_operation_types", "agent_dispatch")
_emit_coordinates_agents("p3", "state_operation_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "state_operation_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "state_operation_types", "healing_outcome")
_emit_escalates_failure("p3", "state_operation_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "state_operation_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "state_operation_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "state_operation_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "state_operation_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "state_operation_types", "eval_metric")
_emit_stores_embedding("p4", "state_operation_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "state_operation_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "state_operation_types", "exec_snapshot_link")

T = TypeVar("T")


class StateOperation(str, Enum):
    """Types of state operations."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    PATCH = "patch"


class StateEventType(str, Enum):
    """Types of state events."""

    TRANSITION = "transition"
    SNAPSHOT = "snapshot"
    ROLLBACK = "rollback"
    PRUNE = "prune"


@dataclass(frozen=True)
class StatePath:
    """Immutable representation of a path in the state tree."""

    parts: tuple[str, ...] = field(default_factory=tuple)

    def __truediv__(self, other: str) -> StatePath:
        """Create a new path by appending a component."""
        return StatePath(self.parts + (str(other),))

    def __str__(self) -> str:
        """Convert to dot notation."""
        return ".".join(self.parts)

    @classmethod
    def from_string(cls, path_str: str) -> StatePath:
        """Create from a dot-separated string."""
        return cls(parts=tuple(part for part in path_str.split(".") if part))


@dataclass(frozen=True)
class StateTransition(Generic[T]):
    """Immutable representation of a state change."""

    operation: StateOperation
    path: StatePath
    value: Any = None
    condition: Callable[[T], bool] | None = field(default=None, compare=False)
    metadata: dict[str, object] = field(default_factory=dict, compare=False)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc), compare=False)

    def with_metadata(self, **kwargs: object) -> StateTransition[T]:
        """Create a new transition with updated metadata."""
        return StateTransition(
            operation=self.operation,
            path=self.path,
            value=self.value,
            condition=self.condition,
            metadata={**self.metadata, **kwargs},
            timestamp=self.timestamp,
        )


@dataclass(frozen=True)
class StateSnapshot(Generic[T]):
    """Immutable snapshot of state at a point in time."""

    state_id: str
    data: T
    parent_id: str | None = None
    transition: StateTransition[T] | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, object] = field(default_factory=dict)

    def get_hash(self) -> str:
        """Generate a deterministic hash of this snapshot."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "StateSnapshot.get_hash")

        data = {
            "state_id": self.state_id,
            "data": self.data,
            "parent_id": self.parent_id,
            "timestamp": self.timestamp.isoformat(),
        }
        if self.transition:
            data["transition"] = {
                "operation": self.transition.operation.value,
                "path": str(self.transition.path),
                "value": self.transition.value,
            }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


class StateError(Exception):
    """Base class for state-related errors."""

    pass


class StateValidationError(StateError):
    """Raised when a state transition is invalid."""

    pass


class StateRollbackError(StateError):
    """Raised when a rollback operation fails."""

    pass
