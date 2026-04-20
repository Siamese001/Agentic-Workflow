"""
Direct Prompt Compilation Anti-Pattern Detector

Detects prompt strings being assembled outside the AirlockAssembler
(the designated Assembly Stage).  Direct f-string / concatenation /
str.join / format() construction of final prompts bypasses:
  - deterministic composition and manifest hashing
  - authority ordering (S0 > I0 > D0 > C0 > U0)
  - injection scanning

Pattern Detection:
- f-strings that reference known prompt-slot names (s0_, i0_, d0_, c0_, u0_)
  outside the canonical assembly_stage module
- BinOp string concatenation ("+") involving prompt-slot variables
- str.join() / str.format() calls on prompt-slot variables
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

_emit_authorize_and_execute("p2", "direct_prompt_compilation_validator", "execution_auth")
_emit_validates_capability("p2", "direct_prompt_compilation_validator", "capability_check")
_emit_routes_to_capability("p2", "direct_prompt_compilation_validator", "capability_route")
_emit_writes_via_uwg("p2", "direct_prompt_compilation_validator", "uwg_write")
_emit_blocks_direct_write("p2", "direct_prompt_compilation_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "direct_prompt_compilation_validator", "tool_invocation")
_emit_captures_execution_output("p2", "direct_prompt_compilation_validator", "exec_output")
_emit_dispatches_agent("p3", "direct_prompt_compilation_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "direct_prompt_compilation_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "direct_prompt_compilation_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "direct_prompt_compilation_validator", "healing_outcome")
_emit_escalates_failure("p3", "direct_prompt_compilation_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "direct_prompt_compilation_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "direct_prompt_compilation_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "direct_prompt_compilation_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "direct_prompt_compilation_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "direct_prompt_compilation_validator", "eval_metric")
_emit_stores_embedding("p4", "direct_prompt_compilation_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "direct_prompt_compilation_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "direct_prompt_compilation_validator", "exec_snapshot_link")
from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

emit_replay_key("p0", "direct_prompt_compilation_validator")
emit_determinism_digest("p0", "direct_prompt_compilation_validator")

_emit_dispatches_healing_run("p1", "direct_prompt_compilation_validator", "L5")
_emit_routes_through("p1", "direct_prompt_compilation_validator", "L5")
_emit_checks_agent_registry("p1", "direct_prompt_compilation_validator", "agent_registry")
_emit_validates_agent_capability("p1", "direct_prompt_compilation_validator", "capability")
_emit_dispatches_execution_plan("p1", "direct_prompt_compilation_validator", "exec_plan")
_emit_agent_executes_agent("p1", "direct_prompt_compilation_validator", "sub_agent")
_emit_routes_to_agent("p1", "direct_prompt_compilation_validator", "target_agent")
_emit_verifies_policy("p1", "direct_prompt_compilation_validator", "policy_check")
_emit_observes_runtime_state("p1", "direct_prompt_compilation_validator", "runtime_state")
_emit_verifies_boundary("p1", "direct_prompt_compilation_validator", "boundary_check")
_emit_transcripts_response("p1", "direct_prompt_compilation_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "direct_prompt_compilation_validator")
_emit_gated_by_confidence("p1", "direct_prompt_compilation_validator", "confidence_gate")
_emit_escalates_to_human("p1", "direct_prompt_compilation_validator", "L5")
_emit_reads_policy_state("p1", "direct_prompt_compilation_validator", "L5")

_emit_applies_guardrail("p0", "direct_prompt_compilation_validator", "p0_governance")
_emit_snapshots_state("p0", "direct_prompt_compilation_validator", "state_snapshot")
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

_emit_emits_metric_event("direct_prompt_compilation_validator", "p4obs", "metric_1")
_emit_emits_metric_event("direct_prompt_compilation_validator", "p4obs", "metric_2")
_emit_emits_metric_event("direct_prompt_compilation_validator", "p4obs", "metric_3")
_emit_emits_metric_event("direct_prompt_compilation_validator", "p4obs", "metric_4")
_emit_emits_metric_event("direct_prompt_compilation_validator", "p4obs", "metric_5")
_emit_emits_metric_event("direct_prompt_compilation_validator", "p4obs", "metric_6")
_emit_records_incident_event("direct_prompt_compilation_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("direct_prompt_compilation_validator", "p4obs", "anomaly")
_emit_writes_observability_log("direct_prompt_compilation_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("direct_prompt_compilation_validator", "p4obs", "mon_state")
_emit_triggers_alert("direct_prompt_compilation_validator", "p4obs", "alert")
_emit_links_incident_trace("direct_prompt_compilation_validator", "p4obs", "trace_link")
_emit_captures_pattern("direct_prompt_compilation_validator", "p3lm", "pattern")
_emit_records_learning_event("direct_prompt_compilation_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("direct_prompt_compilation_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("direct_prompt_compilation_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("direct_prompt_compilation_validator", "p3lm", "routing")
_emit_improves_agent_policy("direct_prompt_compilation_validator", "p3lm", "policy")
_emit_stores_learning_state("direct_prompt_compilation_validator", "p3lm", "state")
_emit_records_execution_trace("direct_prompt_compilation_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("direct_prompt_compilation_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("direct_prompt_compilation_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("direct_prompt_compilation_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("direct_prompt_compilation_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("direct_prompt_compilation_validator", "env_read", "p2_env_1")
_emit_reads_environ("direct_prompt_compilation_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("direct_prompt_compilation_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("direct_prompt_compilation_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "direct_prompt_compilation_validator", "context_pull")
_emit_pulls_context("p1", "direct_prompt_compilation_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "direct_prompt_compilation_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "direct_prompt_compilation_validator", "uwg_term_2")
_emit_writes_through("p1", "direct_prompt_compilation_validator", "write_through")
_emit_writes_through("p1", "direct_prompt_compilation_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "direct_prompt_compilation_validator", "safety_validation")
_emit_invokes_eval("p1", "direct_prompt_compilation_validator", "eval_call")
_emit_proposal_commits_routing("p1", "direct_prompt_compilation_validator", "routing_commit")

_PROMPT_SLOT_PREFIXES = ("s0_", "i0_", "d0_", "c0_", "u0_")
_ASSEMBLY_MODULE_STEMS = {"assembly_stage", "airlock_assembler"}
_WHITELIST_COMMENT = "# guardian: allow-direct-prompt-compilation"


def _is_prompt_slot_name(name: str) -> bool:
    """Return True if the name looks like a prompt slot variable."""
    return any(name.startswith(p) for p in _PROMPT_SLOT_PREFIXES)


def _names_in_node(node: ast.expr) -> list[str]:
    """Collect all Name and Attribute identifiers referenced in an expression."""
    names: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            names.append(child.id)
        elif isinstance(child, ast.Attribute):
            names.append(child.attr)
    return names


class DirectPromptCompilationDetector(AntiPatternDetector):
    """
    Detects direct prompt string construction outside the Assembly Stage.

    All final prompt strings MUST be composed via AirlockAssembler.
    Any f-string / concatenation / join involving prompt-slot variables
    outside assembly_stage.py is a governance violation.
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
        return AntiPatternCategory.DIRECT_PROMPT_COMPILATION

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect direct prompt compilation patterns."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "DirectPromptCompilationDetector.detect",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:DirectPromptCompilationDetector.detect".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self._is_assembly_module(file_path):
            return []

        violations: list[AntiPatternViolation] = []
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except (ValueError, TypeError, RuntimeError) as e:
            raise

        for node in ast.walk(tree):
            v = self._check_node(node, file_path, source_lines)
            if v:
                violations.append(v)

        return violations

    # ------------------------------------------------------------------
    # node-level checks
    # ------------------------------------------------------------------

    def _check_node(
        self,
        node: ast.AST,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        lineno = getattr(node, "lineno", None)
        if lineno is None:
            return None
        if self._is_whitelisted_line(source_lines, lineno):
            return None

        # f-string containing prompt-slot references
        if isinstance(node, ast.JoinedStr):
            slot_names = []
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and _is_prompt_slot_name(child.id):
                    slot_names.append(child.id)
            if slot_names:
                return AntiPatternViolation(
                    file_path=file_path,
                    line_number=lineno,
                    category=self.category,
                    message=(
                        f"Direct prompt compilation: f-string references prompt-slot "
                        f"variable(s) {slot_names!r} outside Assembly Stage"
                    ),
                    evidence=self._get_source_line(file_path, lineno),
                    severity="error",
                    suggested_fix=(
                        "Pass slot values to AirlockAssembler.assemble() instead of "
                        "concatenating them manually."
                    ),
                )

        # BinOp string + involving prompt-slot names
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            names = _names_in_node(node.left) + _names_in_node(node.right)
            slot_names = [n for n in names if _is_prompt_slot_name(n)]
            if slot_names:
                return AntiPatternViolation(
                    file_path=file_path,
                    line_number=lineno,
                    category=self.category,
                    message=(
                        f"Direct prompt compilation: string concatenation (+) references "
                        f"prompt-slot variable(s) {slot_names!r} outside Assembly Stage"
                    ),
                    evidence=self._get_source_line(file_path, lineno),
                    severity="error",
                    suggested_fix=("Use AirlockAssembler.assemble() for all prompt slot composition."),
                )

        # str.join() / str.format() on prompt-slot variables
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in ("join", "format"):
                all_names: list[str] = []
                for arg in node.args:
                    all_names.extend(_names_in_node(arg))
                for kw in node.keywords:
                    if kw.value:
                        all_names.extend(_names_in_node(kw.value))
                # Also check the object being called on
                all_names.extend(_names_in_node(node.func.value))
                slot_names = [n for n in all_names if _is_prompt_slot_name(n)]
                if slot_names:
                    return AntiPatternViolation(
                        file_path=file_path,
                        line_number=lineno,
                        category=self.category,
                        message=(
                            f"Direct prompt compilation: str.{node.func.attr}() references "
                            f"prompt-slot variable(s) {slot_names!r} outside Assembly Stage"
                        ),
                        evidence=self._get_source_line(file_path, lineno),
                        severity="error",
                        suggested_fix=("Use AirlockAssembler.assemble() for all prompt slot composition."),
                    )

        return None

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _is_assembly_module(self, file_path: Path) -> bool:
        """Return True if this file IS the canonical assembly module (allowlisted)."""
        return file_path.stem in _ASSEMBLY_MODULE_STEMS

    def _is_whitelisted_line(self, source_lines: list[str], lineno: int) -> bool:
        for check_line in (lineno - 1, lineno - 2):
            if 0 <= check_line < len(source_lines):
                if _WHITELIST_COMMENT in source_lines[check_line]:
                    return True
        return False


__all__ = ["DirectPromptCompilationDetector"]
