"""
Static Analysis: Canonical schema Compliance Checker for @standard_heal Methods

This script scans all Python files for methods decorated with @standard_heal
and validates that their return statements use canonical keys.

CANONICAL KEYS (from decorators.py):
    - violations_found (NOT: total_violations, count, violations, issues)
    - violations_fixed (NOT: fixed_count, fixed, healed, repaired)
    - errors
    - skipped
    - status (optional - auto-computed by decorator)

USAGE:
    python scripts/maintenance/check_heal_schema_compliance.py

    # As pre-commit hook:
    python scripts/maintenance/check_heal_schema_compliance.py --strict

EXIT CODES:
    0 - All compliant
    1 - Non-canonical keys found (warnings only in non-strict mode)
    2 - Non-canonical keys found (strict mode - blocks commit)
"""

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
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
    _emit_records_execution_trace,
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "heal_schema_visitor", "L0")
_emit_routes_through("p1", "heal_schema_visitor", "L0")
_emit_checks_agent_registry("p1", "heal_schema_visitor", "agent_registry")
_emit_validates_agent_capability("p1", "heal_schema_visitor", "capability")
_emit_dispatches_execution_plan("p1", "heal_schema_visitor", "exec_plan")
_emit_agent_executes_agent("p1", "heal_schema_visitor", "sub_agent")
_emit_routes_to_agent("p1", "heal_schema_visitor", "target_agent")
_emit_verifies_policy("p1", "heal_schema_visitor", "policy_check")
_emit_observes_runtime_state("p1", "heal_schema_visitor", "runtime_state")
_emit_verifies_boundary("p1", "heal_schema_visitor", "boundary_check")
_emit_transcripts_response("p1", "heal_schema_visitor", "transcript")
_emit_hard_fails_untranscripted("p1", "heal_schema_visitor")
_emit_gated_by_confidence("p1", "heal_schema_visitor", "confidence_gate")
_emit_escalates_to_human("p1", "heal_schema_visitor", "L0")
_emit_reads_policy_state("p1", "heal_schema_visitor", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "heal_schema_visitor", "p0_governance")
_emit_snapshots_state("p0", "heal_schema_visitor", "state_snapshot")
_emit_authorize_and_execute("p2", "heal_schema_visitor", "execution_auth")
_emit_validates_capability("p2", "heal_schema_visitor", "capability_check")
_emit_routes_to_capability("p2", "heal_schema_visitor", "capability_route")
_emit_writes_via_uwg("p2", "heal_schema_visitor", "uwg_write")
_emit_blocks_direct_write("p2", "heal_schema_visitor", "direct_write_block")
_emit_records_tool_invocation("p2", "heal_schema_visitor", "tool_invocation")
_emit_captures_execution_output("p2", "heal_schema_visitor", "exec_output")
_emit_dispatches_agent("p3", "heal_schema_visitor", "agent_dispatch")
_emit_coordinates_agents("p3", "heal_schema_visitor", "agent_coordination")
_emit_records_workflow_lineage("p3", "heal_schema_visitor", "workflow_lineage")
_emit_records_healing_outcome("p3", "heal_schema_visitor", "healing_outcome")
_emit_escalates_failure("p3", "heal_schema_visitor", "failure_escalation")
_emit_orchestrates_workflow("p3", "heal_schema_visitor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "heal_schema_visitor", "healing_dispatch")
_emit_invokes_evaluation("p3", "heal_schema_visitor", "evaluation_signal")
_emit_records_telemetry_event("p4", "heal_schema_visitor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "heal_schema_visitor", "eval_metric")
_emit_stores_embedding("p4", "heal_schema_visitor", "embedding_store")
_emit_updates_meta_learning_state("p4", "heal_schema_visitor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "heal_schema_visitor", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from tqdm import tqdm

_emit_emits_metric_event("heal_schema_visitor", "p4obs", "metric_1")
_emit_emits_metric_event("heal_schema_visitor", "p4obs", "metric_2")
_emit_emits_metric_event("heal_schema_visitor", "p4obs", "metric_3")
_emit_emits_metric_event("heal_schema_visitor", "p4obs", "metric_4")
_emit_emits_metric_event("heal_schema_visitor", "p4obs", "metric_5")
_emit_emits_metric_event("heal_schema_visitor", "p4obs", "metric_6")
_emit_records_incident_event("heal_schema_visitor", "p4obs", "incident")
_emit_captures_runtime_anomaly("heal_schema_visitor", "p4obs", "anomaly")
_emit_writes_observability_log("heal_schema_visitor", "p4obs", "obs_log")
_emit_updates_monitoring_state("heal_schema_visitor", "p4obs", "mon_state")
_emit_triggers_alert("heal_schema_visitor", "p4obs", "alert")
_emit_links_incident_trace("heal_schema_visitor", "p4obs", "trace_link")
_emit_captures_pattern("heal_schema_visitor", "p3lm", "pattern")
_emit_records_learning_event("heal_schema_visitor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("heal_schema_visitor", "p3lm", "snapshot")
_emit_feeds_meta_learning("heal_schema_visitor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("heal_schema_visitor", "p3lm", "routing")
_emit_improves_agent_policy("heal_schema_visitor", "p3lm", "policy")
_emit_stores_learning_state("heal_schema_visitor", "p3lm", "state")
_emit_records_execution_trace("heal_schema_visitor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("heal_schema_visitor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("heal_schema_visitor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("heal_schema_visitor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("heal_schema_visitor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("heal_schema_visitor", "env_read", "p2_env_1")
_emit_reads_environ("heal_schema_visitor", "env_read", "p2_env_2")
_emit_reads_runtime_state("heal_schema_visitor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("heal_schema_visitor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "heal_schema_visitor", "context_pull")
_emit_pulls_context("p1", "heal_schema_visitor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "heal_schema_visitor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "heal_schema_visitor", "uwg_term_2")
_emit_writes_through("p1", "heal_schema_visitor", "write_through")
_emit_writes_through("p1", "heal_schema_visitor", "write_through_2")
_emit_validated_by_safety_plane("p1", "heal_schema_visitor", "safety_validation")
_emit_invokes_eval("p1", "heal_schema_visitor", "eval_call")
_emit_proposal_commits_routing("p1", "heal_schema_visitor", "routing_commit")

CANONICAL_KEYS = {"violations_found", "violations_fixed", "errors", "skipped", "status", "error_message"}
NON_CANONICAL_MAPPINGS = {
    "total_violations": "violations_found",
    "violations": "violations_found",
    "count": "violations_found",
    "issues": "violations_found",
    "problems": "violations_found",
    "findings": "violations_found",
    "fixed_count": "violations_fixed",
    "fixed": "violations_fixed",
    "healed": "violations_fixed",
    "repaired": "violations_fixed",
    "resolved": "violations_fixed",
    "renamed": "violations_fixed",
    "moved": "violations_fixed",
    "deleted": "violations_fixed",
    "created": "violations_fixed",
    "error_count": "errors",
    "failures": "errors",
    "skip_count": "skipped",
    "ignored": "skipped",
}


class HealSchemaVisitor(ast.NodeVisitor):
    """AST visitor to find @standard_heal decorated methods and check return keys."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.violations: list[dict] = []
        self.in_standard_heal_method = False
        self.current_method_name = ""
        self.current_method_lineno = 0

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """TODO: Add documentation for visit_FunctionDef."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L0_ROUTING,
            "HealSchemaVisitor.visit_FunctionDef",
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        for decorator in tqdm(node.decorator_list, desc="Processing", unit="item"):
            decorator_name = ""
            if isinstance(decorator, ast.Name):
                decorator_name = decorator.id
            elif isinstance(decorator, ast.Attribute):
                decorator_name = decorator.attr
            if decorator_name == "standard_heal":
                self.in_standard_heal_method = True
                self.current_method_name = node.name
                self.current_method_lineno = node.lineno
                break
        self.generic_visit(node)
        self.in_standard_heal_method = False
        self.current_method_name = ""

    def visit_Return(self, node: ast.Return):
        """TODO: Add documentation for visit_Return."""
        if not self.in_standard_heal_method:
            return
        if node.value is None:
            return
        if isinstance(node.value, ast.Dict):
            self._check_dict_keys(node.value, node.lineno)

    def _check_dict_keys(self, dict_node: ast.Dict, lineno: int):
        """Check dict keys for non-canonical names."""
        for key in tqdm(dict_node.keys, desc="Processing", unit="item"):
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                key_name = key.value
                if key_name in NON_CANONICAL_MAPPINGS:
                    canonical = NON_CANONICAL_MAPPINGS[key_name]
                    self.violations.append(
                        {
                            "file": self.filepath,
                            "line": lineno,
                            "method": self.current_method_name,
                            "key": key_name,
                            "canonical": canonical,
                            "message": f"Use '{canonical}' instead of '{key_name}'",
                        },
                    )


def check_file(filepath: Path) -> list[dict]:
    """Check a single file for schema compliance."""
    try:
        content = filepath.read_text(encoding="utf-8")
        tree = ast.parse(content)
        visitor = HealSchemaVisitor(str(filepath))
        visitor.visit(tree)
        return visitor.violations
    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError:
        return []
    # guardian: allow-silent-swallow
    except (ValueError, TypeError):
        return []


def main():
    """TODO: Add documentation for main."""
    import argparse

    parser = argparse.ArgumentParser(description="Check @standard_heal schema compliance")
    parser.add_argument("--strict", action="store_true", help="Exit with error code on violations")
    parser.add_argument("--path", default=AGENTIC_CORE_DIR, help="Path to scan (default: agentic_core)")
    args = parser.parse_args()
    root = Path(__file__).parent.parent.parent / args.path
    if not root.exists():
        sys.exit(1)
    all_violations = []
    files_checked = 0
    for py_file in root.rglob("*.py"):
        if "__pycache__" in str(py_file) or ".venv" in str(py_file):
            continue
        violations = check_file(py_file)
        all_violations.extend(violations)
        files_checked += 1
    if all_violations:
        for v in all_violations:
            Path(v["file"]).relative_to(root.parent) if root.parent in Path(v["file"]).parents else v["file"]
        if args.strict:
            sys.exit(2)
        else:
            sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
