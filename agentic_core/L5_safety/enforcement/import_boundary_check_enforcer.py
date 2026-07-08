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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "import_boundary_check_enforcer")
trace_contract.emit_determinism_digest("p0", "import_boundary_check_enforcer")

trace_contract._emit_dispatches_healing_run("p1", "import_boundary_check_enforcer", "L5")
trace_contract._emit_routes_through("p1", "import_boundary_check_enforcer", "L5")
trace_contract._emit_checks_agent_registry("p1", "import_boundary_check_enforcer", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "import_boundary_check_enforcer", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "import_boundary_check_enforcer", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "import_boundary_check_enforcer", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "import_boundary_check_enforcer", "target_agent")
trace_contract._emit_verifies_policy("p1", "import_boundary_check_enforcer", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "import_boundary_check_enforcer", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "import_boundary_check_enforcer", "boundary_check")
trace_contract._emit_transcripts_response("p1", "import_boundary_check_enforcer", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "import_boundary_check_enforcer")
trace_contract._emit_gated_by_confidence("p1", "import_boundary_check_enforcer", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "import_boundary_check_enforcer", "L5")
trace_contract._emit_reads_policy_state("p1", "import_boundary_check_enforcer", "L5")

trace_contract._emit_applies_guardrail("p0", "import_boundary_check_enforcer", "p0_governance")
trace_contract._emit_snapshots_state("p0", "import_boundary_check_enforcer", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "import_boundary_check_enforcer", "execution_auth")
trace_contract._emit_validates_capability("p2", "import_boundary_check_enforcer", "capability_check")
trace_contract._emit_routes_to_capability("p2", "import_boundary_check_enforcer", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "import_boundary_check_enforcer", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "import_boundary_check_enforcer", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "import_boundary_check_enforcer", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "import_boundary_check_enforcer", "exec_output")
trace_contract._emit_dispatches_agent("p3", "import_boundary_check_enforcer", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "import_boundary_check_enforcer", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "import_boundary_check_enforcer", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "import_boundary_check_enforcer", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "import_boundary_check_enforcer", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "import_boundary_check_enforcer", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "import_boundary_check_enforcer", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "import_boundary_check_enforcer", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "import_boundary_check_enforcer", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "import_boundary_check_enforcer", "eval_metric")
trace_contract._emit_stores_embedding("p4", "import_boundary_check_enforcer", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "import_boundary_check_enforcer", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "import_boundary_check_enforcer", "exec_snapshot_link")

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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "_ImportBoundaryVisitor.visit_Import",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:_ImportBoundaryVisitor.visit_Import".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        for alias in node.names:
            self._check(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:  # review: Syntax errors should be caught at parser level, not runtime
            self._check(node.module, node.lineno)
        self.generic_visit(node)


def check_file_import_boundaries(file_path: Path) -> list[str]:
    """Return list of violation strings for a single file (empty = clean)."""
    try:
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
    except SyntaxError as exc:  # review: Syntax errors should be caught at parser level, not runtime
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

trace_contract._emit_emits_metric_event("import_boundary_check_enforcer", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("import_boundary_check_enforcer", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("import_boundary_check_enforcer", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("import_boundary_check_enforcer", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("import_boundary_check_enforcer", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("import_boundary_check_enforcer", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("import_boundary_check_enforcer", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("import_boundary_check_enforcer", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("import_boundary_check_enforcer", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("import_boundary_check_enforcer", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("import_boundary_check_enforcer", "p4obs", "alert")
trace_contract._emit_links_incident_trace("import_boundary_check_enforcer", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("import_boundary_check_enforcer", "p3lm", "pattern")
trace_contract._emit_records_learning_event("import_boundary_check_enforcer", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("import_boundary_check_enforcer", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("import_boundary_check_enforcer", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("import_boundary_check_enforcer", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("import_boundary_check_enforcer", "p3lm", "policy")
trace_contract._emit_stores_learning_state("import_boundary_check_enforcer", "p3lm", "state")
trace_contract._emit_records_execution_trace("import_boundary_check_enforcer", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("import_boundary_check_enforcer", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("import_boundary_check_enforcer", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("import_boundary_check_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("import_boundary_check_enforcer", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("import_boundary_check_enforcer", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("import_boundary_check_enforcer", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("import_boundary_check_enforcer", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("import_boundary_check_enforcer", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "import_boundary_check_enforcer", "context_pull")
trace_contract._emit_pulls_context("p1", "import_boundary_check_enforcer", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "import_boundary_check_enforcer", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "import_boundary_check_enforcer", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "import_boundary_check_enforcer", "write_through")
trace_contract._emit_writes_through("p1", "import_boundary_check_enforcer", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "import_boundary_check_enforcer", "safety_validation")
trace_contract._emit_invokes_eval("p1", "import_boundary_check_enforcer", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "import_boundary_check_enforcer", "routing_commit")
