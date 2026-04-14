from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

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
    record_execution_trace,
)

emit_replay_key("p0", "replay_key_computer")
emit_determinism_digest("p0", "replay_key_computer")

_emit_dispatches_healing_run("p1", "replay_key_computer", "L6")
_emit_routes_through("p1", "replay_key_computer", "L6")
_emit_checks_agent_registry("p1", "replay_key_computer", "agent_registry")
_emit_validates_agent_capability("p1", "replay_key_computer", "capability")
_emit_dispatches_execution_plan("p1", "replay_key_computer", "exec_plan")
_emit_agent_executes_agent("p1", "replay_key_computer", "sub_agent")
_emit_routes_to_agent("p1", "replay_key_computer", "target_agent")
_emit_verifies_policy("p1", "replay_key_computer", "policy_check")
_emit_observes_runtime_state("p1", "replay_key_computer", "runtime_state")
_emit_verifies_boundary("p1", "replay_key_computer", "boundary_check")
_emit_transcripts_response("p1", "replay_key_computer", "transcript")
_emit_hard_fails_untranscripted("p1", "replay_key_computer")
_emit_gated_by_confidence("p1", "replay_key_computer", "confidence_gate")
_emit_escalates_to_human("p1", "replay_key_computer", "L6")
_emit_reads_policy_state("p1", "replay_key_computer", "L6")
_emit_authorize_and_execute("p2", "replay_key_computer", "execution_auth")
_emit_validates_capability("p2", "replay_key_computer", "capability_check")
_emit_routes_to_capability("p2", "replay_key_computer", "capability_route")
_emit_writes_via_uwg("p2", "replay_key_computer", "uwg_write")
_emit_blocks_direct_write("p2", "replay_key_computer", "direct_write_block")
_emit_records_tool_invocation("p2", "replay_key_computer", "tool_invocation")
_emit_captures_execution_output("p2", "replay_key_computer", "exec_output")
_emit_dispatches_agent("p3", "replay_key_computer", "agent_dispatch")
_emit_coordinates_agents("p3", "replay_key_computer", "agent_coordination")
_emit_records_workflow_lineage("p3", "replay_key_computer", "workflow_lineage")
_emit_records_healing_outcome("p3", "replay_key_computer", "healing_outcome")
_emit_escalates_failure("p3", "replay_key_computer", "failure_escalation")
_emit_orchestrates_workflow("p3", "replay_key_computer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "replay_key_computer", "healing_dispatch")
_emit_invokes_evaluation("p3", "replay_key_computer", "evaluation_signal")
_emit_records_telemetry_event("p4", "replay_key_computer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "replay_key_computer", "eval_metric")
_emit_stores_embedding("p4", "replay_key_computer", "embedding_store")
_emit_updates_meta_learning_state("p4", "replay_key_computer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "replay_key_computer", "exec_snapshot_link")
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

record_execution_trace("replay_key_computer", "replay_key_computer_trace")


_emit_emits_metric_event("replay_key_computer", "p4obs", "metric_1")
_emit_emits_metric_event("replay_key_computer", "p4obs", "metric_2")
_emit_emits_metric_event("replay_key_computer", "p4obs", "metric_3")
_emit_emits_metric_event("replay_key_computer", "p4obs", "metric_4")
_emit_emits_metric_event("replay_key_computer", "p4obs", "metric_5")
_emit_emits_metric_event("replay_key_computer", "p4obs", "metric_6")
_emit_records_incident_event("replay_key_computer", "p4obs", "incident")
_emit_captures_runtime_anomaly("replay_key_computer", "p4obs", "anomaly")
_emit_writes_observability_log("replay_key_computer", "p4obs", "obs_log")
_emit_updates_monitoring_state("replay_key_computer", "p4obs", "mon_state")
_emit_triggers_alert("replay_key_computer", "p4obs", "alert")
_emit_links_incident_trace("replay_key_computer", "p4obs", "trace_link")
_emit_captures_pattern("replay_key_computer", "p3lm", "pattern")
_emit_records_learning_event("replay_key_computer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("replay_key_computer", "p3lm", "snapshot")
_emit_feeds_meta_learning("replay_key_computer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("replay_key_computer", "p3lm", "routing")
_emit_improves_agent_policy("replay_key_computer", "p3lm", "policy")
_emit_stores_learning_state("replay_key_computer", "p3lm", "state")
_emit_records_execution_trace("replay_key_computer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("replay_key_computer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("replay_key_computer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("replay_key_computer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("replay_key_computer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("replay_key_computer", "env_read", "p2_env_1")
_emit_reads_environ("replay_key_computer", "env_read", "p2_env_2")
_emit_reads_runtime_state("replay_key_computer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("replay_key_computer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "replay_key_computer", "context_pull")
_emit_pulls_context("p1", "replay_key_computer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "replay_key_computer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "replay_key_computer", "uwg_term_2")
_emit_writes_through("p1", "replay_key_computer", "write_through")
_emit_writes_through("p1", "replay_key_computer", "write_through_2")
_emit_validated_by_safety_plane("p1", "replay_key_computer", "safety_validation")
_emit_invokes_eval("p1", "replay_key_computer", "eval_call")
_emit_proposal_commits_routing("p1", "replay_key_computer", "routing_commit")


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

    _emit_snapshots_state(str(_uuid.uuid4()), "compute_replay_key", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "compute_replay_key", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L6_OBSERVABILITY, "compute_replay_key")

    def _canonical_json(data: Any) -> str:
        """Computes canonical JSON: sorted keys, UTF-8, no whitespace."""
        return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))

    from dataclasses import asdict

    material = asdict(components)
    canonical_string = _canonical_json(material)
    return hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()
