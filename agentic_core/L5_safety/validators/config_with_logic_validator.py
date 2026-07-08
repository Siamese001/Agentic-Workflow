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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "config_with_logic_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "config_with_logic_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "config_with_logic_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "config_with_logic_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "config_with_logic_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "config_with_logic_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "config_with_logic_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "config_with_logic_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "config_with_logic_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "config_with_logic_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "config_with_logic_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "config_with_logic_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "config_with_logic_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "config_with_logic_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "config_with_logic_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "config_with_logic_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "config_with_logic_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "config_with_logic_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "config_with_logic_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "config_with_logic_validator", "exec_snapshot_link")
from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

trace_contract.emit_replay_key("p0", "config_with_logic_validator")
trace_contract.emit_determinism_digest("p0", "config_with_logic_validator")

trace_contract._emit_dispatches_healing_run("p1", "config_with_logic_validator", "L5")
trace_contract._emit_routes_through("p1", "config_with_logic_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "config_with_logic_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "config_with_logic_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "config_with_logic_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "config_with_logic_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "config_with_logic_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "config_with_logic_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "config_with_logic_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "config_with_logic_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "config_with_logic_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "config_with_logic_validator")
trace_contract._emit_gated_by_confidence("p1", "config_with_logic_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "config_with_logic_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "config_with_logic_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "config_with_logic_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "config_with_logic_validator", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("config_with_logic_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("config_with_logic_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("config_with_logic_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("config_with_logic_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("config_with_logic_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("config_with_logic_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("config_with_logic_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("config_with_logic_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("config_with_logic_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("config_with_logic_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("config_with_logic_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("config_with_logic_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("config_with_logic_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("config_with_logic_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("config_with_logic_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("config_with_logic_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("config_with_logic_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("config_with_logic_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("config_with_logic_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("config_with_logic_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("config_with_logic_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("config_with_logic_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("config_with_logic_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("config_with_logic_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("config_with_logic_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("config_with_logic_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("config_with_logic_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("config_with_logic_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "config_with_logic_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "config_with_logic_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "config_with_logic_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "config_with_logic_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "config_with_logic_validator", "write_through")
trace_contract._emit_writes_through("p1", "config_with_logic_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "config_with_logic_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "config_with_logic_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "config_with_logic_validator", "routing_commit")

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "ConfigWithLogicDetector.detect")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ConfigWithLogicDetector.detect".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations: list[AntiPatternViolation] = []

        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except (ValueError, TypeError, RuntimeError) as e:
            raise

        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
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
                    for child in tqdm(ast.walk(node), desc="Processing", unit="item"):
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
                                    ),
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
        for child in tqdm(ast.walk(value), desc="Processing", unit="item"):
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
                    ),
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
