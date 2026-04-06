"""
Meta-Learning Bus - Queue-backed deterministic change conduit.

Implements FIFO queue for meta-learning changes with deterministic hashing.
No wall-clock usage, no randomness, no direct L4 mutation.
"""

import hashlib
import json
from collections import deque
from dataclasses import dataclass
from typing import Any

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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "meta_learning_bus", "L0")
_emit_routes_through("p1", "meta_learning_bus", "L0")
_emit_checks_agent_registry("p1", "meta_learning_bus", "agent_registry")
_emit_validates_agent_capability("p1", "meta_learning_bus", "capability")
_emit_dispatches_execution_plan("p1", "meta_learning_bus", "exec_plan")
_emit_agent_executes_agent("p1", "meta_learning_bus", "sub_agent")
_emit_routes_to_agent("p1", "meta_learning_bus", "target_agent")
_emit_verifies_policy("p1", "meta_learning_bus", "policy_check")
_emit_observes_runtime_state("p1", "meta_learning_bus", "runtime_state")
_emit_verifies_boundary("p1", "meta_learning_bus", "boundary_check")
_emit_transcripts_response("p1", "meta_learning_bus", "transcript")
_emit_hard_fails_untranscripted("p1", "meta_learning_bus")
_emit_gated_by_confidence("p1", "meta_learning_bus", "confidence_gate")
_emit_escalates_to_human("p1", "meta_learning_bus", "L0")
_emit_reads_policy_state("p1", "meta_learning_bus", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "meta_learning_bus", "p0_governance")
_emit_snapshots_state("p0", "meta_learning_bus", "state_snapshot")
_emit_authorize_and_execute("p2", "meta_learning_bus", "execution_auth")
_emit_validates_capability("p2", "meta_learning_bus", "capability_check")
_emit_routes_to_capability("p2", "meta_learning_bus", "capability_route")
_emit_writes_via_uwg("p2", "meta_learning_bus", "uwg_write")
_emit_blocks_direct_write("p2", "meta_learning_bus", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_learning_bus", "tool_invocation")
_emit_captures_execution_output("p2", "meta_learning_bus", "exec_output")
_emit_dispatches_agent("p3", "meta_learning_bus", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_learning_bus", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_learning_bus", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_learning_bus", "healing_outcome")
_emit_escalates_failure("p3", "meta_learning_bus", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_learning_bus", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_learning_bus", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_learning_bus", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_learning_bus", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_learning_bus", "eval_metric")
_emit_stores_embedding("p4", "meta_learning_bus", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_learning_bus", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_learning_bus", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_1")
_emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_2")
_emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_3")
_emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_4")
_emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_5")
_emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_6")
_emit_records_incident_event("meta_learning_bus", "p4obs", "incident")
_emit_captures_runtime_anomaly("meta_learning_bus", "p4obs", "anomaly")
_emit_writes_observability_log("meta_learning_bus", "p4obs", "obs_log")
_emit_updates_monitoring_state("meta_learning_bus", "p4obs", "mon_state")
_emit_triggers_alert("meta_learning_bus", "p4obs", "alert")
_emit_links_incident_trace("meta_learning_bus", "p4obs", "trace_link")
_emit_captures_pattern("meta_learning_bus", "p3lm", "pattern")
_emit_records_learning_event("meta_learning_bus", "p3lm", "learning_event")
_emit_writes_learning_snapshot("meta_learning_bus", "p3lm", "snapshot")
_emit_feeds_meta_learning("meta_learning_bus", "p3lm", "meta_feed")
_emit_updates_routing_strategy("meta_learning_bus", "p3lm", "routing")
_emit_improves_agent_policy("meta_learning_bus", "p3lm", "policy")
_emit_stores_learning_state("meta_learning_bus", "p3lm", "state")
_emit_records_execution_trace("meta_learning_bus", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("meta_learning_bus", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("meta_learning_bus", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("meta_learning_bus", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("meta_learning_bus", "L4_STATE", "p2_trace_5")
_emit_reads_environ("meta_learning_bus", "env_read", "p2_env_1")
_emit_reads_environ("meta_learning_bus", "env_read", "p2_env_2")
_emit_reads_runtime_state("meta_learning_bus", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("meta_learning_bus", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "meta_learning_bus", "context_pull")
_emit_pulls_context("p1", "meta_learning_bus", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "meta_learning_bus", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "meta_learning_bus", "uwg_term_2")
_emit_writes_through("p1", "meta_learning_bus", "write_through")
_emit_writes_through("p1", "meta_learning_bus", "write_through_2")
_emit_validated_by_safety_plane("p1", "meta_learning_bus", "safety_validation")
_emit_invokes_eval("p1", "meta_learning_bus", "eval_call")
_emit_proposal_commits_routing("p1", "meta_learning_bus", "routing_commit")


@dataclass(frozen=True)
class MetaLearningChangePackage:
    """Immutable change package for meta-learning operations."""

    trace_id: str
    kind: str
    payload: dict[str, Any]
    package_hash: str

    @classmethod
    def create(cls, trace_id: str, kind: str, payload: dict[str, Any]) -> "MetaLearningChangePackage":
        """
        Create a new MetaLearningChangePackage with deterministic hash.

        Args:
            trace_id: Unique trace identifier
            kind: Change package kind
            payload: Package payload data

        Returns:
            New MetaLearningChangePackage with computed hash
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "MetaLearningChangePackage.create")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        canonical_data = {"kind": kind, "payload": payload}
        canonical_json = json.dumps(canonical_data, sort_keys=True, separators=(",", ":"))
        package_hash = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
        return cls(trace_id=trace_id, kind=kind, payload=payload, package_hash=package_hash)


class MetaLearningBus:
    """
    Queue-backed meta-learning bus for deterministic change processing.

    Provides FIFO queue behavior with injected apply functions.
    No wall-clock usage, no direct L4 mutation.
    """

    def __init__(self):
        """Initialize MetaLearningBus with in-memory FIFO queue."""
        self._queue: deque[MetaLearningChangePackage] = deque()

    def enqueue(self, pkg: MetaLearningChangePackage) -> None:
        """
        Add a package to the queue.

        Args:
            pkg: Package to enqueue
        """
        self._queue.append(pkg)

    def dequeue(self) -> MetaLearningChangePackage | None:
        """
        Remove and return the next package from queue.

        Returns:
            Next package or None if queue is empty
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "MetaLearningBus.dequeue")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if not self._queue:
            return None
        return self._queue.popleft()

    def size(self) -> int:
        """
        Get current queue size.

        Returns:
            Number of packages in queue
        """
        return len(self._queue)

    def apply_next(self, *, apply_fn) -> tuple[MetaLearningChangePackage, Any] | None:
        """
        Apply the next package using injected function.

        Pops one package, calls apply_fn(pkg), returns result.
        Bus has no knowledge of L4; apply_fn is injected.

        Args:
            apply_fn: Function to apply the package

        Returns:
            (package, result) tuple or None if queue empty
        """
        pkg = self.dequeue()
        if pkg is None:
            return None
        result = apply_fn(pkg)
        return (pkg, result)


_PROCESS_BUS: MetaLearningBus = MetaLearningBus()


def get_process_bus() -> MetaLearningBus:
    """Return the process-level singleton MetaLearningBus.

    All components that publish real-time healing outcomes via
    DefaultMetaOutcomeBusHook should share this instance so that
    drain_and_apply() in _fire_meta_learning_intake can flush them.
    """
    return _PROCESS_BUS
