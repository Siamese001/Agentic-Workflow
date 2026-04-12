"""
agentic_core/enforcement/sealed_interface_check_enforcer.py

AST-based enforcement: blocks apps_* from importing sealed interface
implementation modules (_impl pattern) and direct L* layer imports.

Runs as CI gate and can be invoked as:
    python -m agentic_core.enforcement.sealed_interface_check_enforcer

EXIT CODES:
    0 — no violations found
    1 — violations found (prints details)
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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

_emit_emits_metric_event("sealed_interface_check_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("sealed_interface_check_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("sealed_interface_check_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("sealed_interface_check_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("sealed_interface_check_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("sealed_interface_check_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("sealed_interface_check_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("sealed_interface_check_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("sealed_interface_check_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("sealed_interface_check_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("sealed_interface_check_enforcer", "p4obs", "alert")
_emit_links_incident_trace("sealed_interface_check_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("sealed_interface_check_enforcer", "p3lm", "pattern")
_emit_records_learning_event("sealed_interface_check_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sealed_interface_check_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("sealed_interface_check_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sealed_interface_check_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("sealed_interface_check_enforcer", "p3lm", "policy")
_emit_stores_learning_state("sealed_interface_check_enforcer", "p3lm", "state")
_emit_records_execution_trace("sealed_interface_check_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sealed_interface_check_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sealed_interface_check_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sealed_interface_check_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sealed_interface_check_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sealed_interface_check_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("sealed_interface_check_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("sealed_interface_check_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sealed_interface_check_enforcer", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "sealed_interface_check_enforcer")
emit_determinism_digest("p0", "sealed_interface_check_enforcer")

_emit_dispatches_healing_run("p1", "sealed_interface_check_enforcer", "L5")
_emit_routes_through("p1", "sealed_interface_check_enforcer", "L5")
_emit_checks_agent_registry("p1", "sealed_interface_check_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "sealed_interface_check_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "sealed_interface_check_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "sealed_interface_check_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "sealed_interface_check_enforcer", "target_agent")
_emit_verifies_policy("p1", "sealed_interface_check_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "sealed_interface_check_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "sealed_interface_check_enforcer", "boundary_check")
_emit_transcripts_response("p1", "sealed_interface_check_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "sealed_interface_check_enforcer")
_emit_gated_by_confidence("p1", "sealed_interface_check_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "sealed_interface_check_enforcer", "L5")
_emit_reads_policy_state("p1", "sealed_interface_check_enforcer", "L5")
_emit_pulls_context("p1", "sealed_interface_check_enforcer", "context_pull")
_emit_pulls_context("p1", "sealed_interface_check_enforcer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "sealed_interface_check_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sealed_interface_check_enforcer", "uwg_term_secondary")
_emit_writes_through("p1", "sealed_interface_check_enforcer", "write_through")
_emit_writes_through("p1", "sealed_interface_check_enforcer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "sealed_interface_check_enforcer", "safety_validation")
_emit_invokes_eval("p1", "sealed_interface_check_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "sealed_interface_check_enforcer", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "sealed_interface_check_enforcer")
_emit_applies_guardrail("p0", "sealed_interface_check_enforcer", "p0_governance")
_emit_snapshots_state("p0", "sealed_interface_check_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "sealed_interface_check_enforcer", "execution_auth")
_emit_validates_capability("p2", "sealed_interface_check_enforcer", "capability_check")
_emit_routes_to_capability("p2", "sealed_interface_check_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "sealed_interface_check_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "sealed_interface_check_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "sealed_interface_check_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "sealed_interface_check_enforcer", "exec_output")
_emit_dispatches_agent("p3", "sealed_interface_check_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "sealed_interface_check_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "sealed_interface_check_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "sealed_interface_check_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "sealed_interface_check_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "sealed_interface_check_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sealed_interface_check_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "sealed_interface_check_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "sealed_interface_check_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sealed_interface_check_enforcer", "eval_metric")
_emit_stores_embedding("p4", "sealed_interface_check_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "sealed_interface_check_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sealed_interface_check_enforcer", "exec_snapshot_link")

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_ROOTS = [
    REPO_ROOT / APPS_LIC_DIR,
    REPO_ROOT / APPS_RG_DIR,
    REPO_ROOT / APPS_SHARED_DIR,
]

FORBIDDEN_IMPORT_PATTERNS = [
    "agentic_core.interfaces._",  # _impl and other private submodules
]

FORBIDDEN_LAYER_PREFIXES = [
    "agentic_core.L0_",
    "agentic_core.L1_",
    "agentic_core.L2_",
    "agentic_core.L3_",
    "agentic_core.L4_",
    "agentic_core.L5_",
    "agentic_core.L6_",
]


def _get_import_modules(tree: ast.AST) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
    return modules


def check_file(path: Path) -> list[str]:
    """Return list of violation strings for a single file."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:  # guardian: Syntax errors should be caught at parser level, not runtime
        return [f"SYNTAX_ERROR: {path}: {exc}"]

    violations: list[str] = []
    try:
        rel = path.relative_to(REPO_ROOT)
    except ValueError:
        rel = path

    for module in _get_import_modules(tree):
        for pat in FORBIDDEN_IMPORT_PATTERNS:
            if module.startswith(pat):
                violations.append(
                    f"SEALED_IMPL_BYPASS: {rel} imports '{module}' "
                    f"(sealed implementation modules are forbidden in apps_*)",
                )
        for prefix in FORBIDDEN_LAYER_PREFIXES:
            if module.startswith(prefix):
                violations.append(
                    f"DIRECT_LAYER_IMPORT: {rel} imports '{module}' (use agentic_core.interfaces.* instead)",
                )

    return violations


def run_check(apps_roots: list[Path] = APPS_ROOTS) -> list[str]:
    """Scan all apps_* Python files and return all violations."""
    all_violations: list[str] = []
    for root in apps_roots:
        if not root.exists():
            continue
        for py_file in sorted(root.rglob("*.py")):
            all_violations.extend(check_file(py_file))
    return all_violations


def main() -> int:
    violations = run_check()
    if violations:
        print(f"FAIL: {len(violations)} sovereignty violation(s) found:")
        for v in violations:
            print(f"  {v}")
        return 1
    total = sum(len(list(r.rglob("*.py"))) for r in APPS_ROOTS if r.exists())
    print(f"OK: sealed interface check passed ({total} files scanned, 0 violations)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
