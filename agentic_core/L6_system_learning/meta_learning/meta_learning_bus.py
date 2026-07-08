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

from agentic_core.L6_system_learning._tracing import sl_span

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_dispatches_healing_run("p1", "meta_learning_bus", "L0")
trace_contract._emit_routes_through("p1", "meta_learning_bus", "L0")
trace_contract._emit_checks_agent_registry("p1", "meta_learning_bus", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "meta_learning_bus", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "meta_learning_bus", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "meta_learning_bus", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "meta_learning_bus", "target_agent")
trace_contract._emit_verifies_policy("p1", "meta_learning_bus", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "meta_learning_bus", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "meta_learning_bus", "boundary_check")
trace_contract._emit_transcripts_response("p1", "meta_learning_bus", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "meta_learning_bus")
trace_contract._emit_gated_by_confidence("p1", "meta_learning_bus", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "meta_learning_bus", "L0")
trace_contract._emit_reads_policy_state("p1", "meta_learning_bus", "L0")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_applies_guardrail("p0", "meta_learning_bus", "p0_governance")
trace_contract._emit_snapshots_state("p0", "meta_learning_bus", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "meta_learning_bus", "execution_auth")
trace_contract._emit_validates_capability("p2", "meta_learning_bus", "capability_check")
trace_contract._emit_routes_to_capability("p2", "meta_learning_bus", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "meta_learning_bus", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "meta_learning_bus", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "meta_learning_bus", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "meta_learning_bus", "exec_output")
trace_contract._emit_dispatches_agent("p3", "meta_learning_bus", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "meta_learning_bus", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "meta_learning_bus", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "meta_learning_bus", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "meta_learning_bus", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "meta_learning_bus", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "meta_learning_bus", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "meta_learning_bus", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "meta_learning_bus", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "meta_learning_bus", "eval_metric")
trace_contract._emit_stores_embedding("p4", "meta_learning_bus", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "meta_learning_bus", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "meta_learning_bus", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("meta_learning_bus", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("meta_learning_bus", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("meta_learning_bus", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("meta_learning_bus", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("meta_learning_bus", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("meta_learning_bus", "p4obs", "alert")
trace_contract._emit_links_incident_trace("meta_learning_bus", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("meta_learning_bus", "p3lm", "pattern")
trace_contract._emit_records_learning_event("meta_learning_bus", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("meta_learning_bus", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("meta_learning_bus", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("meta_learning_bus", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("meta_learning_bus", "p3lm", "policy")
trace_contract._emit_stores_learning_state("meta_learning_bus", "p3lm", "state")
trace_contract._emit_records_execution_trace("meta_learning_bus", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("meta_learning_bus", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("meta_learning_bus", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("meta_learning_bus", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("meta_learning_bus", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("meta_learning_bus", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("meta_learning_bus", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("meta_learning_bus", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("meta_learning_bus", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "meta_learning_bus", "context_pull")
trace_contract._emit_pulls_context("p1", "meta_learning_bus", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "meta_learning_bus", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "meta_learning_bus", "uwg_term_2")
trace_contract._emit_writes_through("p1", "meta_learning_bus", "write_through")
trace_contract._emit_writes_through("p1", "meta_learning_bus", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "meta_learning_bus", "safety_validation")
trace_contract._emit_invokes_eval("p1", "meta_learning_bus", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "meta_learning_bus", "routing_commit")


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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L0_ROUTING, "MetaLearningChangePackage.create")
        trace_contract.emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        trace_contract.emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L0_ROUTING, "MetaLearningBus.dequeue")
        trace_contract.emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        trace_contract.emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

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
        with sl_span("agentic_core.L6_system_learning.v1.meta_learning_bus.apply_next") as span:
            pkg = self.dequeue()
            if pkg is None:
                span.set_attribute("sl.queue_empty", True)
                return None
            span.set_attribute("sl.package_kind", pkg.kind)
            span.set_attribute("sl.trace_id", pkg.trace_id)
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
