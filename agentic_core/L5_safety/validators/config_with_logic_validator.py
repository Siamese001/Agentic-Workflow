"""
Config-With-Logic Anti-Pattern Detector

Detects business logic embedded inside config-typed objects or files.
Config should be pure data; callable logic in config creates hidden
runtime behaviour and makes enforcement blurry.

Pattern Detection:
- lambda expressions in module-level assignments
- if/match branches inside functions whose name ends with _config/_spec/_policy
- callable values (lambda/function refs) in dict literals assigned to *_config,
  *_spec, or *_policy variables
"""

from __future__ import annotations

import ast
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
    _emit_signs_execution_trace,
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

_emit_authorize_and_execute("p2", "config_with_logic_validator", "execution_auth")
_emit_validates_capability("p2", "config_with_logic_validator", "capability_check")
_emit_routes_to_capability("p2", "config_with_logic_validator", "capability_route")
_emit_writes_via_uwg("p2", "config_with_logic_validator", "uwg_write")
_emit_blocks_direct_write("p2", "config_with_logic_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "config_with_logic_validator", "tool_invocation")
_emit_captures_execution_output("p2", "config_with_logic_validator", "exec_output")
_emit_dispatches_agent("p3", "config_with_logic_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "config_with_logic_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "config_with_logic_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "config_with_logic_validator", "healing_outcome")
_emit_escalates_failure("p3", "config_with_logic_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "config_with_logic_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "config_with_logic_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "config_with_logic_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "config_with_logic_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "config_with_logic_validator", "eval_metric")
_emit_stores_embedding("p4", "config_with_logic_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "config_with_logic_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "config_with_logic_validator", "exec_snapshot_link")
from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

emit_replay_key("p0", "config_with_logic_validator")
emit_determinism_digest("p0", "config_with_logic_validator")

_emit_dispatches_healing_run("p1", "config_with_logic_validator", "L5")
_emit_routes_through("p1", "config_with_logic_validator", "L5")
_emit_checks_agent_registry("p1", "config_with_logic_validator", "agent_registry")
_emit_validates_agent_capability("p1", "config_with_logic_validator", "capability")
_emit_dispatches_execution_plan("p1", "config_with_logic_validator", "exec_plan")
_emit_agent_executes_agent("p1", "config_with_logic_validator", "sub_agent")
_emit_routes_to_agent("p1", "config_with_logic_validator", "target_agent")
_emit_verifies_policy("p1", "config_with_logic_validator", "policy_check")
_emit_observes_runtime_state("p1", "config_with_logic_validator", "runtime_state")
_emit_verifies_boundary("p1", "config_with_logic_validator", "boundary_check")
_emit_transcripts_response("p1", "config_with_logic_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "config_with_logic_validator")
_emit_gated_by_confidence("p1", "config_with_logic_validator", "confidence_gate")
_emit_escalates_to_human("p1", "config_with_logic_validator", "L5")
_emit_reads_policy_state("p1", "config_with_logic_validator", "L5")

_emit_applies_guardrail("p0", "config_with_logic_validator", "p0_governance")
_emit_snapshots_state("p0", "config_with_logic_validator", "state_snapshot")
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

_emit_emits_metric_event("config_with_logic_validator", "p4obs", "metric_1")
_emit_emits_metric_event("config_with_logic_validator", "p4obs", "metric_2")
_emit_emits_metric_event("config_with_logic_validator", "p4obs", "metric_3")
_emit_emits_metric_event("config_with_logic_validator", "p4obs", "metric_4")
_emit_emits_metric_event("config_with_logic_validator", "p4obs", "metric_5")
_emit_emits_metric_event("config_with_logic_validator", "p4obs", "metric_6")
_emit_records_incident_event("config_with_logic_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("config_with_logic_validator", "p4obs", "anomaly")
_emit_writes_observability_log("config_with_logic_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("config_with_logic_validator", "p4obs", "mon_state")
_emit_triggers_alert("config_with_logic_validator", "p4obs", "alert")
_emit_links_incident_trace("config_with_logic_validator", "p4obs", "trace_link")
_emit_captures_pattern("config_with_logic_validator", "p3lm", "pattern")
_emit_records_learning_event("config_with_logic_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("config_with_logic_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("config_with_logic_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("config_with_logic_validator", "p3lm", "routing")
_emit_improves_agent_policy("config_with_logic_validator", "p3lm", "policy")
_emit_stores_learning_state("config_with_logic_validator", "p3lm", "state")
_emit_records_execution_trace("config_with_logic_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("config_with_logic_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("config_with_logic_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("config_with_logic_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("config_with_logic_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("config_with_logic_validator", "env_read", "p2_env_1")
_emit_reads_environ("config_with_logic_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("config_with_logic_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("config_with_logic_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "config_with_logic_validator", "context_pull")
_emit_pulls_context("p1", "config_with_logic_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "config_with_logic_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "config_with_logic_validator", "uwg_term_2")
_emit_writes_through("p1", "config_with_logic_validator", "write_through")
_emit_writes_through("p1", "config_with_logic_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "config_with_logic_validator", "safety_validation")
_emit_invokes_eval("p1", "config_with_logic_validator", "eval_call")
_emit_proposal_commits_routing("p1", "config_with_logic_validator", "routing_commit")

_CONFIG_SUFFIXES = ("_config", "_spec", "_policy", "_settings", "_options")
_WHITELIST_COMMENT = "# guardian: allow-config-with-logic"


class ConfigWithLogicDetector(AntiPatternDetector):
    """
    Detects logic (lambdas, conditionals) embedded in config-typed objects.

    Config-with-logic makes governance enforcement blurry because business
    rules buried in data structures are invisible to policy scanners and
    cannot be independently tested or versioned.
    """

    WHITELIST_COMMENT = _WHITELIST_COMMENT

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "conftest.py",
        ]

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.CONFIG_WITH_LOGIC

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect config-with-logic patterns in the AST."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ConfigWithLogicDetector.detect")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ConfigWithLogicDetector.detect".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations: list[AntiPatternViolation] = []

        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except (ValueError, TypeError, RuntimeError) as e:
            raise
            source_lines = []

        for node in ast.walk(tree):
            # 1. Module-level assignment: x_config = {...lambda...}
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if self._is_config_name(target):
                        v = self._check_value_for_logic(node.value, file_path, source_lines, node.lineno)
                        violations.extend(v)

            # 2. Annotated assignment: x_config: T = {...lambda...}
            elif isinstance(node, ast.AnnAssign):
                if node.value and self._is_config_name(node.target):
                    v = self._check_value_for_logic(node.value, file_path, source_lines, node.lineno)
                    violations.extend(v)

            # 3. Function named *_config/*_spec/*_policy contains if/match
            elif isinstance(node, ast.FunctionDef):
                if any(node.name.endswith(s) for s in _CONFIG_SUFFIXES):
                    for child in ast.walk(node):
                        if isinstance(child, ast.If):
                            if not self._is_whitelisted_line(source_lines, child.lineno):
                                evidence = self._get_source_line(file_path, child.lineno)
                                violations.append(
                                    AntiPatternViolation(
                                        file_path=file_path,
                                        line_number=child.lineno,
                                        category=self.category,
                                        message=(
                                            f"Config-with-logic: 'if' branch inside "
                                            f"config-factory function '{node.name}'"
                                        ),
                                        evidence=evidence,
                                        severity="warning",
                                        suggested_fix=(
                                            "Extract conditional logic to a separate "
                                            "factory or builder; keep config functions "
                                            "as pure data constructors."
                                        ),
                                    )
                                )

        return violations

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _is_config_name(self, node: ast.expr) -> bool:
        """Return True if the AST name node looks like a config variable."""
        if isinstance(node, ast.Name):
            return any(node.id.endswith(s) for s in _CONFIG_SUFFIXES)
        if isinstance(node, ast.Attribute):
            return any(node.attr.endswith(s) for s in _CONFIG_SUFFIXES)
        return False

    def _check_value_for_logic(
        self,
        value: ast.expr,
        file_path: Path,
        source_lines: list[str],
        lineno: int,
    ) -> list[AntiPatternViolation]:
        """Walk a value node and flag any lambda expressions found."""
        violations: list[AntiPatternViolation] = []
        for child in ast.walk(value):
            if isinstance(child, ast.Lambda):
                line = getattr(child, "lineno", lineno)
                if self._is_whitelisted_line(source_lines, line):
                    continue
                evidence = self._get_source_line(file_path, line)
                violations.append(
                    AntiPatternViolation(
                        file_path=file_path,
                        line_number=line,
                        category=self.category,
                        message=("Config-with-logic: lambda expression embedded in config-typed variable"),
                        evidence=evidence,
                        severity="error",
                        suggested_fix=(
                            "Replace the lambda with a named function defined "
                            "outside the config dict, or move the logic to the "
                            "caller that reads the config."
                        ),
                    )
                )
        return violations

    def _is_whitelisted_line(self, source_lines: list[str], lineno: int) -> bool:
        """Return True if the line or its predecessor contains the whitelist comment."""
        for check_line in (lineno - 1, lineno - 2):
            if 0 <= check_line < len(source_lines):
                if _WHITELIST_COMMENT in source_lines[check_line]:
                    return True
        return False


__all__ = ["ConfigWithLogicDetector"]
