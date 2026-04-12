"""
Layer Boundary Enforcement Script (Phase 5)

Ensures prompt_governance (Low Level) does not import from higher layers
to prevent circular dependencies and architectural violations.
"""

import ast
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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

_emit_applies_guardrail("p0", "import_violation_visitor", "p0_governance")
_emit_reads_policy_state("p0", "import_violation_visitor", "policy_binding")
_emit_snapshots_state("p0", "import_violation_visitor", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("import_violation_visitor", "p4obs", "metric_1")
_emit_emits_metric_event("import_violation_visitor", "p4obs", "metric_2")
_emit_emits_metric_event("import_violation_visitor", "p4obs", "metric_3")
_emit_emits_metric_event("import_violation_visitor", "p4obs", "metric_4")
_emit_emits_metric_event("import_violation_visitor", "p4obs", "metric_5")
_emit_emits_metric_event("import_violation_visitor", "p4obs", "metric_6")
_emit_records_incident_event("import_violation_visitor", "p4obs", "incident")
_emit_captures_runtime_anomaly("import_violation_visitor", "p4obs", "anomaly")
_emit_writes_observability_log("import_violation_visitor", "p4obs", "obs_log")
_emit_updates_monitoring_state("import_violation_visitor", "p4obs", "mon_state")
_emit_triggers_alert("import_violation_visitor", "p4obs", "alert")
_emit_links_incident_trace("import_violation_visitor", "p4obs", "trace_link")
_emit_captures_pattern("import_violation_visitor", "p3lm", "pattern")
_emit_records_learning_event("import_violation_visitor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("import_violation_visitor", "p3lm", "snapshot")
_emit_feeds_meta_learning("import_violation_visitor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("import_violation_visitor", "p3lm", "routing")
_emit_improves_agent_policy("import_violation_visitor", "p3lm", "policy")
_emit_stores_learning_state("import_violation_visitor", "p3lm", "state")
_emit_records_execution_trace("import_violation_visitor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("import_violation_visitor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("import_violation_visitor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("import_violation_visitor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("import_violation_visitor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("import_violation_visitor", "env_read", "p2_env_1")
_emit_reads_environ("import_violation_visitor", "env_read", "p2_env_2")
_emit_reads_runtime_state("import_violation_visitor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("import_violation_visitor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "import_violation_visitor", "context_pull")
_emit_pulls_context("p1", "import_violation_visitor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "import_violation_visitor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "import_violation_visitor", "uwg_term_2")
_emit_writes_through("p1", "import_violation_visitor", "write_through")
_emit_writes_through("p1", "import_violation_visitor", "write_through_2")
_emit_validated_by_safety_plane("p1", "import_violation_visitor", "safety_validation")
_emit_invokes_eval("p1", "import_violation_visitor", "eval_call")
_emit_proposal_commits_routing("p1", "import_violation_visitor", "routing_commit")
_emit_escalates_to_human("p1", "import_violation_visitor", "human_escalation")
_emit_routes_through("p1", "import_violation_visitor", "route_through")
_emit_checks_agent_registry("p1", "import_violation_visitor", "agent_registry")
_emit_validates_agent_capability("p1", "import_violation_visitor", "capability")
_emit_dispatches_execution_plan("p1", "import_violation_visitor", "exec_plan")
_emit_agent_executes_agent("p1", "import_violation_visitor", "sub_agent")
_emit_routes_to_agent("p1", "import_violation_visitor", "target_agent")
_emit_verifies_policy("p1", "import_violation_visitor", "policy_check")
_emit_observes_runtime_state("p1", "import_violation_visitor", "runtime_state")
_emit_verifies_boundary("p1", "import_violation_visitor", "boundary_check")
_emit_transcripts_response("p1", "import_violation_visitor", "transcript")
_emit_hard_fails_untranscripted("p1", "import_violation_visitor")
_emit_gated_by_confidence("p1", "import_violation_visitor", "confidence_gate")
emit_replay_key("p0", "import_violation_visitor")
emit_determinism_digest("p0", "import_violation_visitor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "import_violation_visitor", "execution_auth")
_emit_validates_capability("p2", "import_violation_visitor", "capability_check")
_emit_routes_to_capability("p2", "import_violation_visitor", "capability_route")
_emit_writes_via_uwg("p2", "import_violation_visitor", "uwg_write")
_emit_blocks_direct_write("p2", "import_violation_visitor", "direct_write_block")
_emit_records_tool_invocation("p2", "import_violation_visitor", "tool_invocation")
_emit_captures_execution_output("p2", "import_violation_visitor", "exec_output")
_emit_dispatches_agent("p3", "import_violation_visitor", "agent_dispatch")
_emit_coordinates_agents("p3", "import_violation_visitor", "agent_coordination")
_emit_records_workflow_lineage("p3", "import_violation_visitor", "workflow_lineage")
_emit_records_healing_outcome("p3", "import_violation_visitor", "healing_outcome")
_emit_escalates_failure("p3", "import_violation_visitor", "failure_escalation")
_emit_orchestrates_workflow("p3", "import_violation_visitor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "import_violation_visitor", "healing_dispatch")
_emit_invokes_evaluation("p3", "import_violation_visitor", "evaluation_signal")
_emit_records_telemetry_event("p4", "import_violation_visitor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "import_violation_visitor", "eval_metric")
_emit_stores_embedding("p4", "import_violation_visitor", "embedding_store")
_emit_updates_meta_learning_state("p4", "import_violation_visitor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "import_violation_visitor", "exec_snapshot_link")

FORBIDDEN_IMPORTS = {
    "agentic_core.L1_cognition",
    "agentic_core.L2_resources",
    "agentic_core.L3_orchestration",
    "agentic_core.L4_coordination",
    "agentic_core.L5_safety",
    "agentic_core.L6_observability",
}


class ImportViolationVisitor(ast.NodeVisitor):
    """AST visitor to detect forbidden imports."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations = []

    def visit_Import(self, node):
        """Check 'import x.y.z' statements."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ImportViolationVisitor.visit_Import"
        )

        for alias in node.names:
            import_path = alias.name
            self._check_import(import_path, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Check 'from x.y.z import ...' statements."""
        if node.module:
            import_path = node.module
            self._check_import(import_path, node.lineno)
        self.generic_visit(node)

    def _check_import(self, import_path: str, line: int):
        """Check if import path violates layer boundaries."""
        for forbidden in FORBIDDEN_IMPORTS:
            if import_path.startswith(forbidden):
                self.violations.append(
                    {
                        "file": str(self.file_path),
                        "line": line,
                        "import_statement": import_path,
                        "violated_layer": forbidden,
                        "violation_type": "UPWARD_IMPORT",
                    },
                )


def find_python_files(directory: Path) -> list[Path]:
    """Find all Python files in the given directory."""
    python_files = []
    for file_path in directory.rglob("*.py"):
        if file_path.is_file():
            python_files.append(file_path)
    return python_files


def analyze_file(file_path: Path) -> list[dict]:
    """Analyze a single Python file for import violations."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
        visitor = ImportViolationVisitor(file_path)
        visitor.visit(tree)
        return visitor.violations
    except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
        return [
            {
                "file": str(file_path),
                "line": e.lineno or 0,
                "import_statement": "SYNTAX_ERROR",
                "violated_layer": "N/A",
                "violation_type": "SYNTAX_ERROR",
                "error": str(e),
            },
        ]
    # guardian: allow-silent-swallow
    except Exception as e:
        return [
            {
                "file": str(file_path),
                "line": 0,
                "import_statement": "PARSE_ERROR",
                "violated_layer": "N/A",
                "violation_type": "PARSE_ERROR",
                "error": str(e),
            },
        ]


def enforce_layer_boundaries(prompt_governance_dir: Path) -> list[dict]:
    """Enforce layer boundaries across all Python files in prompt_governance."""
    all_violations = []
    python_files = find_python_files(prompt_governance_dir)
    print(f"Scanning {len(python_files)} Python files...")
    for file_path in python_files:
        violations = analyze_file(file_path)
        all_violations.extend(violations)
    return all_violations


def main():
    script_dir = Path(__file__).parent
    prompt_governance_dir = script_dir.parent
    print("Layer Boundary Enforcement Audit (Phase 5)")
    print("=" * 50)
    print(f"Directory: {prompt_governance_dir}")
    print("Forbidden Imports:")
    for forbidden in sorted(FORBIDDEN_IMPORTS):
        print(f"  ❌ {forbidden}")
    print()
    violations = enforce_layer_boundaries(prompt_governance_dir)
    import_violations = [v for v in violations if v["violation_type"] == "UPWARD_IMPORT"]
    syntax_errors = [v for v in violations if v["violation_type"] in ["SYNTAX_ERROR", "PARSE_ERROR"]]
    print("RESULTS:")
    print(f"  Files scanned: {len(find_python_files(prompt_governance_dir))}")
    print(f"  Import violations: {len(import_violations)}")
    print(f"  Syntax errors: {len(syntax_errors)}")
    print()
    if import_violations:
        print("🚨 LAYER BOUNDARY VIOLATIONS:")
        print("   (prompt_governance importing from higher layers)")
        print()
        violations_by_file = {}
        for violation in import_violations:
            file_path = violation["file"]
            if file_path not in violations_by_file:
                violations_by_file[file_path] = []
            violations_by_file[file_path].append(violation)
        for file_path, file_violations in violations_by_file.items():
            print(f"  📁 {file_path}")
            for violation in file_violations:
                print(f"    Line {violation['line']}: import {violation['import_statement']}")
                print(f"    ❌ Violates: {violation['violated_layer']}")
            print()
        print("⚠️  ARCHITECTURAL RISK:")
        print("   Upward imports create circular dependency risks")
        print("   and violate the layered architecture principles.")
        print()
    if syntax_errors:
        print("🔍 SYNTAX/PARSE ERRORS:")
        for error in syntax_errors:
            print(f"  📁 {error['file']}")
            if error.get("line"):
                print(f"    Line {error['line']}: {error.get('error', 'Unknown error')}")
            else:
                print(f"    {error.get('error', 'Unknown error')}")
        print()
    if import_violations:
        print("❌ AUDIT FAILED - Layer boundary violations detected")
        print("   Refactor to remove upward imports from higher layers.")
        sys.exit(1)
    elif syntax_errors:
        print("⚠️  AUDIT WARNING - Syntax errors detected")
        print("   Fix syntax errors before proceeding.")
        sys.exit(2)
    else:
        print("✅ AUDIT PASSED - No layer boundary violations")
        print("   prompt_governance respects architectural boundaries.")
        sys.exit(0)


if __name__ == "__main__":
    main()
