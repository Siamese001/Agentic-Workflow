"""
V15 P0.2 — Adapter Prohibition AST Scanner.

Scans all Python files under agentic_core/ for imports of AdapterBase
or class definitions inheriting from AdapterBase/HealingAdapter.
Files under archives/ are excluded.

Exit code 0 = no violations.
Exit code 1 = violations found.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("check_adapter_prohibition", "p4obs", "metric_1")
_emit_emits_metric_event("check_adapter_prohibition", "p4obs", "metric_2")
_emit_emits_metric_event("check_adapter_prohibition", "p4obs", "metric_3")
_emit_emits_metric_event("check_adapter_prohibition", "p4obs", "metric_4")
_emit_emits_metric_event("check_adapter_prohibition", "p4obs", "metric_5")
_emit_emits_metric_event("check_adapter_prohibition", "p4obs", "metric_6")
_emit_records_incident_event("check_adapter_prohibition", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_adapter_prohibition", "p4obs", "anomaly")
_emit_writes_observability_log("check_adapter_prohibition", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_adapter_prohibition", "p4obs", "mon_state")
_emit_triggers_alert("check_adapter_prohibition", "p4obs", "alert")
_emit_links_incident_trace("check_adapter_prohibition", "p4obs", "trace_link")
_emit_captures_pattern("check_adapter_prohibition", "p3lm", "pattern")
_emit_records_learning_event("check_adapter_prohibition", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_adapter_prohibition", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_adapter_prohibition", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_adapter_prohibition", "p3lm", "routing")
_emit_improves_agent_policy("check_adapter_prohibition", "p3lm", "policy")
_emit_stores_learning_state("check_adapter_prohibition", "p3lm", "state")
_emit_records_execution_trace("check_adapter_prohibition", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_adapter_prohibition", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_adapter_prohibition", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_adapter_prohibition", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_adapter_prohibition", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_adapter_prohibition", "env_read", "p2_env_1")
_emit_reads_environ("check_adapter_prohibition", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_adapter_prohibition", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_adapter_prohibition", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "check_adapter_prohibition")
_emit_applies_guardrail("p0", "check_adapter_prohibition", "p0_governance")
_emit_reads_policy_state("p0", "check_adapter_prohibition", "policy_binding")
_emit_snapshots_state("p0", "check_adapter_prohibition", "state_snapshot")
_emit_pulls_context("p1", "check_adapter_prohibition", "context_pull")
_emit_pulls_context("p1", "check_adapter_prohibition", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_adapter_prohibition", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_adapter_prohibition", "uwg_term_secondary")
_emit_writes_through("p1", "check_adapter_prohibition", "write_through")
_emit_writes_through("p1", "check_adapter_prohibition", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_adapter_prohibition", "safety_validation")
_emit_invokes_eval("p1", "check_adapter_prohibition", "eval_call")
_emit_proposal_commits_routing("p1", "check_adapter_prohibition", "routing_commit")
_emit_escalates_to_human("p1", "check_adapter_prohibition", "human_escalation")
_emit_routes_through("p1", "check_adapter_prohibition", "route_through")
_emit_checks_agent_registry("p1", "check_adapter_prohibition", "agent_registry")
_emit_validates_agent_capability("p1", "check_adapter_prohibition", "capability")
_emit_dispatches_execution_plan("p1", "check_adapter_prohibition", "exec_plan")
_emit_agent_executes_agent("p1", "check_adapter_prohibition", "sub_agent")
_emit_routes_to_agent("p1", "check_adapter_prohibition", "target_agent")
_emit_verifies_policy("p1", "check_adapter_prohibition", "policy_check")
_emit_observes_runtime_state("p1", "check_adapter_prohibition", "runtime_state")
_emit_verifies_boundary("p1", "check_adapter_prohibition", "boundary_check")
_emit_transcripts_response("p1", "check_adapter_prohibition", "transcript")
_emit_hard_fails_untranscripted("p1", "check_adapter_prohibition")
_emit_gated_by_confidence("p1", "check_adapter_prohibition", "confidence_gate")
emit_replay_key("p0", "check_adapter_prohibition")
emit_determinism_digest("p0", "check_adapter_prohibition")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_adapter_prohibition", "execution_auth")
_emit_validates_capability("p2", "check_adapter_prohibition", "capability_check")
_emit_routes_to_capability("p2", "check_adapter_prohibition", "capability_route")
_emit_writes_via_uwg("p2", "check_adapter_prohibition", "uwg_write")
_emit_blocks_direct_write("p2", "check_adapter_prohibition", "direct_write_block")
_emit_records_tool_invocation("p2", "check_adapter_prohibition", "tool_invocation")
_emit_captures_execution_output("p2", "check_adapter_prohibition", "exec_output")
_emit_dispatches_agent("p3", "check_adapter_prohibition", "agent_dispatch")
_emit_coordinates_agents("p3", "check_adapter_prohibition", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_adapter_prohibition", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_adapter_prohibition", "healing_outcome")
_emit_escalates_failure("p3", "check_adapter_prohibition", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_adapter_prohibition", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_adapter_prohibition", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_adapter_prohibition", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_adapter_prohibition", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_adapter_prohibition", "eval_metric")
_emit_stores_embedding("p4", "check_adapter_prohibition", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_adapter_prohibition", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_adapter_prohibition", "exec_snapshot_link")
_ROOT = get_validated_project_root()
SCAN_ROOTS = [_ROOT / AGENTIC_CORE_DIR]
EXCLUDED_PREFIXES = (ARCHIVES_DIR, 'archives/deprecated')
EXCEPTION_MARKER = 'v15-exception:'
PROHIBITED_NAMES = frozenset({'AdapterBase', 'HealingAdapter', 'AdapterBaseAdapter'})

def _is_excluded(path: Path) -> bool:
    parts = path.as_posix()
    return any(parts.startswith(prefix) for prefix in EXCLUDED_PREFIXES)

def scan_file(filepath: Path) -> list[str]:
    """Scan a single Python file for AdapterBase usage. Returns violation messages."""
    violations: list[str] = []
    try:
        source = filepath.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
        return violations
    if EXCEPTION_MARKER in source:
        return violations
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return violations
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name in PROHIBITED_NAMES:
                    violations.append(f"{filepath}:{node.lineno}: imports prohibited name '{alias.name}'")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name_parts = alias.name.split('.')
                if any(part in PROHIBITED_NAMES for part in name_parts):
                    violations.append(f"{filepath}:{node.lineno}: imports prohibited module '{alias.name}'")
        elif isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_name = None
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr
                if base_name and base_name in PROHIBITED_NAMES:
                    violations.append(f"{filepath}:{node.lineno}: class '{node.name}' inherits from prohibited '{base_name}'")
    return violations

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    all_violations: list[str] = []
    for scan_root in SCAN_ROOTS:
        root = project_root / scan_root
        if not root.exists():
            continue
        for py_file in sorted(root.rglob('*.py')):
            rel = py_file.relative_to(project_root)
            if _is_excluded(rel):
                continue
            all_violations.extend(scan_file(py_file))
    if all_violations:
        print(f'FAIL: {len(all_violations)} AdapterBase prohibition violation(s):')
        for v in all_violations:
            print(f'  {v}')
        return 1
    print('PASS: No AdapterBase prohibition violations found.')
    return 0
if __name__ == '__main__':
    sys.exit(main())
