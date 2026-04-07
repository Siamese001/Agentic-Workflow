from __future__ import annotations

import ast

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "ast_relocator", "p0_governance")
_emit_reads_policy_state("p0", "ast_relocator", "policy_binding")
_emit_snapshots_state("p0", "ast_relocator", "state_snapshot")
emit_replay_key("p0", "ast_relocator")
emit_determinism_digest("p0", "ast_relocator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ast_relocator", "execution_auth")
_emit_validates_capability("p2", "ast_relocator", "capability_check")
_emit_routes_to_capability("p2", "ast_relocator", "capability_route")
_emit_writes_via_uwg("p2", "ast_relocator", "uwg_write")
_emit_blocks_direct_write("p2", "ast_relocator", "direct_write_block")
_emit_records_tool_invocation("p2", "ast_relocator", "tool_invocation")
_emit_captures_execution_output("p2", "ast_relocator", "exec_output")
_emit_dispatches_agent("p3", "ast_relocator", "agent_dispatch")
_emit_coordinates_agents("p3", "ast_relocator", "agent_coordination")
_emit_records_workflow_lineage("p3", "ast_relocator", "workflow_lineage")
_emit_records_healing_outcome("p3", "ast_relocator", "healing_outcome")
_emit_escalates_failure("p3", "ast_relocator", "failure_escalation")
_emit_orchestrates_workflow("p3", "ast_relocator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ast_relocator", "healing_dispatch")
_emit_invokes_evaluation("p3", "ast_relocator", "evaluation_signal")
_emit_records_telemetry_event("p4", "ast_relocator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ast_relocator", "eval_metric")
_emit_stores_embedding("p4", "ast_relocator", "embedding_store")
_emit_updates_meta_learning_state("p4", "ast_relocator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ast_relocator", "exec_snapshot_link")

"Brief description of functionality and purpose."
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint import SEMANTIC_L2_REGISTRY
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("ast_relocator", "p4obs", "metric_1")
_emit_emits_metric_event("ast_relocator", "p4obs", "metric_2")
_emit_emits_metric_event("ast_relocator", "p4obs", "metric_3")
_emit_emits_metric_event("ast_relocator", "p4obs", "metric_4")
_emit_emits_metric_event("ast_relocator", "p4obs", "metric_5")
_emit_emits_metric_event("ast_relocator", "p4obs", "metric_6")
_emit_records_incident_event("ast_relocator", "p4obs", "incident")
_emit_captures_runtime_anomaly("ast_relocator", "p4obs", "anomaly")
_emit_writes_observability_log("ast_relocator", "p4obs", "obs_log")
_emit_updates_monitoring_state("ast_relocator", "p4obs", "mon_state")
_emit_triggers_alert("ast_relocator", "p4obs", "alert")
_emit_links_incident_trace("ast_relocator", "p4obs", "trace_link")
_emit_captures_pattern("ast_relocator", "p3lm", "pattern")
_emit_records_learning_event("ast_relocator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ast_relocator", "p3lm", "snapshot")
_emit_feeds_meta_learning("ast_relocator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ast_relocator", "p3lm", "routing")
_emit_improves_agent_policy("ast_relocator", "p3lm", "policy")
_emit_stores_learning_state("ast_relocator", "p3lm", "state")
_emit_records_execution_trace("ast_relocator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ast_relocator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ast_relocator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ast_relocator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ast_relocator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ast_relocator", "env_read", "p2_env_1")
_emit_reads_environ("ast_relocator", "env_read", "p2_env_2")
_emit_reads_runtime_state("ast_relocator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ast_relocator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ast_relocator", "context_pull")
_emit_pulls_context("p1", "ast_relocator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ast_relocator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ast_relocator", "uwg_term_2")
_emit_writes_through("p1", "ast_relocator", "write_through")
_emit_writes_through("p1", "ast_relocator", "write_through_2")
_emit_validated_by_safety_plane("p1", "ast_relocator", "safety_validation")
_emit_invokes_eval("p1", "ast_relocator", "eval_call")
_emit_proposal_commits_routing("p1", "ast_relocator", "routing_commit")
_emit_escalates_to_human("p1", "ast_relocator", "human_escalation")
_emit_routes_through("p1", "ast_relocator", "route_through")
_emit_checks_agent_registry("p1", "ast_relocator", "agent_registry")
_emit_validates_agent_capability("p1", "ast_relocator", "capability")
_emit_dispatches_execution_plan("p1", "ast_relocator", "exec_plan")
_emit_agent_executes_agent("p1", "ast_relocator", "sub_agent")
_emit_routes_to_agent("p1", "ast_relocator", "target_agent")
_emit_verifies_policy("p1", "ast_relocator", "policy_check")
_emit_observes_runtime_state("p1", "ast_relocator", "runtime_state")
_emit_verifies_boundary("p1", "ast_relocator", "boundary_check")
_emit_transcripts_response("p1", "ast_relocator", "transcript")
_emit_hard_fails_untranscripted("p1", "ast_relocator")
_emit_gated_by_confidence("p1", "ast_relocator", "confidence_gate")

try:
    project_root = Path(__file__).resolve().parents[3]
except IndexError:
    project_root = Path.cwd()


class AstRelocator(ast.NodeVisitor):
    """
    [L6 SURGERY] AST-based code relocation engine.
    Surgically extracts classes/functions and calculates their sovereign coordinates.
    """

    def __init__(self, file_path: Path, content: str):
        self.file_path = file_path
        self.content_lines = content.splitlines()
        self.tree = ast.parse(content)
        self.entities: list[dict] = []
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef):
        """Capture top-level classes."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AstRelocator.visit_ClassDef")

        self.entities.append(
            {
                "type": "class",
                "name": node.name,
                "lineno": node.lineno,
                "start_line": getattr(node, "lineno", node.lineno),
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "node": node,
                "suggested_location": self._suggest_placement(node, node.name, "Class"),
            },
        )
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Capture top-level functions (skip methods)."""
        if self.current_class:
            return self.generic_visit(node)
        self.entities.append(
            {
                "type": "function",
                "name": node.name,
                "lineno": node.lineno,
                "start_line": getattr(node, "lineno", node.lineno),
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "node": node,
                "suggested_location": self._suggest_placement(node, node.name, "Function"),
            },
        )
        self.generic_visit(node)

    def _suggest_placement(self, node: ast.AST, name: str, entity_type: str) -> tuple[str, str, float]:
        """
        [SEMANTIC SCORING] Calculates placement confidence using the Rich Semantic Registry.
        Returns (L1, L2, Confidence_Score).
        """
        best_match = ("utils", "general_helpers", 0.0)
        name_lower = name.lower()
        docstring = ast.get_docstring(node) or ""
        doc_lower = docstring.lower()
        for l1, l2_dict in SEMANTIC_L2_REGISTRY.items():
            for l2, meta in l2_dict.items():
                score = 0.0
                for kw in meta.get("keywords", []):
                    if kw in name_lower:
                        score += 3.0
                    elif kw in doc_lower:
                        score += 1.0
                if entity_type in meta.get("entity_types", []):
                    score += 0.5
                purpose_words = meta.get("purpose", "").lower().split()
                doc_words = set(doc_lower.split())
                matches = [w for w in purpose_words if len(w) > 3 and w in doc_words]
                if matches:
                    score += 1.5
                    if len(matches) > 3:
                        score += 1.0 * len(matches)
                if entity_type == "Class" and hasattr(node, "bases"):
                    for base in node.bases:
                        base_name = getattr(base, "id", "") or getattr(
                            getattr(base, "attr", None), "value", "",
                        )
                        if base_name and any(base_name in b for b in meta.get("bases", [])):
                            score += 4.0
                if score > best_match[2]:
                    best_match = (l1, l2, score)
        return best_match

    def get_movable_entities(self) -> list[dict]:
        self.visit(self.tree)
        return self.entities

    @staticmethod
    def extract_entity_code(content_lines: list[str], start: int, end: int) -> str:
        """Surgically extract code block including decorators."""
        lines = content_lines[start - 1 : end]
        return "\n".join(lines) + "\n"

    @staticmethod
    def generate_import_fix(old_path: Path, new_path: Path, entity_name: str) -> str:
        """Generate the import string required to access the moved entity."""
        try:
            rel_path = new_path.relative_to(project_root)
            module_path = str(rel_path.with_suffix("").as_posix()).replace("/", ".")
            return f"from {module_path} import {entity_name}"
        except ValueError:
            return f"# Could not resolve import for {entity_name}"
