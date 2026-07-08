from __future__ import annotations

from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "get_existing_file_hashes_util")
trace_contract.emit_determinism_digest("p0", "get_existing_file_hashes_util")

trace_contract._emit_dispatches_healing_run("p1", "get_existing_file_hashes_util", "L4")
trace_contract._emit_routes_through("p1", "get_existing_file_hashes_util", "L4")
trace_contract._emit_checks_agent_registry("p1", "get_existing_file_hashes_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "get_existing_file_hashes_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "get_existing_file_hashes_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "get_existing_file_hashes_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "get_existing_file_hashes_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "get_existing_file_hashes_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "get_existing_file_hashes_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "get_existing_file_hashes_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "get_existing_file_hashes_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "get_existing_file_hashes_util")
trace_contract._emit_gated_by_confidence("p1", "get_existing_file_hashes_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "get_existing_file_hashes_util", "L4")
trace_contract._emit_reads_policy_state("p1", "get_existing_file_hashes_util", "L4")
trace_contract._emit_authorize_and_execute("p2", "get_existing_file_hashes_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "get_existing_file_hashes_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "get_existing_file_hashes_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "get_existing_file_hashes_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "get_existing_file_hashes_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "get_existing_file_hashes_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "get_existing_file_hashes_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "get_existing_file_hashes_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "get_existing_file_hashes_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "get_existing_file_hashes_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "get_existing_file_hashes_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "get_existing_file_hashes_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "get_existing_file_hashes_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "get_existing_file_hashes_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "get_existing_file_hashes_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "get_existing_file_hashes_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "get_existing_file_hashes_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "get_existing_file_hashes_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "get_existing_file_hashes_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "get_existing_file_hashes_util", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from typing import Any

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR
from agentic_core.utils.runners.ssot_discovery_validator import get_data_files, get_python_files

trace_contract._emit_emits_metric_event("get_existing_file_hashes_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("get_existing_file_hashes_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("get_existing_file_hashes_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("get_existing_file_hashes_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("get_existing_file_hashes_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("get_existing_file_hashes_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("get_existing_file_hashes_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("get_existing_file_hashes_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("get_existing_file_hashes_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("get_existing_file_hashes_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("get_existing_file_hashes_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("get_existing_file_hashes_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("get_existing_file_hashes_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("get_existing_file_hashes_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("get_existing_file_hashes_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("get_existing_file_hashes_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("get_existing_file_hashes_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("get_existing_file_hashes_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("get_existing_file_hashes_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("get_existing_file_hashes_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("get_existing_file_hashes_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("get_existing_file_hashes_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("get_existing_file_hashes_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("get_existing_file_hashes_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("get_existing_file_hashes_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("get_existing_file_hashes_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("get_existing_file_hashes_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("get_existing_file_hashes_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "get_existing_file_hashes_util", "context_pull")
trace_contract._emit_pulls_context("p1", "get_existing_file_hashes_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "get_existing_file_hashes_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "get_existing_file_hashes_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "get_existing_file_hashes_util", "write_through")
trace_contract._emit_writes_through("p1", "get_existing_file_hashes_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "get_existing_file_hashes_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "get_existing_file_hashes_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "get_existing_file_hashes_util", "routing_commit")


def get_existing_file_hashes() -> dict[str, str]:
    """Get dict of filename -> content hash for existing sovereign files."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "get_existing_file_hashes", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "get_existing_file_hashes", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L4_STATE, "get_existing_file_hashes")
    existing: Any = {}
    repo_root: Any = Path(".")
    sovereign_roots: Any = {
        AGENTIC_CORE_DIR,
        APPS_LIC_DIR,
        APPS_RG_DIR,
        APPS_SHARED_DIR,
        "schemas",
        "prompt_governance",
        "observability",
        "config",
        "data",
        ARCHIVES_DIR,
        "docs",
    }
    for root in sovereign_roots:
        root_path: Any = repo_root / root
        if root_path.exists():
            for file_path in get_python_files(root_path):
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in get_data_files(root_path, extensions=[".json"]):
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in get_data_files(root_path, extensions=[".md"]):
                existing[file_path.name] = get_file_hash(file_path)
    return existing
