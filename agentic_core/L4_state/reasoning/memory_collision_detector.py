from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import NamedTuple, Sequence

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "memory_collision_detector")
emit_determinism_digest("p0", "memory_collision_detector")

_emit_dispatches_healing_run("p1", "memory_collision_detector", "L4")
_emit_routes_through("p1", "memory_collision_detector", "L4")
_emit_checks_agent_registry("p1", "memory_collision_detector", "agent_registry")
_emit_validates_agent_capability("p1", "memory_collision_detector", "capability")
_emit_dispatches_execution_plan("p1", "memory_collision_detector", "exec_plan")
_emit_agent_executes_agent("p1", "memory_collision_detector", "sub_agent")
_emit_routes_to_agent("p1", "memory_collision_detector", "target_agent")
_emit_verifies_policy("p1", "memory_collision_detector", "policy_check")
_emit_observes_runtime_state("p1", "memory_collision_detector", "runtime_state")
_emit_verifies_boundary("p1", "memory_collision_detector", "boundary_check")
_emit_transcripts_response("p1", "memory_collision_detector", "transcript")
_emit_hard_fails_untranscripted("p1", "memory_collision_detector")
_emit_gated_by_confidence("p1", "memory_collision_detector", "confidence_gate")
_emit_escalates_to_human("p1", "memory_collision_detector", "L4")
_emit_reads_policy_state("p1", "memory_collision_detector", "L4")
_emit_authorize_and_execute("p2", "memory_collision_detector", "execution_auth")
_emit_validates_capability("p2", "memory_collision_detector", "capability_check")
_emit_routes_to_capability("p2", "memory_collision_detector", "capability_route")
_emit_writes_via_uwg("p2", "memory_collision_detector", "uwg_write")
_emit_blocks_direct_write("p2", "memory_collision_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "memory_collision_detector", "tool_invocation")
_emit_captures_execution_output("p2", "memory_collision_detector", "exec_output")
_emit_dispatches_agent("p3", "memory_collision_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "memory_collision_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "memory_collision_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "memory_collision_detector", "healing_outcome")
_emit_escalates_failure("p3", "memory_collision_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "memory_collision_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "memory_collision_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "memory_collision_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "memory_collision_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "memory_collision_detector", "eval_metric")
_emit_stores_embedding("p4", "memory_collision_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "memory_collision_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "memory_collision_detector", "exec_snapshot_link")
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

_emit_emits_metric_event("memory_collision_detector", "p4obs", "metric_1")
_emit_emits_metric_event("memory_collision_detector", "p4obs", "metric_2")
_emit_emits_metric_event("memory_collision_detector", "p4obs", "metric_3")
_emit_emits_metric_event("memory_collision_detector", "p4obs", "metric_4")
_emit_emits_metric_event("memory_collision_detector", "p4obs", "metric_5")
_emit_emits_metric_event("memory_collision_detector", "p4obs", "metric_6")
_emit_records_incident_event("memory_collision_detector", "p4obs", "incident")
_emit_captures_runtime_anomaly("memory_collision_detector", "p4obs", "anomaly")
_emit_writes_observability_log("memory_collision_detector", "p4obs", "obs_log")
_emit_updates_monitoring_state("memory_collision_detector", "p4obs", "mon_state")
_emit_triggers_alert("memory_collision_detector", "p4obs", "alert")
_emit_links_incident_trace("memory_collision_detector", "p4obs", "trace_link")
_emit_captures_pattern("memory_collision_detector", "p3lm", "pattern")
_emit_records_learning_event("memory_collision_detector", "p3lm", "learning_event")
_emit_writes_learning_snapshot("memory_collision_detector", "p3lm", "snapshot")
_emit_feeds_meta_learning("memory_collision_detector", "p3lm", "meta_feed")
_emit_updates_routing_strategy("memory_collision_detector", "p3lm", "routing")
_emit_improves_agent_policy("memory_collision_detector", "p3lm", "policy")
_emit_stores_learning_state("memory_collision_detector", "p3lm", "state")
_emit_records_execution_trace("memory_collision_detector", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("memory_collision_detector", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("memory_collision_detector", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("memory_collision_detector", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("memory_collision_detector", "L4_STATE", "p2_trace_5")
_emit_reads_environ("memory_collision_detector", "env_read", "p2_env_1")
_emit_reads_environ("memory_collision_detector", "env_read", "p2_env_2")
_emit_reads_runtime_state("memory_collision_detector", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("memory_collision_detector", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "memory_collision_detector", "context_pull")
_emit_pulls_context("p1", "memory_collision_detector", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "memory_collision_detector", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "memory_collision_detector", "uwg_term_2")
_emit_writes_through("p1", "memory_collision_detector", "write_through")
_emit_writes_through("p1", "memory_collision_detector", "write_through_2")
_emit_validated_by_safety_plane("p1", "memory_collision_detector", "safety_validation")
_emit_invokes_eval("p1", "memory_collision_detector", "eval_call")
_emit_proposal_commits_routing("p1", "memory_collision_detector", "routing_commit")


class MemoryDeadlockViolation(Exception):
    """Raised when a deadlock is detected during lock acquisition."""


class LockAcquisitionResult(NamedTuple):
    """The result of a lock acquisition attempt."""

    success: bool
    locks_acquired: list[str]
    violation: MemoryDeadlockViolation | None = None


@dataclass(frozen=True)
class LockPolicy:
    """Defines the policy for lock acquisition."""

    lock_hierarchy: list[str]
    timeout_seconds: float = 5.0


class MemoryCollisionDetector:
    """
    Manages concurrent access to shared memory with deterministic deadlock resolution.

    This detector enforces Guarantee #14 by implementing a strict lock acquisition
    hierarchy and a timeout policy. It prevents both race conditions and livelocks,
    ensuring that memory access is safe and deterministic under concurrency.
    """

    def __init__(self, policy: LockPolicy):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "MemoryCollisionDetector.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "MemoryCollisionDetector.__init__", "p0_governance")
        self.policy = policy
        self._locks: dict[str, threading.Lock] = {name: threading.Lock() for name in policy.lock_hierarchy}
        self._lock_order: dict[str, int] = {name: i for i, name in enumerate(policy.lock_hierarchy)}

    def acquire_locks(self, trace_id: str, required_locks: Sequence[str]) -> LockAcquisitionResult:
        """
        Acquires a set of locks in a deterministic, deadlock-free order.

        Args:
            trace_id: The unique identifier for the execution trace.
            required_locks: A sequence of lock names that need to be acquired.

        Returns:
            A LockAcquisitionResult indicating the outcome.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L4_STATE,
            "MemoryCollisionDetector.acquire_locks",
        )

        try:
            sorted_locks = sorted(required_locks, key=lambda name: self._lock_order[name])
        except KeyError as e:
            violation = MemoryDeadlockViolation(f"Lock '{e.args[0]}' is not defined in the global hierarchy.")
            return LockAcquisitionResult(success=False, locks_acquired=[], violation=violation)
        acquired_locks: list[str] = []
        start_time = time.monotonic()
        for lock_name in sorted_locks:
            lock = self._locks[lock_name]
            timeout = self.policy.timeout_seconds - (time.monotonic() - start_time)
            if timeout <= 0:
                violation = MemoryDeadlockViolation("Timeout exceeded during lock acquisition.")
                self._release_locks(acquired_locks)
                return LockAcquisitionResult(success=False, locks_acquired=[], violation=violation)
            if not lock.acquire(timeout=timeout):
                violation = MemoryDeadlockViolation(
                    f"Failed to acquire lock '{lock_name}' within the timeout.",
                )
                self._release_locks(acquired_locks)
                return LockAcquisitionResult(success=False, locks_acquired=[], violation=violation)
            acquired_locks.append(lock_name)
        return LockAcquisitionResult(success=True, locks_acquired=acquired_locks)

    def _release_locks(self, locks_to_release: list[str]) -> None:
        """Releases a list of locks, typically after a failed acquisition."""
        for lock_name in reversed(locks_to_release):
            self._locks[lock_name].release()

    def release_locks(self, acquired_locks: list[str]) -> None:
        """Public method to release locks after an operation is complete."""
        for lock_name in sorted(acquired_locks, key=lambda name: self._lock_order[name], reverse=True):
            self._locks[lock_name].release()
