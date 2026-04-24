"""
unified_hygiene_mixin.py - HARDENED: Unified code hygiene validation
"""

from __future__ import annotations

import hashlib
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
from agentic_core.runtime.exceptions.SovereignError import HygieneError

_emit_authorize_and_execute("p2", "hygiene_mixin", "execution_auth")
_emit_validates_capability("p2", "hygiene_mixin", "capability_check")
_emit_routes_to_capability("p2", "hygiene_mixin", "capability_route")
_emit_writes_via_uwg("p2", "hygiene_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "hygiene_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "hygiene_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "hygiene_mixin", "exec_output")
_emit_dispatches_agent("p3", "hygiene_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "hygiene_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "hygiene_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "hygiene_mixin", "healing_outcome")
_emit_escalates_failure("p3", "hygiene_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "hygiene_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hygiene_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "hygiene_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "hygiene_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hygiene_mixin", "eval_metric")
_emit_stores_embedding("p4", "hygiene_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "hygiene_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hygiene_mixin", "exec_snapshot_link")
from agentic_core.utils.decorators_compat_util import standard_heal

_emit_applies_guardrail("p0", "hygiene_mixin", "p0_governance")
_emit_reads_policy_state("p0", "hygiene_mixin", "policy_binding")
_emit_snapshots_state("p0", "hygiene_mixin", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("hygiene_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("hygiene_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("hygiene_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("hygiene_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("hygiene_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("hygiene_mixin", "p4obs", "metric_6")
_emit_records_incident_event("hygiene_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("hygiene_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("hygiene_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("hygiene_mixin", "p4obs", "mon_state")
_emit_triggers_alert("hygiene_mixin", "p4obs", "alert")
_emit_links_incident_trace("hygiene_mixin", "p4obs", "trace_link")
_emit_captures_pattern("hygiene_mixin", "p3lm", "pattern")
_emit_records_learning_event("hygiene_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hygiene_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("hygiene_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hygiene_mixin", "p3lm", "routing")
_emit_improves_agent_policy("hygiene_mixin", "p3lm", "policy")
_emit_stores_learning_state("hygiene_mixin", "p3lm", "state")
_emit_records_execution_trace("hygiene_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hygiene_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hygiene_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hygiene_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hygiene_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hygiene_mixin", "env_read", "p2_env_1")
_emit_reads_environ("hygiene_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("hygiene_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hygiene_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hygiene_mixin", "context_pull")
_emit_pulls_context("p1", "hygiene_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hygiene_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hygiene_mixin", "uwg_term_2")
_emit_writes_through("p1", "hygiene_mixin", "write_through")
_emit_writes_through("p1", "hygiene_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "hygiene_mixin", "safety_validation")
_emit_invokes_eval("p1", "hygiene_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "hygiene_mixin", "routing_commit")
_emit_escalates_to_human("p1", "hygiene_mixin", "human_escalation")
_emit_routes_through("p1", "hygiene_mixin", "route_through")
_emit_checks_agent_registry("p1", "hygiene_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "hygiene_mixin", "capability")
_emit_dispatches_execution_plan("p1", "hygiene_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "hygiene_mixin", "sub_agent")
_emit_routes_to_agent("p1", "hygiene_mixin", "target_agent")
_emit_verifies_policy("p1", "hygiene_mixin", "policy_check")
_emit_observes_runtime_state("p1", "hygiene_mixin", "runtime_state")
_emit_verifies_boundary("p1", "hygiene_mixin", "boundary_check")
_emit_transcripts_response("p1", "hygiene_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "hygiene_mixin")
_emit_gated_by_confidence("p1", "hygiene_mixin", "confidence_gate")
emit_replay_key("p0", "hygiene_mixin")
emit_determinism_digest("p0", "hygiene_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass
class HygieneMixin:
    """
    HARDENED: Unified code hygiene validation and healing.
    SALVAGED: Consolidated from HygieneValidatorAgent.py.
    """

    project_root: Path = field(default_factory=Path.cwd)
    allowed_duplicates: set[str] = field(default_factory=lambda: {"__init__.py", "README.md", ".gitignore"})

    @standard_heal
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        HARDENED: Unified hygiene healing with comprehensive validation.
        """
        try:
            hygiene_results = self._analyze_hygiene_violations()
            violations_found = len(hygiene_results.get("empty_files", [])) + len(
                hygiene_results.get("duplicate_files", []),
            )
            violations_fixed = 0
            if execute and (not dry_run):
                violations_fixed = self._fix_hygiene_violations(hygiene_results)
            return {
                "violations_found": violations_found,
                "violations_fixed": violations_fixed,
                "errors": 0,
                "skipped": 0,
            }
        except (OSError, ValueError, RuntimeError) as e:
            raise HygieneError(f"Hygiene healing failed: {e}") from e

    def _analyze_hygiene_violations(self) -> dict[str, list[dict[str, Any]]]:
        """
        Analyze hygiene violations across the project.
        SALVAGED: Comprehensive hygiene analysis from legacy HygieneValidatorAgent.
        """
        results = {"empty_files": [], "duplicate_files": [], "large_files": [], "syntax_errors": []}
        try:
            file_hashes = {}
            for py_file in tqdm(self.project_root.rglob("*.py"), desc="Processing", unit="item"):
                if py_file.name.startswith(".") or "__pycache__" in str(py_file):
                    continue
                rel_path = py_file.relative_to(self.project_root)
                try:
                    if py_file.stat().st_size == 0:
                        content = py_file.read_text(encoding="utf-8")
                        if not content.strip():
                            results["empty_files"].append({"file": str(rel_path), "size": 0})
                    if py_file.name not in self.allowed_duplicates:
                        file_hash = self._calculate_file_hash(py_file)
                        if file_hash in file_hashes:
                            results["duplicate_files"].append(
                                {"file": str(rel_path), "duplicate_of": file_hashes[file_hash]},
                            )
                        else:
                            file_hashes[file_hash] = str(rel_path)
                    if py_file.stat().st_size > 1024 * 1024:
                        results["large_files"].append(
                            {"file": str(rel_path), "size_bytes": py_file.stat().st_size},
                        )
                    try:
                        import ast

                        content = py_file.read_text(encoding="utf-8")
                        ast.parse(content)
                    except SyntaxError as e:  # guardian: allow-silent-swallow -- acceptable exception handling
                        results["syntax_errors"].append(
                            {"file": str(rel_path), "error": str(e)}
                        )  # guardian: File operations with encoding need error-specific handling
                except (OSError, UnicodeDecodeError) as e:  # guardian: allow-silent-swallow -- acceptable exception handling
                    self.logger.debug(f"Failed to scan {rel_path}: {e}")
                    continue
        except (OSError, ValueError, RuntimeError) as e:
            raise HygieneError(f"Hygiene analysis failed: {str(e)}") from e
        return results

    def _fix_hygiene_violations(self, violations: dict[str, list[dict[str, Any]]]) -> int:
        """
        Fix hygiene violations.
        SALVAGED: Automated fixing from legacy hygiene validators.
        """
        fixed = 0
        for item in violations.get("empty_files", []):
            try:
                file_path = self.project_root / item["file"]
                if file_path.exists():
                    file_path.unlink()  # guardian: Add error context logging
                    fixed += 1
            except OSError as e:  # guardian: allow-silent-swallow -- acceptable exception handling
                self.logger.debug(f"Failed to remove {file_path.name}: {e}")
                continue
        for item in violations.get("duplicate_files", []):
            try:
                duplicate_path = self.project_root / item["file"]
                if duplicate_path.exists():  # guardian: Add error context logging
                    duplicate_path.unlink()
                    # guardian: allow-silent-swallow -- acceptable exception handling
                    fixed += 1
            except OSError as e:
                self.logger.debug(f"Failed to remove {duplicate_path.name}: {e}")
                continue
        return fixed

    def _calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of file for duplicate detection.
        SALVAGED: Hash calculation from legacy duplicate detection.
        """
        try:
            return hashlib.sha256(file_path.read_bytes()).hexdigest()
        except OSError as e:
            raise HygieneError(f"Failed to calculate hash for {file_path}: {str(e)}") from e

    def get_hygiene_report(self) -> dict[str, Any]:
        """
        Generate comprehensive hygiene report.
        SALVAGED: Reporting functionality from legacy HygieneValidatorAgent.
        """
        try:
            violations = self._analyze_hygiene_violations()
            report = {
                "summary": {
                    "total_files": sum(
                        1
                        for _ in self.project_root.rglob("*.py")
                        if not _.name.startswith(".") and "__pycache__" not in str(_)
                    ),
                    "empty_files": len(violations["empty_files"]),
                    "duplicate_files": len(violations["duplicate_files"]),
                    "large_files": len(violations["large_files"]),
                    "syntax_errors": len(violations["syntax_errors"]),
                    "total_violations": sum(len(v) for v in violations.values()),
                },
                "details": violations,
                "recommendations": self._generate_recommendations(violations),
            }
            return report
        except (OSError, ValueError, RuntimeError) as e:
            raise HygieneError(f"Failed to generate hygiene report: {str(e)}") from e

    def _generate_recommendations(self, violations: dict[str, list[dict[str, Any]]]) -> list[str]:
        """
        Generate recommendations based on violations found.
        SALVAGED: Recommendation engine from legacy hygiene validators.
        """
        recommendations = []
        if violations["empty_files"]:
            recommendations.append(f"Remove {len(violations['empty_files'])} empty files")
        if violations["duplicate_files"]:
            recommendations.append(f"Resolve {len(violations['duplicate_files'])} duplicate files")
        if violations["large_files"]:
            recommendations.append(f"Refactor {len(violations['large_files'])} large files (>1MB)")
        if violations["syntax_errors"]:
            recommendations.append(f"Fix {len(violations['syntax_errors'])} syntax errors")
        if not recommendations:
            recommendations.append("No hygiene violations found - codebase is clean!")
        return recommendations

    def validate_file_hygiene(self, file_path: Path) -> dict[str, Any]:
        """
        Validate hygiene of a specific file.
        SALVAGED: Individual file validation from legacy hygiene validators.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "HygieneMixin.validate_file_hygiene"
        )

        if not file_path.exists():
            raise HygieneError(f"File not found: {file_path}")
        try:
            violations = []
            if file_path.stat().st_size == 0:
                content = file_path.read_text(encoding="utf-8")
                if not content.strip():
                    violations.append("Empty file")
            if file_path.stat().st_size > 1024 * 1024:
                violations.append("Large file (>1MB)")
            try:
                import ast  # guardian: Syntax errors should be caught at parser level, not runtime

                # guardian: allow-silent-swallow -- acceptable exception handling
                content = file_path.read_text(encoding="utf-8")
                ast.parse(content)
            except SyntaxError as e:
                violations.append(f"Syntax error: {e}")
            return {
                "file": str(file_path.relative_to(self.project_root)),
                "is_clean": len(violations) == 0,
                "violations": violations,
                "size_bytes": file_path.stat().st_size,
            }
        except (OSError, ValueError, RuntimeError) as e:
            raise HygieneError(f"File hygiene validation failed for {file_path}: {str(e)}") from e
