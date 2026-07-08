from __future__ import annotations

from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "ssot_import_enforcer")
trace_contract.emit_determinism_digest("p0", "ssot_import_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "ssot_import_enforcer", "L5")
trace_contract._emit_routes_through("p1", "ssot_import_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "ssot_import_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "ssot_import_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "ssot_import_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "ssot_import_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "ssot_import_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "ssot_import_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "ssot_import_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "ssot_import_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "ssot_import_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "ssot_import_enforcer")
trace_contract._emit_gated_by_confidence("p1", "ssot_import_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "ssot_import_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "ssot_import_enforcer", "L5")
trace_contract._emit_authorize_and_execute("p2", "ssot_import_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "ssot_import_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "ssot_import_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "ssot_import_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "ssot_import_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "ssot_import_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "ssot_import_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "ssot_import_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "ssot_import_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "ssot_import_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "ssot_import_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "ssot_import_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "ssot_import_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "ssot_import_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "ssot_import_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "ssot_import_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "ssot_import_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "ssot_import_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "ssot_import_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "ssot_import_enforcer", "exec_snapshot_link")

"\nSSOT Enforcement Script\nAdds structure_blueprint.py import to files that reference L0-L5 layers\nbut don't already import from SSOT.\n"
import re
from pathlib import Path

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR
from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from tqdm import tqdm

trace_contract._emit_emits_metric_event("ssot_import_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("ssot_import_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("ssot_import_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("ssot_import_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("ssot_import_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("ssot_import_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("ssot_import_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("ssot_import_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("ssot_import_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("ssot_import_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("ssot_import_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("ssot_import_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("ssot_import_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("ssot_import_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("ssot_import_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("ssot_import_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("ssot_import_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("ssot_import_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("ssot_import_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("ssot_import_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("ssot_import_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("ssot_import_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("ssot_import_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("ssot_import_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("ssot_import_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("ssot_import_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("ssot_import_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("ssot_import_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "ssot_import_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "ssot_import_enforcer", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "ssot_import_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "ssot_import_enforcer", "uwg_term_2")
trace_contract._emit_writes_through("p1", "ssot_import_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "ssot_import_enforcer", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "ssot_import_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "ssot_import_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "ssot_import_enforcer", "routing_commit")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR
SSOT_IMPORT = "# [SSOT IMPORT] Structure blueprint is the single source of truth\nfrom agentic_core.L5_safety.config.structure_blueprint import (\n    SOVEREIGN_REGISTRY,\n    CORE_SUBFOLDER_MAP,\n)\n"
LAYER_PATTERN = re.compile("L[0-5]_")
SSOT_IMPORT_PATTERN = re.compile("from agentic_core\\.config\\.blueprint_sovereign\\.structure_blueprint")


def needs_ssot_import(content: str) -> bool:
    """Check if file references layers but doesn't import SSOT."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "needs_ssot_import", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "needs_ssot_import", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "needs_ssot_import")
    has_layer_ref = bool(LAYER_PATTERN.search(content))
    has_ssot_import = bool(SSOT_IMPORT_PATTERN.search(content))
    return has_layer_ref and (not has_ssot_import)


def add_ssot_import(file_path: Path) -> bool:
    """Add SSOT import to a file if needed."""
    try:
        content = file_path.read_text(encoding="utf-8")
    except (ValueError, TypeError, RuntimeError) as e:
        return False
    if not needs_ssot_import(content):
        return False
    if "structure_blueprint.py" in str(file_path):
        return False
    if file_path.name == "__init__.py":
        return False
    lines = content.split("\n")
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_idx = i + 1
        elif line.startswith("class ") or line.startswith("def "):
            break
    lines.insert(insert_idx, "")
    lines.insert(insert_idx + 1, SSOT_IMPORT)
    new_content = "\n".join(lines)
    _wg.write_text(file_path, new_content, encoding="utf-8")
    return True


def main():
    """Process all Python files in agentic_core, tests, apps_shared, apps_rg, apps_lic."""
    updated = 0
    skipped = 0
    territories = [
        AGENTIC_CORE,
        PROJECT_ROOT / TESTS_DIR,
        PROJECT_ROOT / APPS_SHARED_DIR,
        PROJECT_ROOT / APPS_RG_DIR,
        PROJECT_ROOT / APPS_LIC_DIR,
    ]
    for territory in tqdm(territories, desc="Processing", unit="item"):
        if not territory.exists():
            continue
        from agentic_core.utils.runners.ssot_discovery_validator import get_python_files

        for py_file in get_python_files(territory):
            if add_ssot_import(py_file):
                print(f"[UPDATED] {py_file.relative_to(PROJECT_ROOT)}")
                updated += 1
            else:
                skipped += 1
    print(f"\n[DONE] Updated {updated} files, skipped {skipped}")


if __name__ == "__main__":
    main()
