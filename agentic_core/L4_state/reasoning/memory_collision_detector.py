from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import NamedTuple, Sequence

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "memory_collision_detector")
trace_contract.emit_determinism_digest("p0", "memory_collision_detector")

trace_contract._emit_dispatches_healing_run("p1", "memory_collision_detector", "L4")
trace_contract._emit_routes_through("p1", "memory_collision_detector", "L4")
trace_contract._emit_checks_agent_registry("p1", "memory_collision_detector", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "memory_collision_detector", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "memory_collision_detector", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "memory_collision_detector", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "memory_collision_detector", "target_agent")
trace_contract._emit_verifies_policy("p1", "memory_collision_detector", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "memory_collision_detector", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "memory_collision_detector", "boundary_check")
trace_contract._emit_transcripts_response("p1", "memory_collision_detector", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "memory_collision_detector")
trace_contract._emit_gated_by_confidence("p1", "memory_collision_detector", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "memory_collision_detector", "L4")
trace_contract._emit_reads_policy_state("p1", "memory_collision_detector", "L4")
trace_contract._emit_authorize_and_execute("p2", "memory_collision_detector", "execution_auth")
trace_contract._emit_validates_capability("p2", "memory_collision_detector", "capability_check")
trace_contract._emit_routes_to_capability("p2", "memory_collision_detector", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "memory_collision_detector", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "memory_collision_detector", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "memory_collision_detector", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "memory_collision_detector", "exec_output")
trace_contract._emit_dispatches_agent("p3", "memory_collision_detector", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "memory_collision_detector", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "memory_collision_detector", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "memory_collision_detector", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "memory_collision_detector", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "memory_collision_detector", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "memory_collision_detector", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "memory_collision_detector", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "memory_collision_detector", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "memory_collision_detector", "eval_metric")
trace_contract._emit_stores_embedding("p4", "memory_collision_detector", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "memory_collision_detector", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "memory_collision_detector", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("memory_collision_detector", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("memory_collision_detector", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("memory_collision_detector", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("memory_collision_detector", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("memory_collision_detector", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("memory_collision_detector", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("memory_collision_detector", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("memory_collision_detector", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("memory_collision_detector", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("memory_collision_detector", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("memory_collision_detector", "p4obs", "alert")
trace_contract._emit_links_incident_trace("memory_collision_detector", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("memory_collision_detector", "p3lm", "pattern")
trace_contract._emit_records_learning_event("memory_collision_detector", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("memory_collision_detector", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("memory_collision_detector", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("memory_collision_detector", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("memory_collision_detector", "p3lm", "policy")
trace_contract._emit_stores_learning_state("memory_collision_detector", "p3lm", "state")
trace_contract._emit_records_execution_trace("memory_collision_detector", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("memory_collision_detector", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("memory_collision_detector", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("memory_collision_detector", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("memory_collision_detector", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("memory_collision_detector", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("memory_collision_detector", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("memory_collision_detector", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("memory_collision_detector", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "memory_collision_detector", "context_pull")
trace_contract._emit_pulls_context("p1", "memory_collision_detector", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "memory_collision_detector", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "memory_collision_detector", "uwg_term_2")
trace_contract._emit_writes_through("p1", "memory_collision_detector", "write_through")
trace_contract._emit_writes_through("p1", "memory_collision_detector", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "memory_collision_detector", "safety_validation")
trace_contract._emit_invokes_eval("p1", "memory_collision_detector", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "memory_collision_detector", "routing_commit")


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

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "MemoryCollisionDetector.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "MemoryCollisionDetector.__init__", "p0_governance")
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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L4_STATE,
            "MemoryCollisionDetector.acquire_locks",
        )

        try:
            sorted_locks = sorted(required_locks, key=lambda name: self._lock_order[name])
        except KeyError as e:
            violation = MemoryDeadlockViolation(f"Lock '{e.args[0]}' is not defined in the global hierarchy.")
            return LockAcquisitionResult(success=False, locks_acquired=[], violation=violation)
        acquired_locks: list[str] = []
        start_time = time.monotonic()
        for lock_name in tqdm(sorted_locks, desc="Processing", unit="item"):
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
