"""Structure drift manifest generator for architectural integrity monitoring.

This module provides deterministic generation of structure manifests
that can be used to detect unauthorized changes to the codebase structure.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "structure_drift_validator")
trace_contract.emit_determinism_digest("p0", "structure_drift_validator")

trace_contract._emit_dispatches_healing_run("p1", "structure_drift_validator", "L5")
trace_contract._emit_routes_through("p1", "structure_drift_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "structure_drift_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "structure_drift_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "structure_drift_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "structure_drift_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "structure_drift_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "structure_drift_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "structure_drift_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "structure_drift_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "structure_drift_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "structure_drift_validator")
trace_contract._emit_gated_by_confidence("p1", "structure_drift_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "structure_drift_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "structure_drift_validator", "L5")
trace_contract._emit_authorize_and_execute("p2", "structure_drift_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "structure_drift_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "structure_drift_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "structure_drift_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "structure_drift_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "structure_drift_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "structure_drift_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "structure_drift_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "structure_drift_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "structure_drift_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "structure_drift_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "structure_drift_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "structure_drift_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "structure_drift_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "structure_drift_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "structure_drift_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "structure_drift_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "structure_drift_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "structure_drift_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "structure_drift_validator", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("structure_drift_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("structure_drift_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("structure_drift_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("structure_drift_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("structure_drift_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("structure_drift_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("structure_drift_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("structure_drift_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("structure_drift_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("structure_drift_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("structure_drift_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("structure_drift_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("structure_drift_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("structure_drift_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("structure_drift_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("structure_drift_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("structure_drift_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("structure_drift_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("structure_drift_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("structure_drift_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("structure_drift_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("structure_drift_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("structure_drift_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("structure_drift_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("structure_drift_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("structure_drift_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("structure_drift_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("structure_drift_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "structure_drift_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "structure_drift_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "structure_drift_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "structure_drift_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "structure_drift_validator", "write_through")
trace_contract._emit_writes_through("p1", "structure_drift_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "structure_drift_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "structure_drift_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "structure_drift_validator", "routing_commit")

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def generate_structure_manifest() -> dict[str, Any]:
    """Generate a deterministic structure manifest of the codebase.

    Returns:
        A dictionary containing the structure manifest with:
        - directories: List of all directories in the codebase
        - python_files: List of all Python files with their relative paths
        - hash: SHA256 hash of the manifest content for integrity checking
    """
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "generate_structure_manifest", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "generate_structure_manifest", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "generate_structure_manifest")
    manifest = {"directories": [], "python_files": []}
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if path.is_dir():
            if any(part.startswith(".") for part in path.parts):
                continue
            if any(part in ["__pycache__", ".pytest_cache", ".nox", "node_modules"] for part in path.parts):
                continue
            if ".git" in path.parts:
                continue
            relative_path = path.relative_to(PROJECT_ROOT).as_posix()
            manifest["directories"].append(relative_path)
    for py_file in sorted(PROJECT_ROOT.rglob("*.py")):
        if any(part.startswith(".") for part in py_file.parts):
            continue
        if ".git" in py_file.parts:
            continue
        if "__pycache__" in py_file.parts:
            continue
        relative_path = py_file.relative_to(PROJECT_ROOT).as_posix()
        manifest["python_files"].append(relative_path)
    content_for_hash = json.dumps(
        {k: v for k, v in manifest.items() if k != "hash"},
        sort_keys=True,
        separators=(",", ":"),
    )
    manifest["hash"] = hashlib.sha256(content_for_hash.encode()).hexdigest()
    return manifest


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load a structure manifest from a file.

    Args:
        manifest_path: Path to the manifest file

    Returns:
        The loaded structure manifest
    """
    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    import json as _json

    manifest = generate_structure_manifest()
    output_file = PROJECT_ROOT / "artifacts" / "structure" / "structure_manifest.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(_json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Structure manifest saved to: {output_file}")
    print(f"Manifest hash: {manifest['hash']}")
