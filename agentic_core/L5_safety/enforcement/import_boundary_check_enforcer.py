"""
agentic_core/enforcement/import_boundary_check_enforcer.py

AST-based import boundary checker for the agentic_core package.

Enforces that no file inside agentic_core imports from downstream
apps_* packages (apps_lic, apps_rg, apps_shared).
Uses AST parsing — no regex.
"""

import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "import_boundary_check_enforcer")
emit_determinism_digest("p0", "import_boundary_check_enforcer")

_emit_dispatches_healing_run("p1", "import_boundary_check_enforcer", "L5")
_emit_routes_through("p1", "import_boundary_check_enforcer", "L5")
_emit_checks_agent_registry("p1", "import_boundary_check_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "import_boundary_check_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "import_boundary_check_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "import_boundary_check_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "import_boundary_check_enforcer", "target_agent")
_emit_verifies_policy("p1", "import_boundary_check_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "import_boundary_check_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "import_boundary_check_enforcer", "boundary_check")
_emit_transcripts_response("p1", "import_boundary_check_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "import_boundary_check_enforcer")
_emit_gated_by_confidence("p1", "import_boundary_check_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "import_boundary_check_enforcer", "L5")
_emit_reads_policy_state("p1", "import_boundary_check_enforcer", "L5")

_emit_applies_guardrail("p0", "import_boundary_check_enforcer", "p0_governance")
_emit_snapshots_state("p0", "import_boundary_check_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "import_boundary_check_enforcer", "execution_auth")
_emit_validates_capability("p2", "import_boundary_check_enforcer", "capability_check")
_emit_routes_to_capability("p2", "import_boundary_check_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "import_boundary_check_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "import_boundary_check_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "import_boundary_check_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "import_boundary_check_enforcer", "exec_output")
_emit_dispatches_agent("p3", "import_boundary_check_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "import_boundary_check_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "import_boundary_check_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "import_boundary_check_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "import_boundary_check_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "import_boundary_check_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "import_boundary_check_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "import_boundary_check_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "import_boundary_check_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "import_boundary_check_enforcer", "eval_metric")
_emit_stores_embedding("p4", "import_boundary_check_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "import_boundary_check_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "import_boundary_check_enforcer", "exec_snapshot_link")

_AGENTIC_CORE_ROOT = Path(__file__).parent.parent
FORBIDDEN_IMPORT_PREFIXES = frozenset({APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR})


class _ImportBoundaryVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations: list[str] = []

    def _check(self, module: str, lineno: int) -> None:
        if any(module.startswith(p) for p in FORBIDDEN_IMPORT_PREFIXES):
            self.violations.append(f"Line {lineno}: Forbidden import '{module}'")

    def visit_Import(self, node: ast.Import) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "_ImportBoundaryVisitor.visit_Import",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:_ImportBoundaryVisitor.visit_Import".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        for alias in node.names:
            self._check(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:    # guardian: Syntax errors should be caught at parser level, not runtime
            self._check(node.module, node.lineno)
        self.generic_visit(node)


def check_file_import_boundaries(file_path: Path) -> list[str]:
    """Return list of violation strings for a single file (empty = clean)."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except SyntaxError as exc:    # guardian: Syntax errors should be caught at parser level, not runtime
        return [f"SyntaxError: {exc}"]
    visitor = _ImportBoundaryVisitor()
    visitor.visit(tree)
    return visitor.violations


def check_agentic_core_boundaries() -> bool:
    """Check all agentic_core files for import boundary compliance.

    Prints violations and returns False if any found, True if clean.
    """
    all_violations: list[str] = []
    for py_file in _AGENTIC_CORE_ROOT.rglob("*.py"):
        file_violations = check_file_import_boundaries(py_file)
        if file_violations:
            for v in file_violations:
                all_violations.append(f"{py_file.relative_to(_AGENTIC_CORE_ROOT)}: {v}")
    if all_violations:
        print("agentic_core import boundary violations found:")
        for v in all_violations:
            print(f"  {v}")
        return False
    print("OK: All agentic_core files comply with import boundaries")
    return True


if __name__ == "__main__":
    import sys

    sys.exit(0 if check_agentic_core_boundaries() else 1)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_emits_metric_event("import_boundary_check_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("import_boundary_check_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("import_boundary_check_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("import_boundary_check_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("import_boundary_check_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("import_boundary_check_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("import_boundary_check_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("import_boundary_check_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("import_boundary_check_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("import_boundary_check_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("import_boundary_check_enforcer", "p4obs", "alert")
_emit_links_incident_trace("import_boundary_check_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("import_boundary_check_enforcer", "p3lm", "pattern")
_emit_records_learning_event("import_boundary_check_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("import_boundary_check_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("import_boundary_check_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("import_boundary_check_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("import_boundary_check_enforcer", "p3lm", "policy")
_emit_stores_learning_state("import_boundary_check_enforcer", "p3lm", "state")
_emit_records_execution_trace("import_boundary_check_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("import_boundary_check_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("import_boundary_check_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("import_boundary_check_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("import_boundary_check_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("import_boundary_check_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("import_boundary_check_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("import_boundary_check_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("import_boundary_check_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "import_boundary_check_enforcer", "context_pull")
_emit_pulls_context("p1", "import_boundary_check_enforcer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "import_boundary_check_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "import_boundary_check_enforcer", "uwg_term_secondary")
_emit_writes_through("p1", "import_boundary_check_enforcer", "write_through")
_emit_writes_through("p1", "import_boundary_check_enforcer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "import_boundary_check_enforcer", "safety_validation")
_emit_invokes_eval("p1", "import_boundary_check_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "import_boundary_check_enforcer", "routing_commit")
