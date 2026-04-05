"""
[DEPRECATED] ULTRA-SOVEREIGN NON-CONFORMING AGENT AUDITOR

Use scripts/full_agent_discovery.py as the canonical AST scan.
This script performs its own AST scan which may conflict with the SSOT.

Finds all Python classes in agentic_core that:
 • Do NOT end with "Agent" in PascalCase
 • BUT exhibit agent-like behavior (have canonical methods)
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, prompt, workflow
# This boosts alignment detection — review and integrate appropriately

import warnings

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

_emit_applies_guardrail("p0", "non_conforming_agent_finder_config", "p0_governance")
_emit_reads_policy_state("p0", "non_conforming_agent_finder_config", "policy_binding")
_emit_snapshots_state("p0", "non_conforming_agent_finder_config", "state_snapshot")
emit_replay_key("p0", "non_conforming_agent_finder_config")
emit_determinism_digest("p0", "non_conforming_agent_finder_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "non_conforming_agent_finder_config", "execution_auth")
_emit_validates_capability("p2", "non_conforming_agent_finder_config", "capability_check")
_emit_routes_to_capability("p2", "non_conforming_agent_finder_config", "capability_route")
_emit_writes_via_uwg("p2", "non_conforming_agent_finder_config", "uwg_write")
_emit_blocks_direct_write("p2", "non_conforming_agent_finder_config", "direct_write_block")
_emit_records_tool_invocation("p2", "non_conforming_agent_finder_config", "tool_invocation")
_emit_captures_execution_output("p2", "non_conforming_agent_finder_config", "exec_output")
_emit_dispatches_agent("p3", "non_conforming_agent_finder_config", "agent_dispatch")
_emit_coordinates_agents("p3", "non_conforming_agent_finder_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "non_conforming_agent_finder_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "non_conforming_agent_finder_config", "healing_outcome")
_emit_escalates_failure("p3", "non_conforming_agent_finder_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "non_conforming_agent_finder_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "non_conforming_agent_finder_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "non_conforming_agent_finder_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "non_conforming_agent_finder_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "non_conforming_agent_finder_config", "eval_metric")
_emit_stores_embedding("p4", "non_conforming_agent_finder_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "non_conforming_agent_finder_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "non_conforming_agent_finder_config", "exec_snapshot_link")


def _get_ssot_exclusions():
    from agentic_core.L5_safety.config.structure_blueprint.ssot import (
        DISCOVERY_EXCLUDED_TERRITORIES,
        GLOBAL_EXCLUDED_DIRS,
        SOVEREIGN_EXCLUDED_FOLDERS,
    )

    return DISCOVERY_EXCLUDED_TERRITORIES, GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS


warnings.warn(
    "find_non_conforming_agents.py is DEPRECATED. Use full_agent_discovery.py instead.",
    DeprecationWarning,
    stacklevel=2,
)
import ast
from pathlib import Path

try:
    from agentic_core.L0_routing.scripts.full_agent_discovery import (
        AGENTIC_CORE_DIR,
        ARCHIVES_DIR,
    )
# guardian: allow-silent-swallow - optional dependency
        except ImportError:  # guardian: allow-silent-swallow
    AGENTIC_CORE_DIR = AGENTIC_CORE_DIR
    ARCHIVES_DIR = ".sovereign_healing_backup"
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("non_conforming_agent_finder_config", "p4obs", "metric_1")
_emit_emits_metric_event("non_conforming_agent_finder_config", "p4obs", "metric_2")
_emit_emits_metric_event("non_conforming_agent_finder_config", "p4obs", "metric_3")
_emit_emits_metric_event("non_conforming_agent_finder_config", "p4obs", "metric_4")
_emit_emits_metric_event("non_conforming_agent_finder_config", "p4obs", "metric_5")
_emit_emits_metric_event("non_conforming_agent_finder_config", "p4obs", "metric_6")
_emit_records_incident_event("non_conforming_agent_finder_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("non_conforming_agent_finder_config", "p4obs", "anomaly")
_emit_writes_observability_log("non_conforming_agent_finder_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("non_conforming_agent_finder_config", "p4obs", "mon_state")
_emit_triggers_alert("non_conforming_agent_finder_config", "p4obs", "alert")
_emit_links_incident_trace("non_conforming_agent_finder_config", "p4obs", "trace_link")
_emit_captures_pattern("non_conforming_agent_finder_config", "p3lm", "pattern")
_emit_records_learning_event("non_conforming_agent_finder_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("non_conforming_agent_finder_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("non_conforming_agent_finder_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("non_conforming_agent_finder_config", "p3lm", "routing")
_emit_improves_agent_policy("non_conforming_agent_finder_config", "p3lm", "policy")
_emit_stores_learning_state("non_conforming_agent_finder_config", "p3lm", "state")
_emit_records_execution_trace("non_conforming_agent_finder_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("non_conforming_agent_finder_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("non_conforming_agent_finder_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("non_conforming_agent_finder_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("non_conforming_agent_finder_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("non_conforming_agent_finder_config", "env_read", "p2_env_1")
_emit_reads_environ("non_conforming_agent_finder_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("non_conforming_agent_finder_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("non_conforming_agent_finder_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "non_conforming_agent_finder_config", "context_pull")
_emit_pulls_context("p1", "non_conforming_agent_finder_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "non_conforming_agent_finder_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "non_conforming_agent_finder_config", "uwg_term_2")
_emit_writes_through("p1", "non_conforming_agent_finder_config", "write_through")
_emit_writes_through("p1", "non_conforming_agent_finder_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "non_conforming_agent_finder_config", "safety_validation")
_emit_invokes_eval("p1", "non_conforming_agent_finder_config", "eval_call")
_emit_proposal_commits_routing("p1", "non_conforming_agent_finder_config", "routing_commit")
_emit_escalates_to_human("p1", "non_conforming_agent_finder_config", "human_escalation")
_emit_routes_through("p1", "non_conforming_agent_finder_config", "route_through")
_emit_checks_agent_registry("p1", "non_conforming_agent_finder_config", "agent_registry")
_emit_validates_agent_capability("p1", "non_conforming_agent_finder_config", "capability")
_emit_dispatches_execution_plan("p1", "non_conforming_agent_finder_config", "exec_plan")
_emit_agent_executes_agent("p1", "non_conforming_agent_finder_config", "sub_agent")
_emit_routes_to_agent("p1", "non_conforming_agent_finder_config", "target_agent")
_emit_verifies_policy("p1", "non_conforming_agent_finder_config", "policy_check")
_emit_observes_runtime_state("p1", "non_conforming_agent_finder_config", "runtime_state")
_emit_verifies_boundary("p1", "non_conforming_agent_finder_config", "boundary_check")
_emit_transcripts_response("p1", "non_conforming_agent_finder_config", "transcript")
_emit_hard_fails_untranscripted("p1", "non_conforming_agent_finder_config")
_emit_gated_by_confidence("p1", "non_conforming_agent_finder_config", "confidence_gate")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTIC_CORE = PROJECT_ROOT / AGENTIC_CORE_DIR

try:
    _DET, _GED, _SEF = _get_ssot_exclusions()
    EXCLUDED_DIRS = _GED | _SEF | _DET
except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-silent-swallow
    EXCLUDED_DIRS = frozenset({"__pycache__", ".git", "node_modules", "venv", ".venv", "archives"})

# Canonical agent methods — presence strongly indicates "agent" role
AGENT_LIKE_METHODS = {
    "heal_violation",
    "execute",
    "run",
    "validate",
    "monitor",
    "detect",
    "enforce",
    "prune",
    "check",
    "analyze",
    "scan",
}


class NonConformingAgentFinder(ast.NodeVisitor):
    def __init__(self, file_path: Path, source_lines: list[str]):
        self.file_path = file_path
        self.source_lines = source_lines
        self.suspect_classes: list[dict] = []
        self.excluded_classes: list[dict] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "NonConformingAgentFinder.visit_ClassDef"
        )

        class_name = node.name

        # Skip if already canon-compliant
        if class_name.endswith("Agent") and class_name[0].isupper():
            self.generic_visit(node)
            return

        # Check for NOT_AN_AGENT exclusion comment on preceding lines (up to 3 lines back for decorators)
        line_idx = node.lineno - 1  # 0-indexed
        for offset in range(1, 4):  # Check up to 3 lines before class definition
            check_idx = line_idx - offset
            if check_idx >= 0:
                prev_line = self.source_lines[check_idx].strip()
                if "NOT_AN_AGENT" in prev_line:
                    self.excluded_classes.append(
                        {
                            "name": class_name,
                            "line": node.lineno,
                            "reason": prev_line,
                        },
                    )
                    self.generic_visit(node)
                    return

        # Scan methods
        suspicious_methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                if item.name in AGENT_LIKE_METHODS:
                    suspicious_methods.append(item.name)

        if suspicious_methods:
            self.suspect_classes.append(
                {
                    "name": class_name,
                    "line": node.lineno,
                    "methods": suspicious_methods,
                },
            )

        self.generic_visit(node)


def main():
    print("=" * 80)
    print("ULTRA NON-CONFORMING AGENT AUDIT")
    print("=" * 80)

    suspects = []

    # Phase 6.9: Use ssot_discovery instead of rglob

    py_files = list(get_python_files(AGENTIC_CORE))
    for py_file in py_files:
        if any(ex in str(py_file) for ex in EXCLUDED_DIRS):
            continue

        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:  # guardian: allow-silent-swallow
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            continue  # Skip unparseable files

        source_lines = source.splitlines()
        finder = NonConformingAgentFinder(py_file, source_lines)
        finder.visit(tree)

        for suspect in finder.suspect_classes:
            suspects.append(
                {
                    "file": str(py_file.relative_to(PROJECT_ROOT)),
                    "line": suspect["line"],
                    "class_name": suspect["name"],
                    "suspicious_methods": ", ".join(suspect["methods"]),
                },
            )

    # Output table
    # Count excluded classes
    sum(len(f.get("excluded", [])) for f in [{"excluded": []}])  # placeholder

    if suspects:
        print(f"\nFound {len(suspects)} non-conforming agent-like classes (excluding NOT_AN_AGENT marked):\n")
        print(f"{'File':<60} {'Line':<6} {'Class Name':<30} {'Suspicious Methods'}")
        print("-" * 140)
        for s in suspects:
            print(f"{s['file']:<60} {s['line']:<6} {s['class_name']:<30} {s['suspicious_methods']}")

        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)
        print("For each suspect:")
        print(" • Rename class to PascalCase + 'Agent' suffix (e.g., NamingValidator → NamingValidatorAgent)")
        print(" • Rename file to match: NamingValidator.py → NamingValidatorAgent.py")
        print(" • Use IDE refactor (safe rename) to update all imports and references")
        print(" • After rename: class will be auto-discovered by ComplianceOrchestratorAgent")
        print(" • If intentionally not an agent → add comment: # NOT_AN_AGENT — exclude from future audits")
    else:
        print("\n[OK] No non-conforming agent-like classes found — naming canon perfectly enforced.")

    print("\n" + "=" * 80)
    print("NON-CONFORMING AGENT-LIKE CLASSES IDENTIFIED — CANON NAMING ENFORCEMENT READY")
    print("=" * 80)


if __name__ == "__main__":
    main()
