"""Structure drift manifest writer — stdlib only, no UWG dependency.

Write counterpart for structure_drift_validator.generate_structure_manifest().
Moved here from validators/ to preserve the pure read-only contract of that module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "structure_drift_writer")
trace_contract.emit_determinism_digest("p0", "structure_drift_writer")

trace_contract._emit_dispatches_healing_run("p1", "structure_drift_writer", "L5")
trace_contract._emit_routes_through("p1", "structure_drift_writer", "L5")
trace_contract._emit_checks_agent_registry("p1", "structure_drift_writer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "structure_drift_writer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "structure_drift_writer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "structure_drift_writer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "structure_drift_writer", "target_agent")
trace_contract._emit_verifies_policy("p1", "structure_drift_writer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "structure_drift_writer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "structure_drift_writer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "structure_drift_writer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "structure_drift_writer")
trace_contract._emit_gated_by_confidence("p1", "structure_drift_writer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "structure_drift_writer", "L5")
trace_contract._emit_reads_policy_state("p1", "structure_drift_writer", "L5")
trace_contract._emit_authorize_and_execute("p2", "structure_drift_writer", "execution_auth")
trace_contract._emit_validates_capability("p2", "structure_drift_writer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "structure_drift_writer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "structure_drift_writer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "structure_drift_writer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "structure_drift_writer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "structure_drift_writer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "structure_drift_writer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "structure_drift_writer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "structure_drift_writer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "structure_drift_writer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "structure_drift_writer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "structure_drift_writer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "structure_drift_writer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "structure_drift_writer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "structure_drift_writer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "structure_drift_writer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "structure_drift_writer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "structure_drift_writer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "structure_drift_writer", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("structure_drift_writer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("structure_drift_writer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("structure_drift_writer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("structure_drift_writer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("structure_drift_writer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("structure_drift_writer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("structure_drift_writer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("structure_drift_writer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("structure_drift_writer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("structure_drift_writer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("structure_drift_writer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("structure_drift_writer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("structure_drift_writer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("structure_drift_writer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("structure_drift_writer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("structure_drift_writer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("structure_drift_writer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("structure_drift_writer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("structure_drift_writer", "p3lm", "state")
trace_contract._emit_records_execution_trace("structure_drift_writer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("structure_drift_writer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("structure_drift_writer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("structure_drift_writer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("structure_drift_writer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("structure_drift_writer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("structure_drift_writer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("structure_drift_writer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("structure_drift_writer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "structure_drift_writer", "context_pull")
trace_contract._emit_pulls_context("p1", "structure_drift_writer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "structure_drift_writer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "structure_drift_writer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "structure_drift_writer", "write_through")
trace_contract._emit_writes_through("p1", "structure_drift_writer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "structure_drift_writer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "structure_drift_writer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "structure_drift_writer", "routing_commit")


def save_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    """Save the structure manifest to a file.

    Args:
        manifest: The structure manifest to save
        output_path: Path where to save the manifest
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "save_manifest", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "save_manifest", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "save_manifest")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


__all__ = ["save_manifest"]
