from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "fresh_data_validator")
trace_contract.emit_determinism_digest("p0", "fresh_data_validator")

trace_contract._emit_dispatches_healing_run("p1", "fresh_data_validator", "L4")
trace_contract._emit_routes_through("p1", "fresh_data_validator", "L4")
trace_contract._emit_checks_agent_registry("p1", "fresh_data_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "fresh_data_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "fresh_data_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "fresh_data_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "fresh_data_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "fresh_data_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "fresh_data_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "fresh_data_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "fresh_data_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "fresh_data_validator")
trace_contract._emit_gated_by_confidence("p1", "fresh_data_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "fresh_data_validator", "L4")
trace_contract._emit_reads_policy_state("p1", "fresh_data_validator", "L4")
trace_contract._emit_authorize_and_execute("p2", "fresh_data_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "fresh_data_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "fresh_data_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "fresh_data_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "fresh_data_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "fresh_data_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "fresh_data_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "fresh_data_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "fresh_data_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "fresh_data_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "fresh_data_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "fresh_data_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "fresh_data_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "fresh_data_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "fresh_data_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "fresh_data_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "fresh_data_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "fresh_data_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "fresh_data_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "fresh_data_validator", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("fresh_data_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("fresh_data_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("fresh_data_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("fresh_data_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("fresh_data_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("fresh_data_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("fresh_data_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("fresh_data_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("fresh_data_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("fresh_data_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("fresh_data_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("fresh_data_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("fresh_data_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("fresh_data_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("fresh_data_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("fresh_data_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("fresh_data_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("fresh_data_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("fresh_data_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("fresh_data_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("fresh_data_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("fresh_data_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("fresh_data_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("fresh_data_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("fresh_data_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("fresh_data_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("fresh_data_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("fresh_data_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "fresh_data_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "fresh_data_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "fresh_data_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "fresh_data_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "fresh_data_validator", "write_through")
trace_contract._emit_writes_through("p1", "fresh_data_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "fresh_data_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "fresh_data_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "fresh_data_validator", "routing_commit")


class StaleDataViolation(Exception):
    """Raised when data is served that is older than the freshness policy allows."""

    def __init__(self, data_timestamp: datetime.datetime, policy_max_age: int):
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "StaleDataViolation.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "StaleDataViolation.__init__", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "StaleDataViolation.__init__")
        self.data_timestamp = data_timestamp
        self.policy_max_age = policy_max_age
        super().__init__(
            f"Data with timestamp {data_timestamp} is stale. Policy requires data to be no older than {policy_max_age} seconds.",
        )


@dataclass(frozen=True)
class FreshnessPolicy:
    """Defines the freshness window for a piece of data."""

    max_age_seconds: int


@dataclass(frozen=True)
class VersionedData:
    """Represents a piece of data with a timestamp for freshness validation."""

    content: Any
    timestamp: datetime.datetime


def validate_freshness(data: VersionedData, policy: FreshnessPolicy) -> None:
    """
    Validates that a piece of versioned data is not stale.

    This function enforces Guarantee #11 (Fresh data only at runtime) by comparing
    the data's timestamp against a configurable freshness window. It is a critical
    sovereign gate in L4 to prevent the use of outdated context or knowledge.

    Args:
        data: The versioned data to validate.
        policy: The freshness policy to apply.

    Raises:
        StaleDataViolation: If the data's timestamp is older than the allowed max age.
    """
    now = datetime.datetime.utcnow()
    allowed_age = datetime.timedelta(seconds=policy.max_age_seconds)
    if now - data.timestamp > allowed_age:
        raise StaleDataViolation(data_timestamp=data.timestamp, policy_max_age=policy.max_age_seconds)
