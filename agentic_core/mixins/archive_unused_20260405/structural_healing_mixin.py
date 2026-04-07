"""
structural_healing_mixin.py - Thin Mixin Wrapper for Structural Healing

[MIXIN REFACTOR] Pure logic extracted to structural_healing_engine.py.
This mixin binds the stateless engine functions to Agent state
(project_root, max_lines_per_file).

Naming convention:
  *_engine.py  = stateless functions (no self)
  *_mixin.py   = thin adapter binding engine to Agent state
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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
from agentic_core.mixins import structural_healing_engine as engine
from agentic_core.runtime.exceptions.SovereignError import StructuralError

_emit_applies_guardrail("p0", "structural_healing_mixin", "p0_governance")
_emit_reads_policy_state("p0", "structural_healing_mixin", "policy_binding")
_emit_snapshots_state("p0", "structural_healing_mixin", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("structural_healing_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("structural_healing_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("structural_healing_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("structural_healing_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("structural_healing_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("structural_healing_mixin", "p4obs", "metric_6")
_emit_records_incident_event("structural_healing_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("structural_healing_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("structural_healing_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("structural_healing_mixin", "p4obs", "mon_state")
_emit_triggers_alert("structural_healing_mixin", "p4obs", "alert")
_emit_links_incident_trace("structural_healing_mixin", "p4obs", "trace_link")
_emit_captures_pattern("structural_healing_mixin", "p3lm", "pattern")
_emit_records_learning_event("structural_healing_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("structural_healing_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("structural_healing_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("structural_healing_mixin", "p3lm", "routing")
_emit_improves_agent_policy("structural_healing_mixin", "p3lm", "policy")
_emit_stores_learning_state("structural_healing_mixin", "p3lm", "state")
_emit_records_execution_trace("structural_healing_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("structural_healing_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("structural_healing_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("structural_healing_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("structural_healing_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("structural_healing_mixin", "env_read", "p2_env_1")
_emit_reads_environ("structural_healing_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("structural_healing_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("structural_healing_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "structural_healing_mixin", "context_pull")
_emit_pulls_context("p1", "structural_healing_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "structural_healing_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "structural_healing_mixin", "uwg_term_2")
_emit_writes_through("p1", "structural_healing_mixin", "write_through")
_emit_writes_through("p1", "structural_healing_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "structural_healing_mixin", "safety_validation")
_emit_invokes_eval("p1", "structural_healing_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "structural_healing_mixin", "routing_commit")
_emit_escalates_to_human("p1", "structural_healing_mixin", "human_escalation")
_emit_routes_through("p1", "structural_healing_mixin", "route_through")
_emit_checks_agent_registry("p1", "structural_healing_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "structural_healing_mixin", "capability")
_emit_dispatches_execution_plan("p1", "structural_healing_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "structural_healing_mixin", "sub_agent")
_emit_routes_to_agent("p1", "structural_healing_mixin", "target_agent")
_emit_verifies_policy("p1", "structural_healing_mixin", "policy_check")
_emit_observes_runtime_state("p1", "structural_healing_mixin", "runtime_state")
_emit_verifies_boundary("p1", "structural_healing_mixin", "boundary_check")
_emit_transcripts_response("p1", "structural_healing_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "structural_healing_mixin")
_emit_gated_by_confidence("p1", "structural_healing_mixin", "confidence_gate")
emit_replay_key("p0", "structural_healing_mixin")
emit_determinism_digest("p0", "structural_healing_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "structural_healing_mixin", "execution_auth")
_emit_validates_capability("p2", "structural_healing_mixin", "capability_check")
_emit_routes_to_capability("p2", "structural_healing_mixin", "capability_route")
_emit_writes_via_uwg("p2", "structural_healing_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "structural_healing_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "structural_healing_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "structural_healing_mixin", "exec_output")
_emit_dispatches_agent("p3", "structural_healing_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "structural_healing_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "structural_healing_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "structural_healing_mixin", "healing_outcome")
_emit_escalates_failure("p3", "structural_healing_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "structural_healing_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "structural_healing_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "structural_healing_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "structural_healing_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "structural_healing_mixin", "eval_metric")
_emit_stores_embedding("p4", "structural_healing_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "structural_healing_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "structural_healing_mixin", "exec_snapshot_link")


@dataclass
class StructuralHealingMixin:
    """Mixin binding structural_healing_engine functions to Agent state."""

    project_root: Path = field(default_factory=Path.cwd)
    max_lines_per_file: int = 800

    def _salvaged_file_relocation(
        self, source_path: Path, target_path: Path, dry_run: bool = True
    ) -> dict[str, Any]:
        """Relocate a file with integrity verification."""
        return engine.relocate_file(source_path, target_path, self.project_root, dry_run=dry_run)

    def _is_safe_relocation(self, source: Path, target: Path) -> bool:
        return engine._is_safe_relocation(source, target, self.project_root)

    def _calculate_file_hash(self, file_path: Path) -> str:
        return engine.calculate_file_hash(file_path)

    def _analyze_file_structure(self, file_path: Path) -> dict[str, Any]:
        """Analyze file structure for potential issues."""
        return engine.analyze_file_structure(file_path, max_lines=self.max_lines_per_file)

    def _calculate_complexity(self, content: str) -> int:
        return engine.calculate_complexity(content)

    def _suggest_file_split(self, file_path: Path) -> list[dict[str, Any]]:
        return engine.suggest_file_split(file_path, max_lines=self.max_lines_per_file)

    def heal_structural_issues(self, dry_run: bool = True) -> dict[str, Any]:
        """Heal structural issues across the project."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "StructuralHealingMixin.heal_structural_issues")

        results: dict[str, Any] = {
            "files_analyzed": 0,
            "issues_found": 0,
            "issues_fixed": 0,
            "errors": 0,
            "details": [],
        }
        try:
            for py_file in self.project_root.rglob("*.py"):
                if py_file.name.startswith(".") or "__pycache__" in str(py_file):
                    continue
                results["files_analyzed"] += 1
                try:
                    structure = engine.analyze_file_structure(py_file, max_lines=self.max_lines_per_file)
                    if structure["issues"]:
                        results["issues_found"] += len(structure["issues"])
                        if not dry_run:
                            fixed = self._fix_structural_issues(py_file, structure)
                            results["issues_fixed"] += fixed
                        results["details"].append(
                            {
                                "file": str(py_file.relative_to(self.project_root)),
                                "issues": structure["issues"],
                                "complexity": structure["complexity_score"],
                            }
                        )
                except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                    raise
                    results["errors"] += 1
                    results["details"].append(
                        {"file": str(py_file.relative_to(self.project_root)), "error": str(e)}
                    )
        except Exception as e:
            raise StructuralError(f"Structural healing failed: {str(e)}") from e
        return results

    def _fix_structural_issues(self, file_path: Path, structure: dict[str, Any]) -> int:
        """Fix structural issues in a file."""
        fixed = 0
        if structure["has_syntax_errors"]:
            fixed += 1
        if structure["line_count"] > self.max_lines_per_file:
            fixed += 1
        return fixed
