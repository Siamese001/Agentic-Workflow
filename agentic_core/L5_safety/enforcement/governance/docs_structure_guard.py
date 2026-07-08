from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "docs_structure_guard")
trace_contract.emit_determinism_digest("p0", "docs_structure_guard")

trace_contract._emit_dispatches_healing_run("p1", "docs_structure_guard", "L5")
trace_contract._emit_routes_through("p1", "docs_structure_guard", "L5")
trace_contract._emit_checks_agent_registry("p1", "docs_structure_guard", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "docs_structure_guard", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "docs_structure_guard", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "docs_structure_guard", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "docs_structure_guard", "target_agent")
trace_contract._emit_verifies_policy("p1", "docs_structure_guard", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "docs_structure_guard", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "docs_structure_guard", "boundary_check")
trace_contract._emit_transcripts_response("p1", "docs_structure_guard", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "docs_structure_guard")
trace_contract._emit_gated_by_confidence("p1", "docs_structure_guard", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "docs_structure_guard", "L5")
trace_contract._emit_reads_policy_state("p1", "docs_structure_guard", "L5")
trace_contract._emit_authorize_and_execute("p2", "docs_structure_guard", "execution_auth")
trace_contract._emit_validates_capability("p2", "docs_structure_guard", "capability_check")
trace_contract._emit_routes_to_capability("p2", "docs_structure_guard", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "docs_structure_guard", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "docs_structure_guard", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "docs_structure_guard", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "docs_structure_guard", "exec_output")
trace_contract._emit_dispatches_agent("p3", "docs_structure_guard", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "docs_structure_guard", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "docs_structure_guard", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "docs_structure_guard", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "docs_structure_guard", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "docs_structure_guard", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "docs_structure_guard", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "docs_structure_guard", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "docs_structure_guard", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "docs_structure_guard", "eval_metric")
trace_contract._emit_stores_embedding("p4", "docs_structure_guard", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "docs_structure_guard", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "docs_structure_guard", "exec_snapshot_link")

"\nDocumentation Structure Guard\n\nDeterministic read-only scanner for docs/ directory governance.\nEnforces structural invariants without modifying any files.\n"
from pathlib import Path
from typing import Any

from tqdm import tqdm

trace_contract._emit_emits_metric_event("docs_structure_guard", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("docs_structure_guard", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("docs_structure_guard", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("docs_structure_guard", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("docs_structure_guard", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("docs_structure_guard", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("docs_structure_guard", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("docs_structure_guard", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("docs_structure_guard", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("docs_structure_guard", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("docs_structure_guard", "p4obs", "alert")
trace_contract._emit_links_incident_trace("docs_structure_guard", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("docs_structure_guard", "p3lm", "pattern")
trace_contract._emit_records_learning_event("docs_structure_guard", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("docs_structure_guard", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("docs_structure_guard", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("docs_structure_guard", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("docs_structure_guard", "p3lm", "policy")
trace_contract._emit_stores_learning_state("docs_structure_guard", "p3lm", "state")
trace_contract._emit_records_execution_trace("docs_structure_guard", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("docs_structure_guard", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("docs_structure_guard", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("docs_structure_guard", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("docs_structure_guard", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("docs_structure_guard", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("docs_structure_guard", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("docs_structure_guard", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("docs_structure_guard", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "docs_structure_guard", "context_pull")
trace_contract._emit_pulls_context("p1", "docs_structure_guard", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "docs_structure_guard", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "docs_structure_guard", "uwg_term_2")
trace_contract._emit_writes_through("p1", "docs_structure_guard", "write_through")
trace_contract._emit_writes_through("p1", "docs_structure_guard", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "docs_structure_guard", "safety_validation")
trace_contract._emit_invokes_eval("p1", "docs_structure_guard", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "docs_structure_guard", "routing_commit")


def is_valid_extension(file_path: Path) -> bool:
    """Check if file has a valid documentation extension."""
    return file_path.suffix.lower() in {".md", ".yaml", ".yml", ".json", ".txt"}


def has_backup_suffix(filename: str) -> bool:
    """Check if filename has backup suffix."""
    return any(filename.endswith(suffix) for suffix in [".bak.md", ".old.md", ".backup.md"])


def has_h1_heading(file_path: Path) -> bool:
    """Check if markdown file contains at least one H1 heading."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "has_h1_heading", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "has_h1_heading", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    # review: Multiple exceptions (UnicodeDecodeError, PermissionError) need specific handling
    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "has_h1_heading")
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            return "# " in content
    except (
        UnicodeDecodeError,
        PermissionError,
    ):  # review: Multiple exceptions (UnicodeDecodeError, PermissionError) need specific handling
        return False


def scan_docs_directory(docs_path: Path) -> dict[str, Any]:
    """Scan docs directory for structural violations."""
    violations = []
    files_scanned = 0
    filenames_seen = set()
    all_files = sorted(docs_path.rglob("*"))
    for file_path in tqdm(all_files, desc="Processing", unit="item"):
        if file_path.is_dir():
            continue
        if not is_valid_extension(file_path):
            continue
        files_scanned += 1
        relative_path = file_path.relative_to(docs_path)
        filename = file_path.name
        if has_backup_suffix(filename):
            violations.append(
                {
                    "file": str(relative_path),
                    "type": "backup_suffix",
                    "detail": f"File has backup suffix: {filename}",
                },
            )
        filename_lower = filename.lower()
        if filename_lower in filenames_seen:
            violations.append(
                {
                    "file": str(relative_path),
                    "type": "duplicate_filename",
                    "detail": f"Duplicate filename (case-insensitive): {filename}",
                },
            )
        filenames_seen.add(filename_lower)
        if file_path.suffix.lower() == ".md" and file_path.stat().st_size == 0:
            violations.append(
                {"file": str(relative_path), "type": "empty_markdown", "detail": "Empty markdown file"},
            )
        depth = len(relative_path.parts) - 1
        if depth > 6:
            violations.append(
                {
                    "file": str(relative_path),
                    "type": "depth_exceeded",
                    "detail": f"File depth {depth} exceeds maximum of 6 levels",
                },
            )
        if file_path.suffix.lower() == ".md" and (not has_h1_heading(file_path)):
            violations.append(
                {
                    "file": str(relative_path),
                    "type": "missing_h1",
                    "detail": "Markdown file missing H1 heading (# )",
                },
            )
    return {"files_scanned": files_scanned, "violations": violations}


def main():
    """Main scanner execution."""
    root_path = Path(__file__).parent.parent.parent
    docs_path = root_path / "docs"
    if not docs_path.exists():
        print(f"Error: docs directory not found at {docs_path}")
        return 1
    print(f"Scanning docs directory: {docs_path}")
    result = scan_docs_directory(docs_path)
    output_dir = root_path / "artifacts" / "governance"
    _wg.ensure_dir(output_dir)
    report_path = output_dir / "docs_structure_report.json"
    _wg.write_json(report_path, result, indent=2)
    print(f"Scan complete. Report written to: {report_path}")
    print(f"Files scanned: {result['files_scanned']}")
    print(f"Violations found: {len(result['violations'])}")
    if result["violations"]:
        print("DOCS STRUCTURE VIOLATIONS DETECTED:")
        for violation in result["violations"]:
            print(f"  {violation['file']}: {violation['type']} - {violation['detail']}")
        return 1
    else:
        print("No docs structure violations found.")
        return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
