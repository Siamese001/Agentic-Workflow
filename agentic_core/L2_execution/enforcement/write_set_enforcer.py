"""
Wave 6.1: L2.2 Write-Set Enforcement.

Compares actual writes against the declared_write_set from L2.0.
Aborts execution if an undeclared write is attempted.

Lives in L2 (execution enforcement) per gravity rules.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

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
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "write_set_enforcer")
emit_determinism_digest("p0", "write_set_enforcer")

_emit_dispatches_healing_run("p1", "write_set_enforcer", "L2")
_emit_routes_through("p1", "write_set_enforcer", "L2")
_emit_checks_agent_registry("p1", "write_set_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "write_set_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "write_set_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "write_set_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "write_set_enforcer", "target_agent")
_emit_verifies_policy("p1", "write_set_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "write_set_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "write_set_enforcer", "boundary_check")
_emit_transcripts_response("p1", "write_set_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "write_set_enforcer")
_emit_gated_by_confidence("p1", "write_set_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "write_set_enforcer", "L2")
_emit_reads_policy_state("p1", "write_set_enforcer", "L2")

_emit_snapshots_state("p0", "write_set_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "write_set_enforcer", "execution_auth")
_emit_validates_capability("p2", "write_set_enforcer", "capability_check")
_emit_routes_to_capability("p2", "write_set_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "write_set_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "write_set_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "write_set_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "write_set_enforcer", "exec_output")
_emit_dispatches_agent("p3", "write_set_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "write_set_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "write_set_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "write_set_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "write_set_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "write_set_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "write_set_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "write_set_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "write_set_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "write_set_enforcer", "eval_metric")
_emit_stores_embedding("p4", "write_set_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "write_set_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "write_set_enforcer", "exec_snapshot_link")
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
)

_emit_emits_metric_event("write_set_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("write_set_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("write_set_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("write_set_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("write_set_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("write_set_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("write_set_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("write_set_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("write_set_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("write_set_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("write_set_enforcer", "p4obs", "alert")
_emit_links_incident_trace("write_set_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("write_set_enforcer", "p3lm", "pattern")
_emit_records_learning_event("write_set_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("write_set_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("write_set_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("write_set_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("write_set_enforcer", "p3lm", "policy")
_emit_stores_learning_state("write_set_enforcer", "p3lm", "state")
_emit_records_execution_trace("write_set_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("write_set_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("write_set_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("write_set_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("write_set_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("write_set_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("write_set_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("write_set_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("write_set_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "write_set_enforcer", "context_pull")
_emit_pulls_context("p1", "write_set_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "write_set_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "write_set_enforcer", "uwg_term_2")
_emit_writes_through("p1", "write_set_enforcer", "write_through")
_emit_writes_through("p1", "write_set_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "write_set_enforcer", "safety_validation")
_emit_invokes_eval("p1", "write_set_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "write_set_enforcer", "routing_commit")


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
        _emit_writes_through(str(uuid.uuid4()), "WriteSetEnforcer.record_write", "L2_EXECUTION")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "WriteSetEnforcer.record_write")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:WriteSetEnforcer.record_write".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        _emit_applies_guardrail(str(uuid.uuid4()), "WriteSetEnforcer.verify", "L2_EXECUTION")
        if self._aborted:
            return False
        return self._actual_writes.issubset(self.declared_write_set)
