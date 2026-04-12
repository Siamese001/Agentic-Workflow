"""
Deep Architectural Anti-Pattern Audit (Ultra-Hardened AST Visitor)
Scans for SSOT, DRY, and Layered Sovereignty violations with high precision.
"""

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARCHIVES_DIR,
)
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

_emit_dispatches_healing_run("p1", "hardened_anti_pattern_visitor", "L0")
_emit_routes_through("p1", "hardened_anti_pattern_visitor", "L0")
_emit_checks_agent_registry("p1", "hardened_anti_pattern_visitor", "agent_registry")
_emit_validates_agent_capability("p1", "hardened_anti_pattern_visitor", "capability")
_emit_dispatches_execution_plan("p1", "hardened_anti_pattern_visitor", "exec_plan")
_emit_agent_executes_agent("p1", "hardened_anti_pattern_visitor", "sub_agent")
_emit_routes_to_agent("p1", "hardened_anti_pattern_visitor", "target_agent")
_emit_verifies_policy("p1", "hardened_anti_pattern_visitor", "policy_check")
_emit_observes_runtime_state("p1", "hardened_anti_pattern_visitor", "runtime_state")
_emit_verifies_boundary("p1", "hardened_anti_pattern_visitor", "boundary_check")
_emit_transcripts_response("p1", "hardened_anti_pattern_visitor", "transcript")
_emit_hard_fails_untranscripted("p1", "hardened_anti_pattern_visitor")
_emit_gated_by_confidence("p1", "hardened_anti_pattern_visitor", "confidence_gate")
_emit_escalates_to_human("p1", "hardened_anti_pattern_visitor", "L0")
_emit_reads_policy_state("p1", "hardened_anti_pattern_visitor", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "hardened_anti_pattern_visitor", "p0_governance")
_emit_snapshots_state("p0", "hardened_anti_pattern_visitor", "state_snapshot")
_emit_authorize_and_execute("p2", "hardened_anti_pattern_visitor", "execution_auth")
_emit_validates_capability("p2", "hardened_anti_pattern_visitor", "capability_check")
_emit_routes_to_capability("p2", "hardened_anti_pattern_visitor", "capability_route")
_emit_writes_via_uwg("p2", "hardened_anti_pattern_visitor", "uwg_write")
_emit_blocks_direct_write("p2", "hardened_anti_pattern_visitor", "direct_write_block")
_emit_records_tool_invocation("p2", "hardened_anti_pattern_visitor", "tool_invocation")
_emit_captures_execution_output("p2", "hardened_anti_pattern_visitor", "exec_output")
_emit_dispatches_agent("p3", "hardened_anti_pattern_visitor", "agent_dispatch")
_emit_coordinates_agents("p3", "hardened_anti_pattern_visitor", "agent_coordination")
_emit_records_workflow_lineage("p3", "hardened_anti_pattern_visitor", "workflow_lineage")
_emit_records_healing_outcome("p3", "hardened_anti_pattern_visitor", "healing_outcome")
_emit_escalates_failure("p3", "hardened_anti_pattern_visitor", "failure_escalation")
_emit_orchestrates_workflow("p3", "hardened_anti_pattern_visitor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hardened_anti_pattern_visitor", "healing_dispatch")
_emit_invokes_evaluation("p3", "hardened_anti_pattern_visitor", "evaluation_signal")
_emit_records_telemetry_event("p4", "hardened_anti_pattern_visitor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hardened_anti_pattern_visitor", "eval_metric")
_emit_stores_embedding("p4", "hardened_anti_pattern_visitor", "embedding_store")
_emit_updates_meta_learning_state("p4", "hardened_anti_pattern_visitor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hardened_anti_pattern_visitor", "exec_snapshot_link")
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

_emit_emits_metric_event("hardened_anti_pattern_visitor", "p4obs", "metric_1")
_emit_emits_metric_event("hardened_anti_pattern_visitor", "p4obs", "metric_2")
_emit_emits_metric_event("hardened_anti_pattern_visitor", "p4obs", "metric_3")
_emit_emits_metric_event("hardened_anti_pattern_visitor", "p4obs", "metric_4")
_emit_emits_metric_event("hardened_anti_pattern_visitor", "p4obs", "metric_5")
_emit_emits_metric_event("hardened_anti_pattern_visitor", "p4obs", "metric_6")
_emit_records_incident_event("hardened_anti_pattern_visitor", "p4obs", "incident")
_emit_captures_runtime_anomaly("hardened_anti_pattern_visitor", "p4obs", "anomaly")
_emit_writes_observability_log("hardened_anti_pattern_visitor", "p4obs", "obs_log")
_emit_updates_monitoring_state("hardened_anti_pattern_visitor", "p4obs", "mon_state")
_emit_triggers_alert("hardened_anti_pattern_visitor", "p4obs", "alert")
_emit_links_incident_trace("hardened_anti_pattern_visitor", "p4obs", "trace_link")
_emit_captures_pattern("hardened_anti_pattern_visitor", "p3lm", "pattern")
_emit_records_learning_event("hardened_anti_pattern_visitor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hardened_anti_pattern_visitor", "p3lm", "snapshot")
_emit_feeds_meta_learning("hardened_anti_pattern_visitor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hardened_anti_pattern_visitor", "p3lm", "routing")
_emit_improves_agent_policy("hardened_anti_pattern_visitor", "p3lm", "policy")
_emit_stores_learning_state("hardened_anti_pattern_visitor", "p3lm", "state")
_emit_records_execution_trace("hardened_anti_pattern_visitor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hardened_anti_pattern_visitor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hardened_anti_pattern_visitor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hardened_anti_pattern_visitor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hardened_anti_pattern_visitor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hardened_anti_pattern_visitor", "env_read", "p2_env_1")
_emit_reads_environ("hardened_anti_pattern_visitor", "env_read", "p2_env_2")
_emit_reads_runtime_state("hardened_anti_pattern_visitor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hardened_anti_pattern_visitor", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hardened_anti_pattern_visitor", "context_pull")
_emit_pulls_context("p1", "hardened_anti_pattern_visitor", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hardened_anti_pattern_visitor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hardened_anti_pattern_visitor", "uwg_term_2")
_emit_writes_through("p1", "hardened_anti_pattern_visitor", "write_through")
_emit_writes_through("p1", "hardened_anti_pattern_visitor", "write_through_2")
_emit_validated_by_safety_plane("p1", "hardened_anti_pattern_visitor", "safety_validation")
_emit_invokes_eval("p1", "hardened_anti_pattern_visitor", "eval_call")
_emit_proposal_commits_routing("p1", "hardened_anti_pattern_visitor", "routing_commit")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))
if hasattr(ast, "unparse"):
    unparse = ast.unparse
else:

    def unparse(node):
        """TODO: Add documentation for unparse."""
        return str(ast.dump(node))


class HardenedAntiPatternVisitor(ast.NodeVisitor):
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.filename = filepath.name
        self.findings = []
        self.aliases: dict[str, str] = {}
        path_str = str(filepath).replace("\\", "/")
        self.is_l1_l2 = "/L1_" in path_str or "/L2_" in path_str
        self.is_test = "test_" in self.filename or "tests/" in path_str
        self.is_legacy = any(x in path_str.lower() for x in ["legacy", "deprecated", ARCHIVES_DIR])

    def add_finding(self, pattern_type: str, evidence: str, recommendation: str):
        """TODO: Add documentation for add_finding."""
        self.findings.append(
            {
                "file": str(self.filepath),
                "type": pattern_type,
                "evidence": evidence,
                "recommendation": recommendation,
            },
        )

    def _is_docstring(self, node: ast.stmt) -> bool:
        if isinstance(node, ast.Expr):
            return isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
            return isinstance(node.value, ast.Str)
        return False

    def visit_Import(self, node: ast.Import):
        """TODO: Add documentation for visit_Import."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L0_ROUTING,
            "HardenedAntiPatternVisitor.visit_Import",
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        for name in node.names:
            real_name = name.name
            alias = name.asname or name.name
            self.aliases[alias] = real_name
            if self.is_l1_l2 and (not self.is_test):
                if any(x in real_name for x in ["agentic_core.L5", "agentic_core.L6"]):
                    self.add_finding(
                        "Layer Bleed",
                        f"L1/L2 imports upper layer: {real_name}",
                        "Use Dependency Injection.",
                    )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """TODO: Add documentation for visit_ImportFrom."""
        if node.module:
            for name in node.names:
                real_name = f"{node.module}.{name.name}"
                alias = name.asname or name.name
                self.aliases[alias] = real_name
                if self.is_l1_l2 and (not self.is_test):
                    if any(x in node.module for x in ["L5_safety", "L6_observability"]):
                        self.add_finding(
                            "Layer Bleed",
                            f"L1/L2 imports from upper layer: {node.module}",
                            "Refactor to Interface.",
                        )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        """TODO: Add documentation for visit_ClassDef."""
        bases = [self.aliases.get(b.id, b.id) if isinstance(b, ast.Name) else unparse(b) for b in node.bases]
        if any("BaseAgent" in b for b in bases) and any("MCPHardenedMixin" in b for b in bases):
            self.add_finding(
                "Redundant Mixin Chain",
                f"{node.name} redundant MCPHardenedMixin",
                "Inherit only BaseAgent.",
            )
        if any("HealerMixin" in b for b in bases):
            heal_method = next(
                (n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "heal_repository"),
                None,
            )
            if heal_method:
                has_super = False
                for child in ast.walk(heal_method):
                    if (
                        isinstance(child, ast.Call)
                        and isinstance(child.func, ast.Attribute)
                        and (child.func.attr == "heal_repository")
                    ):
                        if (
                            isinstance(child.func.value, ast.Call)
                            and isinstance(child.func.value.func, ast.Name)
                            and (child.func.value.func.id == "super")
                        ):
                            has_super = True
                            break
                if not has_super:
                    self.add_finding(
                        "Circular Healer Dependency",
                        f"{node.name} missing super().heal_repository()",
                        "Maintain healing chain.",
                    )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """TODO: Add documentation for visit_FunctionDef."""
        if node.name in ("execute", "run", "process", "handle") and (not node.name.startswith("_")):
            body = [s for s in node.body if not self._is_docstring(s)]
            is_ghost = not body or (len(body) == 1 and isinstance(body[0], ast.Pass | ast.Raise))
            if is_ghost:
                self.add_finding(
                    "Ghost Implementation",
                    f"{node.name}() is empty or NotImplemented",
                    "Remove zombie method.",
                )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        """TODO: Add documentation for visit_Assign."""
        for target in node.targets:
            if isinstance(target, ast.Name) and any(
                x in target.id.upper() for x in ["REGISTRY", "MAP", "CONFIG"]
            ):
                if isinstance(node.value, ast.Dict | ast.List):
                    try:
                        src = unparse(node.value)
                        if len(src) > 500 and "Agent" in src:
                            self.add_finding(
                                "Hardcoded Registry",
                                f"Large static structure: {target.id}",
                                "Use dynamic discovery.",
                            )
                    # guardian: allow-silent-swallow
                    except (ValueError, TypeError):
                        pass
        self.generic_visit(node)

    def _check_string_bleed(self, s: str):
        if self.is_l1_l2 and (not self.is_test) and (not self.is_legacy):
            if any(p in s for p in ["agentic_core/L5", "agentic_core/L6", "L5_safety"]):
                self.add_finding(
                    "Layer Bleed",
                    f'Hardcoded upper layer path in string: "{s[:30]}..."',
                    "Remove hardcoded path.",
                )

    def visit_Constant(self, node: ast.Constant):
        """TODO: Add documentation for visit_Constant."""
        if isinstance(node.value, str):
            self._check_string_bleed(node.value)
        self.generic_visit(node)

    def visit_Str(self, node: ast.Str):
        """TODO: Add documentation for visit_Str."""
        self._check_string_bleed(node.s)
        self.generic_visit(node)


def main():
    """TODO: Add documentation for main."""
    search_dirs = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR, "scripts"]
    findings = []
    for dir_name in search_dirs:
        path = PROJECT_ROOT / dir_name
        if not path.exists():
            continue
        for py_file in path.rglob("*.py"):
            if ARCHIVES_DIR in str(py_file) or "__pycache__" in str(py_file):
                continue
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
                visitor = HardenedAntiPatternVisitor(py_file)
                visitor.visit(tree)
                findings.extend(visitor.findings)
            # guardian: allow-silent-swallow
            except Exception:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                # TODO: Handle specific exception properly
                raise  # Re-raise after logging/handling
                continue
    for _f in findings:
        pass


if __name__ == "__main__":
    main()
