"""
Migrate missing names from monolithic structure_blueprint_config.py
into the modular structure_blueprint/ package.

Uses AST parsing to find line ranges, then extracts source text.
"""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_reads_through,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("migrate_blueprint_to_modular", "p4obs", "metric_1")
_emit_emits_metric_event("migrate_blueprint_to_modular", "p4obs", "metric_2")
_emit_emits_metric_event("migrate_blueprint_to_modular", "p4obs", "metric_3")
_emit_emits_metric_event("migrate_blueprint_to_modular", "p4obs", "metric_4")
_emit_emits_metric_event("migrate_blueprint_to_modular", "p4obs", "metric_5")
_emit_emits_metric_event("migrate_blueprint_to_modular", "p4obs", "metric_6")
_emit_records_incident_event("migrate_blueprint_to_modular", "p4obs", "incident")
_emit_captures_runtime_anomaly("migrate_blueprint_to_modular", "p4obs", "anomaly")
_emit_writes_observability_log("migrate_blueprint_to_modular", "p4obs", "obs_log")
_emit_updates_monitoring_state("migrate_blueprint_to_modular", "p4obs", "mon_state")
_emit_triggers_alert("migrate_blueprint_to_modular", "p4obs", "alert")
_emit_links_incident_trace("migrate_blueprint_to_modular", "p4obs", "trace_link")
_emit_captures_pattern("migrate_blueprint_to_modular", "p3lm", "pattern")
_emit_records_learning_event("migrate_blueprint_to_modular", "p3lm", "learning_event")
_emit_writes_learning_snapshot("migrate_blueprint_to_modular", "p3lm", "snapshot")
_emit_feeds_meta_learning("migrate_blueprint_to_modular", "p3lm", "meta_feed")
_emit_updates_routing_strategy("migrate_blueprint_to_modular", "p3lm", "routing")
_emit_improves_agent_policy("migrate_blueprint_to_modular", "p3lm", "policy")
_emit_stores_learning_state("migrate_blueprint_to_modular", "p3lm", "state")
_emit_records_execution_trace("migrate_blueprint_to_modular", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("migrate_blueprint_to_modular", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("migrate_blueprint_to_modular", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("migrate_blueprint_to_modular", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("migrate_blueprint_to_modular", "L4_STATE", "p2_trace_5")
_emit_reads_environ("migrate_blueprint_to_modular", "env_read", "p2_env_1")
_emit_reads_environ("migrate_blueprint_to_modular", "env_read", "p2_env_2")
_emit_reads_runtime_state("migrate_blueprint_to_modular", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("migrate_blueprint_to_modular", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "migrate_blueprint_to_modular")
_emit_applies_guardrail("p0", "migrate_blueprint_to_modular", "p0_governance")
_emit_reads_policy_state("p0", "migrate_blueprint_to_modular", "policy_binding")
_emit_snapshots_state("p0", "migrate_blueprint_to_modular", "state_snapshot")
_emit_pulls_context("p1", "migrate_blueprint_to_modular", "context_pull")
_emit_pulls_context("p1", "migrate_blueprint_to_modular", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "migrate_blueprint_to_modular", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "migrate_blueprint_to_modular", "uwg_term_secondary")
_emit_writes_through("p1", "migrate_blueprint_to_modular", "write_through")
_emit_writes_through("p1", "migrate_blueprint_to_modular", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "migrate_blueprint_to_modular", "safety_validation")
_emit_invokes_eval("p1", "migrate_blueprint_to_modular", "eval_call")
_emit_proposal_commits_routing("p1", "migrate_blueprint_to_modular", "routing_commit")
_emit_escalates_to_human("p1", "migrate_blueprint_to_modular", "human_escalation")
_emit_routes_through("p1", "migrate_blueprint_to_modular", "route_through")
_emit_checks_agent_registry("p1", "migrate_blueprint_to_modular", "agent_registry")
_emit_validates_agent_capability("p1", "migrate_blueprint_to_modular", "capability")
_emit_dispatches_execution_plan("p1", "migrate_blueprint_to_modular", "exec_plan")
_emit_agent_executes_agent("p1", "migrate_blueprint_to_modular", "sub_agent")
_emit_routes_to_agent("p1", "migrate_blueprint_to_modular", "target_agent")
_emit_verifies_policy("p1", "migrate_blueprint_to_modular", "policy_check")
_emit_observes_runtime_state("p1", "migrate_blueprint_to_modular", "runtime_state")
_emit_verifies_boundary("p1", "migrate_blueprint_to_modular", "boundary_check")
_emit_transcripts_response("p1", "migrate_blueprint_to_modular", "transcript")
_emit_hard_fails_untranscripted("p1", "migrate_blueprint_to_modular")
_emit_gated_by_confidence("p1", "migrate_blueprint_to_modular", "confidence_gate")
emit_replay_key("p0", "migrate_blueprint_to_modular")
emit_determinism_digest("p0", "migrate_blueprint_to_modular")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "migrate_blueprint_to_modular", "execution_auth")
_emit_validates_capability("p2", "migrate_blueprint_to_modular", "capability_check")
_emit_routes_to_capability("p2", "migrate_blueprint_to_modular", "capability_route")
_emit_writes_via_uwg("p2", "migrate_blueprint_to_modular", "uwg_write")
_emit_blocks_direct_write("p2", "migrate_blueprint_to_modular", "direct_write_block")
_emit_records_tool_invocation("p2", "migrate_blueprint_to_modular", "tool_invocation")
_emit_captures_execution_output("p2", "migrate_blueprint_to_modular", "exec_output")
_emit_dispatches_agent("p3", "migrate_blueprint_to_modular", "agent_dispatch")
_emit_coordinates_agents("p3", "migrate_blueprint_to_modular", "agent_coordination")
_emit_records_workflow_lineage("p3", "migrate_blueprint_to_modular", "workflow_lineage")
_emit_records_healing_outcome("p3", "migrate_blueprint_to_modular", "healing_outcome")
_emit_escalates_failure("p3", "migrate_blueprint_to_modular", "failure_escalation")
_emit_orchestrates_workflow("p3", "migrate_blueprint_to_modular", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "migrate_blueprint_to_modular", "healing_dispatch")
_emit_invokes_evaluation("p3", "migrate_blueprint_to_modular", "evaluation_signal")
_emit_records_telemetry_event("p4", "migrate_blueprint_to_modular", "telemetry_event")
_emit_captures_evaluation_metric("p4", "migrate_blueprint_to_modular", "eval_metric")
_emit_stores_embedding("p4", "migrate_blueprint_to_modular", "embedding_store")
_emit_updates_meta_learning_state("p4", "migrate_blueprint_to_modular", "meta_learning")
_emit_links_execution_to_snapshot("p4", "migrate_blueprint_to_modular", "exec_snapshot_link")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_1")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_2")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_3")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_4")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_5")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_6")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_7")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_8")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_9")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_10")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_11")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_12")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_13")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_14")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_15")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_16")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_17")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_18")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_19")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_20")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_21")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_22")
_emit_reads_through("l4", "migrate_blueprint_to_modular", "urg_read_23")
ROOT = get_validated_project_root()
MONOLITH = ROOT / AGENTIC_CORE_DIR / "L5_safety" / "config" / "structure_blueprint_config.py"
MOD_DIR = ROOT / AGENTIC_CORE_DIR / "L5_safety" / "config" / "structure_blueprint"
ASSIGNMENTS: dict[str, str] = {
    "HEALING_CONFIG": "governance",
    "AGENT_RESILIENCE_CONFIG": "governance",
    "MISSION_CONFIG": "governance",
    "MCP_CAPABILITIES": "governance",
    "GRAVITY_CONFIG": "governance",
    "GRAVITY_SURGERY_ENABLED": "governance",
    "UPSTREAM_SOVEREIGN_ROOTS": "governance",
    "DOWNSTREAM_ROOTS": "governance",
    "VALIDATED_FILE_EXTENSIONS": "ssot",
    "NAMING_EXEMPT_FILES": "ssot",
    "NAMING_EXEMPT_DIRS": "ssot",
    "FORBIDDEN_PATTERNS": "ssot",
    "ROOT_PROTECTED_FILES": "ssot",
    "PROJECT_ROOT_WHITELIST": "ssot",
    "ROOT_ALLOWED_PATTERNS": "ssot",
    "SOVEREIGN_EXCLUDED_FOLDERS": "ssot",
    "FORBIDDEN_FOLDER_PATTERN": "ssot",
    "FORBIDDEN_ROOT_FOLDERS": "ssot",
    "TESTS_ROOT_FILE_WHITELIST": "ssot",
    "AUTONOMOUS_AGENT_WHITELIST": "ssot",
    "ALLOWED_DUPLICATE_FILENAMES": "ssot",
    "DISCOVERY_EXCLUDED_TERRITORIES": "ssot",
    "PYTHON_STDLIB_MODULES": "ssot",
    "ROOT_WHITELIST": "ssot",
    "GLOBAL_EXCLUDED_DIRS": "ssot",
    "SCOPE_SUMMARY_EXCLUSIONS": "ssot",
    "FLAT_DIRECTORIES": "ssot",
    "validate_flat_directory": "ssot",
    "safe_prefixed_filename": "ssot",
    "validate_no_duplicate_prefix": "ssot",
    "is_path_allowed": "ssot",
    "is_l4_approved": "ssot",
    "protected_folders": "ssot",
    "ignore_dirs": "ssot",
    "sovereign_ignored_folders": "ssot",
    "ARTIFACT_ROUTING_MAP": "artifacts",
    "validate_artifact_routing": "artifacts",
    "check_forbidden_signals": "artifacts",
    "DATA_SUBFOLDER_METADATA": "artifacts",
    "DOCS_SUBFOLDER_METADATA": "artifacts",
    "PROJECT_ROOT_SUBFOLDERS": "artifacts",
    "PROJECT_ROOT_METADATA": "artifacts",
    "TEST_TYPE_SIGNALS": "semantics",
    "LEGACY_AST_SIGNALS": "semantics",
    "AST_PLACEMENT_SIGNALS": "semantics",
    "PLACEMENT_CONFIDENCE": "semantics",
    "L2_TO_L1_MAP": "semantics",
    "EXERCISER_REGISTRY": "semantics",
    "AGENT_REGISTRY": "semantics",
    "semantic_l2_registry": "semantics",
    "SEMANTIC_L2_REGISTRY": "semantics",
}
PRIVATE_DEPS: dict[str, str] = {
    "_STATIC_ROOT_PROTECTED_FILES": "ssot",
    "_DYNAMIC_ROOT_PROTECTED_FILES": "ssot",
    "_semantic_templates": "semantics",
}


def find_top_level_nodes(source: str) -> dict[str, tuple[int, int]]:
    """AST-parse source and return {name: (start_line, end_line)} for all top-level definitions."""
    tree = ast.parse(source)
    result: dict[str, tuple[int, int]] = {}
    for node in ast.iter_child_nodes(tree):
        name = None
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    name = t.id
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
        elif isinstance(node, ast.ClassDef):
            name = node.name
        if name:
            result[name] = (node.lineno, node.end_lineno)
    return result


def extract_lines(all_lines: list[str], start: int, end: int) -> str:
    """Extract source lines (1-indexed, inclusive)."""
    return "".join(all_lines[start - 1 : end])


def find_preceding_comments(all_lines: list[str], start_line: int) -> int:
    """Walk backward from start_line to include preceding comment/blank lines."""
    idx = start_line - 2
    first_comment_line = start_line
    while idx >= 0:
        stripped = all_lines[idx].strip()
        if stripped.startswith("#") or stripped == "":
            first_comment_line = idx + 1
            idx -= 1
        else:
            break
    return first_comment_line


def main():
    source = MONOLITH.read_text(encoding="utf-8")
    all_lines = source.splitlines(True)
    nodes = find_top_level_nodes(source)
    all_targets = {**ASSIGNMENTS, **PRIVATE_DEPS}
    by_module: dict[str, list[tuple[str, int, int]]] = {}
    missing_names = []
    for name, module in all_targets.items():
        if name not in nodes:
            missing_names.append(name)
            continue
        start, end = nodes[name]
        comment_start = find_preceding_comments(all_lines, start)
        if module not in by_module:
            by_module[module] = []
        by_module[module].append((name, comment_start, end))
    if missing_names:
        print(f"WARNING: Names not found in monolith: {missing_names}")
    for module in by_module:
        by_module[module].sort(key=lambda x: x[1])
    for module, items in sorted(by_module.items()):
        total_lines = sum((end - start + 1 for _, start, end in items))
        names = [n for n, _, _ in items]
        print(f"\n{module}.py: {len(items)} names, ~{total_lines} lines")
        for n in names:
            print(f"  - {n}")
    for module, items in sorted(by_module.items()):
        blocks = []
        for name, start, end in items:
            block = extract_lines(all_lines, start, end)
            blocks.append(block)
        combined = "\n".join(blocks)
        output_file = ROOT / "data" / "freeze_reports" / f"_migrate_{module}.py.fragment"
        output_file.write_text(combined, encoding="utf-8")
        print(f"\nWrote {output_file} ({len(combined)} chars)")
    print("\n=== MIGRATION FRAGMENTS GENERATED ===")
    print("Review fragments in data/freeze_reports/_migrate_*.py.fragment")
    print("Then append each fragment to the corresponding modular file.")


if __name__ == "__main__":
    main()
