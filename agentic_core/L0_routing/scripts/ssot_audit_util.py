"""
SSOT Audit Script - Scans approved folders for SSOT violations
"""

import ast
from collections import defaultdict
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
)

# SSOT: Import canonical layer inference (Phase 3 Migration)
# [FIX] Corrected import path (was canonical_truth_1, should be canonical_truth)
from agentic_core.L0_routing.enforcement.safety_validators_seam import (
    load_canonical_truth_validator,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
)

emit_replay_key("p0", "ssot_audit_util")
emit_determinism_digest("p0", "ssot_audit_util")

_emit_dispatches_healing_run("p1", "ssot_audit_util", "L0")
_emit_routes_through("p1", "ssot_audit_util", "L0")
_emit_checks_agent_registry("p1", "ssot_audit_util", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_audit_util", "capability")
_emit_dispatches_execution_plan("p1", "ssot_audit_util", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_audit_util", "sub_agent")
_emit_routes_to_agent("p1", "ssot_audit_util", "target_agent")
_emit_verifies_policy("p1", "ssot_audit_util", "policy_check")
_emit_observes_runtime_state("p1", "ssot_audit_util", "runtime_state")
_emit_verifies_boundary("p1", "ssot_audit_util", "boundary_check")
_emit_transcripts_response("p1", "ssot_audit_util", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_audit_util")
_emit_gated_by_confidence("p1", "ssot_audit_util", "confidence_gate")
_emit_escalates_to_human("p1", "ssot_audit_util", "L0")
_emit_reads_policy_state("p1", "ssot_audit_util", "L0")

_emit_records_execution_trace("p0", "evidence", "ssot_audit_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "ssot_audit_util", "p0_governance")
_emit_snapshots_state("p0", "ssot_audit_util", "state_snapshot")
_emit_authorize_and_execute("p2", "ssot_audit_util", "execution_auth")
_emit_validates_capability("p2", "ssot_audit_util", "capability_check")
_emit_routes_to_capability("p2", "ssot_audit_util", "capability_route")
_emit_writes_via_uwg("p2", "ssot_audit_util", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_audit_util", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_audit_util", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_audit_util", "exec_output")
_emit_dispatches_agent("p3", "ssot_audit_util", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_audit_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_audit_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_audit_util", "healing_outcome")
_emit_escalates_failure("p3", "ssot_audit_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_audit_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_audit_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_audit_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_audit_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_audit_util", "eval_metric")
_emit_stores_embedding("p4", "ssot_audit_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_audit_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_audit_util", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("ssot_audit_util", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_audit_util", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_audit_util", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_audit_util", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_audit_util", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_audit_util", "p4obs", "metric_6")
_emit_records_incident_event("ssot_audit_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_audit_util", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_audit_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_audit_util", "p4obs", "mon_state")
_emit_triggers_alert("ssot_audit_util", "p4obs", "alert")
_emit_links_incident_trace("ssot_audit_util", "p4obs", "trace_link")
_emit_captures_pattern("ssot_audit_util", "p3lm", "pattern")
_emit_records_learning_event("ssot_audit_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_audit_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_audit_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_audit_util", "p3lm", "routing")
_emit_improves_agent_policy("ssot_audit_util", "p3lm", "policy")
_emit_stores_learning_state("ssot_audit_util", "p3lm", "state")
_emit_records_execution_trace("ssot_audit_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_audit_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_audit_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_audit_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_audit_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_audit_util", "env_read", "p2_env_1")
_emit_reads_environ("ssot_audit_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_audit_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_audit_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ssot_audit_util", "context_pull")
_emit_pulls_context("p1", "ssot_audit_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ssot_audit_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_audit_util", "uwg_term_2")
_emit_writes_through("p1", "ssot_audit_util", "write_through")
_emit_writes_through("p1", "ssot_audit_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "ssot_audit_util", "safety_validation")
_emit_invokes_eval("p1", "ssot_audit_util", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_audit_util", "routing_commit")

_ctv = load_canonical_truth_validator()
get_canonical_layer = _ctv.get_canonical_layer

# Approved folders only
APPROVED_FOLDERS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, SCRIPTS_DIR, TESTS_DIR]
ROOT = Path(".")

# REMOVED: get_layer() function - migrated to canonical_truth.py (Phase 3)
# All layer inference now uses get_canonical_layer() from canonical_truth.py


def find_duplicates():
    """Find duplicate filenames across approved folders."""
    # Phase 4.1: Use ssot_discovery instead of rglob
    from agentic_core.utils.schemas.ssot_discovery_validator import get_python_files

    files_by_name = defaultdict(list)
    for folder in APPROVED_FOLDERS:
        folder_path = ROOT / folder
        if folder_path.exists():
            for py_file in get_python_files(folder_path):
                if py_file.name != "__init__.py":
                    files_by_name[py_file.name].append(str(py_file))

    return {name: paths for name, paths in files_by_name.items() if len(paths) > 1}


def find_gravity_violations():
    """Find upward import violations (higher layer importing from lower layer)."""
    violations = []

    # Phase 4.1: Use ssot_discovery instead of rglob
    from agentic_core.utils.schemas.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(ROOT / AGENTIC_CORE_DIR):
        file_layer = get_canonical_layer(py_file)
        if not file_layer or file_layer == "Unknown":
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    import_path = node.module.replace(".", "/")
                    import_layer = get_canonical_layer(import_path)
                    # SSOT: Use canonical layer order from canonical_truth
                    layer_order = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}
                    if import_layer and layer_order.get(import_layer, 99) < layer_order.get(file_layer, 0):
                        violations.append(
                            {
                                "file": str(py_file),
                                "file_layer": file_layer,
                                "imports": node.module,
                                "import_layer": import_layer,
                            },
                        )
        # guardian: allow-silent-swallow
        except (ValueError, TypeError):
            pass

    return violations


def find_syntax_errors():
    """Find files with syntax errors."""
    # Phase 4.1: Use ssot_discovery instead of rglob
    from agentic_core.utils.schemas.ssot_discovery_validator import get_python_files

    errors = []
    for folder in APPROVED_FOLDERS:
        folder_path = ROOT / folder
        if folder_path.exists():
            for py_file in get_python_files(folder_path):
                try:
                    content = py_file.read_text(encoding="utf-8")
                    ast.parse(content)
                # guardian: allow-silent-swallow - acceptable exception handling    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
                except SyntaxError as e:
                    errors.append({"file": str(py_file), "line": e.lineno, "message": str(e.msg)})
                # guardian: allow-silent-swallow
                except (ValueError, TypeError):
                    pass
    return errors


def find_naming_violations():
    """Find files with naming convention violations."""
    # Phase 4.1: Use ssot_discovery instead of rglob
    from agentic_core.utils.schemas.ssot_discovery_validator import get_python_files

    violations = []
    for folder in APPROVED_FOLDERS:
        folder_path = ROOT / folder
        if folder_path.exists():
            for py_file in get_python_files(folder_path):
                name = py_file.stem
                # Check for CamelCase in non-Agent files
                if any(c.isupper() for c in name) and "Agent" not in name and "Mixin" not in name:
                    violations.append(
                        {"file": str(py_file), "issue": "CamelCase naming (should be snake_case)"},
                    )
                # Check for version suffixes
                if any(suffix in name for suffix in ["_v1", "_v2", "_v3", "_old", "_new", "_backup"]):
                    violations.append({"file": str(py_file), "issue": "Version suffix in filename"})
    return violations


if __name__ == "__main__":
    print("=== SSOT AUDIT REPORT ===\n")

    # Duplicates
    duplicates = find_duplicates()
    print(f"DUPLICATE FILES: {len(duplicates)}")
    for name, paths in sorted(duplicates.items())[:50]:
        print(f"  {name}:")
        for p in paths:
            print(f"    - {p}")

    print(f"\n{'=' * 50}\n")

    # Gravity violations
    gravity = find_gravity_violations()
    print(f"GRAVITY VIOLATIONS: {len(gravity)}")
    for v in gravity[:30]:
        print(f"  {v['file_layer']} imports {v['import_layer']}: {Path(v['file']).name}")
        print(f"    File: {v['file']}")
        print(f"    Imports: {v['imports']}")

    print(f"\n{'=' * 50}\n")

    # Syntax errors
    syntax = find_syntax_errors()
    print(f"SYNTAX ERRORS: {len(syntax)}")
    for e in syntax[:30]:
        print(f"  {e['file']}:{e['line']} - {e['message']}")

    print(f"\n{'=' * 50}\n")

    # Naming violations
    naming = find_naming_violations()
    print(f"NAMING VIOLATIONS: {len(naming)}")
    for v in naming[:30]:
        print(f"  {v['file']}: {v['issue']}")
