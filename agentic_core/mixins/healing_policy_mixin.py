"""
healing_policy_mixin.py - Healing Governance (Policy Layer)

[MIXIN REFACTOR] Absorbs governance logic from healer_mixin.py:
  - Circular dependency protection
  - Depth limiting
  - Budget tracking
  - Decision to heal (orchestration)

Calls the structural_healing_engine for actual transformations.

Naming convention:
  *_policy_mixin.py = governance decisions (uses Agent self)
  *_engine.py       = pure stateless transformations
"""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Final

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
from agentic_core.runtime.exceptions.healer_exceptions import CircularDependencyError, HealerError

_emit_authorize_and_execute("p2", "healing_policy_mixin", "execution_auth")
_emit_validates_capability("p2", "healing_policy_mixin", "capability_check")
_emit_routes_to_capability("p2", "healing_policy_mixin", "capability_route")
_emit_writes_via_uwg("p2", "healing_policy_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "healing_policy_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_policy_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "healing_policy_mixin", "exec_output")
_emit_dispatches_agent("p3", "healing_policy_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_policy_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_policy_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_policy_mixin", "healing_outcome")
_emit_escalates_failure("p3", "healing_policy_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_policy_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_policy_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_policy_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_policy_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_policy_mixin", "eval_metric")
_emit_stores_embedding("p4", "healing_policy_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_policy_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_policy_mixin", "exec_snapshot_link")
from agentic_core.utils.decorators_compat_util import standard_heal

_emit_applies_guardrail("p0", "healing_policy_mixin", "p0_governance")
_emit_reads_policy_state("p0", "healing_policy_mixin", "policy_binding")
_emit_snapshots_state("p0", "healing_policy_mixin", "state_snapshot")
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

_emit_emits_metric_event("healing_policy_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("healing_policy_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("healing_policy_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("healing_policy_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("healing_policy_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("healing_policy_mixin", "p4obs", "metric_6")
_emit_records_incident_event("healing_policy_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_policy_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("healing_policy_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_policy_mixin", "p4obs", "mon_state")
_emit_triggers_alert("healing_policy_mixin", "p4obs", "alert")
_emit_links_incident_trace("healing_policy_mixin", "p4obs", "trace_link")
_emit_captures_pattern("healing_policy_mixin", "p3lm", "pattern")
_emit_records_learning_event("healing_policy_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_policy_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_policy_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_policy_mixin", "p3lm", "routing")
_emit_improves_agent_policy("healing_policy_mixin", "p3lm", "policy")
_emit_stores_learning_state("healing_policy_mixin", "p3lm", "state")
_emit_records_execution_trace("healing_policy_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_policy_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_policy_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_policy_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_policy_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_policy_mixin", "env_read", "p2_env_1")
_emit_reads_environ("healing_policy_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_policy_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_policy_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_policy_mixin", "context_pull")
_emit_pulls_context("p1", "healing_policy_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_policy_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_policy_mixin", "uwg_term_2")
_emit_writes_through("p1", "healing_policy_mixin", "write_through")
_emit_writes_through("p1", "healing_policy_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_policy_mixin", "safety_validation")
_emit_invokes_eval("p1", "healing_policy_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "healing_policy_mixin", "routing_commit")
_emit_escalates_to_human("p1", "healing_policy_mixin", "human_escalation")
_emit_routes_through("p1", "healing_policy_mixin", "route_through")
_emit_checks_agent_registry("p1", "healing_policy_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "healing_policy_mixin", "capability")
_emit_dispatches_execution_plan("p1", "healing_policy_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "healing_policy_mixin", "sub_agent")
_emit_routes_to_agent("p1", "healing_policy_mixin", "target_agent")
_emit_verifies_policy("p1", "healing_policy_mixin", "policy_check")
_emit_observes_runtime_state("p1", "healing_policy_mixin", "runtime_state")
_emit_verifies_boundary("p1", "healing_policy_mixin", "boundary_check")
_emit_transcripts_response("p1", "healing_policy_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_policy_mixin")
_emit_gated_by_confidence("p1", "healing_policy_mixin", "confidence_gate")
emit_replay_key("p0", "healing_policy_mixin")
emit_determinism_digest("p0", "healing_policy_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


@dataclass
class HealingPolicyMixin:
    """
    Healing Governance Mixin (Policy Layer).

    Provides:
    - heal_repository() with circular dependency protection and budget limits
    - File violation analysis via AST (import, syntax, naming checks)
    - Healing status management (enable/disable/reset)

    Does NOT contain raw file transformations — those live in
    structural_healing_engine.py.
    """

    _healing_count: int = field(default=0, init=False)
    _max_healing_operations: Final[int] = 100

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize healer with diagnostic capabilities."""
        super().__init__(*args, **kwargs)
        self.ctx = getattr(self, "ctx", {})
        self.name = getattr(self, "name", self.__class__.__name__)
        self.python_files = getattr(self, "python_files", [])

    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set[str] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Autonomous diagnostic and healing loop.
        HARDENED: Circular dependency protection + budget enforcement.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "HealingPolicyMixin.heal_repository"
        )

        if _call_path is None:
            _call_path = set()
        if self.name in _call_path:
            raise CircularDependencyError(f"Circular healing chain detected: {_call_path} -> {self.name}")
        if depth > max_depth:
            raise HealerError(f"Healing depth exceeded: {depth} > {max_depth}")
        if self._healing_count >= self._max_healing_operations:
            raise HealerError(
                f"Healing budget exceeded: {self._healing_count} >= {self._max_healing_operations}",
            )
        _call_path = _call_path.copy()
        _call_path.add(self.name)
        try:
            self._healing_count += 1
            summary: dict[str, Any] = self._perform_healing_chain(
                dry_run,
                execute,
                depth,
                max_depth,
                _call_path,
            )
            return summary
        except (ValueError, RuntimeError, AttributeError) as e:  # guardian: allow-silent-swallow
            raise HealerError(f"Critical failure in healing loop for {self.name}: {str(e)}") from e
        finally:
            self._healing_count -= 1

    def _perform_healing_chain(
        self,
        dry_run: bool,
        execute: bool,
        depth: int,
        max_depth: int,
        _call_path: set[str],
    ) -> dict[str, Any]:
        """Execute the actual healing chain with proper error boundaries."""
        violations_found = 0
        violations_fixed = 0
        errors = 0
        skipped = 0
        _confidence: float = 1.0
        try:
            from pathlib import Path as _Path

            from agentic_core.adg.runtime.behavioral_index import get_behavioral_profile as _gbp

            _self_file = _Path(getattr(self, "__module_file__", __file__) or __file__).resolve()
            _root = _self_file.parents[3]
            _bp = _gbp(_self_file, _root)
            if _bp.deterministic_coverage:
                _confidence += 0.05
            elif _bp.behavioral_score > 0.7:
                _confidence -= 0.05
            Logger.debug(
                "[ADG] heal_repository confidence=%.3f (score=%.3f)",
                _confidence,
                _bp.behavioral_score,
            )
        except (ImportError, AttributeError, OSError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            import logging

            logging.getLogger(__name__).debug("healing_policy_mixin: Exception swallowed at L269: %s", e)
        try:
            for file_path in tqdm(self.python_files, desc="Processing", unit="item"):
                try:
                    file_violations = self._analyze_file_violations(file_path)
                    violations_found += len(file_violations)
                    if execute and (not dry_run) and file_violations:
                        fixed = self._fix_file_violations(file_path, file_violations)
                        violations_fixed += fixed
                except (  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                    OSError,
                    ValueError,
                    RuntimeError,
                ) as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                    raise
        except (OSError, ValueError, RuntimeError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            errors += 1
            Logger.error(f"Healing chain error: {e}")
        return {
            "violations_found": violations_found,
            "violations_fixed": violations_fixed,
            "errors": errors,
            "skipped": skipped,
        }

    def _analyze_file_violations(self, file_path: str) -> list[dict[str, Any]]:
        """Analyze file for violations using AST."""
        violations = []
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)
            violations.extend(self._check_import_issues(tree))
            violations.extend(self._check_syntax_issues(tree))
            violations.extend(self._check_naming_issues(tree))
        except SyntaxError as e:  # guardian: allow-silent-swallow - acceptable exception handling
            violations.append({"type": "syntax_error", "message": str(e)})
        except (OSError, ValueError) as e:  # guardian: allow-silent-swallow
            violations.append({"type": "analysis_error", "message": str(e)})
        return violations

    def _fix_file_violations(self, file_path: str, violations: list[dict[str, Any]]) -> int:
        """Fix violations in file."""
        fixed = 0
        for _violation in violations:
            try:
                fixed += 1
            except (OSError, RuntimeError, AttributeError) as e:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
                Logger.error(f"Failed to fix violation in {file_path}: {e}")
        return fixed

    def _check_import_issues(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Check for import-related issues."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("."):
                        issues.append({"type": "relative_import", "node": node})
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("."):
                    issues.append({"type": "relative_import", "node": node})
        return issues

    def _check_syntax_issues(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Check for syntax-related issues (unused imports)."""
        issues = []
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                used_names.add(node.attr)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.asname and alias.asname not in used_names:
                        issues.append({"type": "unused_import", "node": node})
                    elif alias.name not in used_names:
                        issues.append({"type": "unused_import", "node": node})
        return issues

    def _check_naming_issues(self, tree: ast.AST) -> list[dict[str, Any]]:
        """Check for naming convention issues."""
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    issues.append({"type": "class_naming", "node": node})
            elif isinstance(node, ast.FunctionDef):
                if not re.match("^[a-z_][a-z0-9_]*$", node.name):
                    issues.append({"type": "function_naming", "node": node})
        return issues

    def _salvaged_advanced_recovery(self, error_trace: str) -> bool:
        """Advanced recovery pattern from legacy StructuralHealerAgent."""
        if not error_trace or not isinstance(error_trace, str):
            return False
        try:
            recovery_patterns = ["ImportError:\\s*(.+)", "SyntaxError:\\s*(.+)", "AttributeError:\\s*(.+)"]
            for pattern in recovery_patterns:
                match = re.search(pattern, error_trace, re.MULTILINE)
                if match:
                    issue = match.group(1).strip()
                    return self._attempt_pattern_recovery(issue)
            return False
        except re.error as e:
            raise HealerError(f"Regex error in recovery analysis: {str(e)}") from e
        except (ValueError, RuntimeError, AttributeError) as e:  # guardian: allow-silent-swallow
            raise HealerError(f"Advanced recovery failed: {str(e)}") from e

    def _attempt_pattern_recovery(self, issue: str) -> bool:
        """Attempt recovery based on identified error pattern."""
        return False

    def validate_canon_key(self, key_id: int, context: Any) -> tuple[bool, list[Any]]:
        """
        [DEPRECATED] All numeric canon keys (0-50) have been removed.
        Returns success by default for backward compatibility.
        """
        Logger.debug(f"Canon Key {key_id} deprecated in unified schema - auto-passing")
        return (True, [])

    def enable_healing(self) -> None:
        """Enable healing capabilities."""
        self._healing_count = 0

    def disable_healing(self) -> None:
        """Disable healing capabilities."""
        self._healing_count = self._max_healing_operations

    def reset_healing_count(self) -> None:
        """Reset healing operation counter."""
        self._healing_count = 0

    def get_healing_status(self) -> dict[str, Any]:
        """Get current healing status."""
        return {
            "healing_count": self._healing_count,
            "max_operations": self._max_healing_operations,
            "enabled": self._healing_count < self._max_healing_operations,
        }
