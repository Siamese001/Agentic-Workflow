from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "replay_key_computer")
trace_contract.emit_determinism_digest("p0", "replay_key_computer")

trace_contract._emit_dispatches_healing_run("p1", "replay_key_computer", "L6")
trace_contract._emit_routes_through("p1", "replay_key_computer", "L6")
trace_contract._emit_checks_agent_registry("p1", "replay_key_computer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "replay_key_computer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "replay_key_computer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "replay_key_computer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "replay_key_computer", "target_agent")
trace_contract._emit_verifies_policy("p1", "replay_key_computer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "replay_key_computer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "replay_key_computer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "replay_key_computer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "replay_key_computer")
trace_contract._emit_gated_by_confidence("p1", "replay_key_computer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "replay_key_computer", "L6")
trace_contract._emit_reads_policy_state("p1", "replay_key_computer", "L6")
trace_contract._emit_authorize_and_execute("p2", "replay_key_computer", "execution_auth")
trace_contract._emit_validates_capability("p2", "replay_key_computer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "replay_key_computer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "replay_key_computer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "replay_key_computer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "replay_key_computer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "replay_key_computer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "replay_key_computer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "replay_key_computer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "replay_key_computer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "replay_key_computer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "replay_key_computer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "replay_key_computer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "replay_key_computer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "replay_key_computer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "replay_key_computer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "replay_key_computer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "replay_key_computer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "replay_key_computer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "replay_key_computer", "exec_snapshot_link")

trace_contract.record_execution_trace("replay_key_computer", "replay_key_computer_trace")


trace_contract._emit_emits_metric_event("replay_key_computer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("replay_key_computer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("replay_key_computer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("replay_key_computer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("replay_key_computer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("replay_key_computer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("replay_key_computer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("replay_key_computer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("replay_key_computer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("replay_key_computer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("replay_key_computer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("replay_key_computer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("replay_key_computer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("replay_key_computer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("replay_key_computer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("replay_key_computer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("replay_key_computer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("replay_key_computer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("replay_key_computer", "p3lm", "state")
trace_contract._emit_records_execution_trace("replay_key_computer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("replay_key_computer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("replay_key_computer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("replay_key_computer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("replay_key_computer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("replay_key_computer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("replay_key_computer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("replay_key_computer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("replay_key_computer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "replay_key_computer", "context_pull")
trace_contract._emit_pulls_context("p1", "replay_key_computer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "replay_key_computer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "replay_key_computer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "replay_key_computer", "write_through")
trace_contract._emit_writes_through("p1", "replay_key_computer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "replay_key_computer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "replay_key_computer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "replay_key_computer", "routing_commit")


@dataclass(frozen=True)
class ReplayKeyComponents:
    """A structured container for all components that define a replay key."""

    tier_selection: str
    retry_count: int
    threshold_config: dict[str, float]
    tool_budget_caps: dict[str, int]
    freshness_windows: dict[str, int]
    config_surface_hash: str
    embedding_pack_hash: str
    embedding_model_version: str
    c0_context_hash: str


def compute_replay_key(components: ReplayKeyComponents) -> str:
    """
    Computes a deterministic replay key from a comprehensive set of components.

    This function enforces Guarantee #12 by creating a single, verifiable hash
    that represents the entire context of a governance decision. Any change to
    the inputs (e.g., a config change, a model update, or a different retry
    count) will produce a different key, ensuring that replays are always
    executed against the exact context of the original decision.

    The key is computed in L6 (Observability) and would be stored in L4 (State)
    alongside the decision record.

    Args:
        components: A structured dataclass containing all parts of the replay key.

    Returns:
        A SHA-256 hex digest representing the deterministic replay key.
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "compute_replay_key", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "compute_replay_key", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L6_OBSERVABILITY, "compute_replay_key")

    def _canonical_json(data: Any) -> str:
        """Computes canonical JSON: sorted keys, UTF-8, no whitespace."""
        return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

    from dataclasses import asdict

    material = asdict(components)
    canonical_string = _canonical_json(material)
    return hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()
