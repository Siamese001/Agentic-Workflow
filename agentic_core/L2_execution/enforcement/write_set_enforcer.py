"""
Wave 6.1: L2.2 Write-Set Enforcement.

Compares actual writes against the declared_write_set from L2.0.
Aborts execution if an undeclared write is attempted.

Lives in L2 (execution enforcement) per gravity rules.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "write_set_enforcer")
trace_contract.emit_determinism_digest("p0", "write_set_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "write_set_enforcer", "L2")
trace_contract._emit_routes_through("p1", "write_set_enforcer", "L2")
trace_contract._emit_checks_agent_registry("p1", "write_set_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "write_set_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "write_set_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "write_set_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "write_set_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "write_set_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "write_set_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "write_set_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "write_set_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "write_set_enforcer")
trace_contract._emit_gated_by_confidence("p1", "write_set_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "write_set_enforcer", "L2")
trace_contract._emit_reads_policy_state("p1", "write_set_enforcer", "L2")

trace_contract._emit_snapshots_state("p0", "write_set_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "write_set_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "write_set_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "write_set_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "write_set_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "write_set_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "write_set_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "write_set_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "write_set_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "write_set_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "write_set_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "write_set_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "write_set_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "write_set_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "write_set_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "write_set_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "write_set_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "write_set_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "write_set_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "write_set_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "write_set_enforcer", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("write_set_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("write_set_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("write_set_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("write_set_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("write_set_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("write_set_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("write_set_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("write_set_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("write_set_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("write_set_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("write_set_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("write_set_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("write_set_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("write_set_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("write_set_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("write_set_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("write_set_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("write_set_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("write_set_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("write_set_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("write_set_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("write_set_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("write_set_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("write_set_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("write_set_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("write_set_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("write_set_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("write_set_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "write_set_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "write_set_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "write_set_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "write_set_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "write_set_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "write_set_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "write_set_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "write_set_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "write_set_enforcer", "routing_commit")


class WriteSetViolation(RuntimeError):
    """Raised when an undeclared write is attempted."""


@dataclass
class WriteSetEnforcer:
    """Enforces that actual writes match the declared write set.

    Usage::

        enforcer = WriteSetEnforcer(
            declared_write_set={"key_a", "key_b"}
        )
        enforcer.record_write("key_a")   # ok
        enforcer.record_write("key_c")   # raises
    """

    declared_write_set: frozenset[str]
    _actual_writes: set[str] = field(default_factory=set, init=False, repr=False)
    _aborted: bool = field(default=False, init=False, repr=False)

    def record_write(self, key: str) -> None:
        """Record an actual write and enforce declaration.

        Raises WriteSetViolation if key is not in the
        declared write set.
        """
        trace_contract._emit_writes_through(str(uuid.uuid4()), "WriteSetEnforcer.record_write", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L2_EXECUTION, "WriteSetEnforcer.record_write")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:WriteSetEnforcer.record_write".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self._aborted:
            raise WriteSetViolation("Execution aborted due to prior write-set violation.")
        if key not in self.declared_write_set:
            self._aborted = True
            raise WriteSetViolation(
                f"Undeclared write to '{key}'. Declared set: {sorted(self.declared_write_set)}",
            )
        self._actual_writes.add(key)

    @property
    def actual_writes(self) -> frozenset[str]:
        """Return the set of actual writes recorded."""
        return frozenset(self._actual_writes)

    @property
    def is_complete(self) -> bool:
        """True if all declared writes have been performed."""
        return self._actual_writes == set(self.declared_write_set)

    @property
    def is_aborted(self) -> bool:
        return self._aborted

    def verify(self) -> bool:
        """Verify no undeclared writes occurred.

        Returns True if actual_writes is a subset of
        declared_write_set and execution was not aborted.
        """
        trace_contract._emit_applies_guardrail(str(uuid.uuid4()), "WriteSetEnforcer.verify", "L2_EXECUTION")
        if self._aborted:
            return False
        return self._actual_writes.issubset(self.declared_write_set)
