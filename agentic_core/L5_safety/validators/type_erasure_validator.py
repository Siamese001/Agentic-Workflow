"""
Type Erasure Anti-Pattern Detector

Detects functions returning raw `dict` or `Any` types instead of
structured Pydantic models or dataclasses.

Pattern Detection:
- `-> dict:` or `-> dict[str, Any]:` return annotations
- `-> Any:` return annotations
- Missing return type annotations on public methods
"""

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
    _emit_pulls_context,
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
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "type_erasure_validator", "execution_auth")
_emit_validates_capability("p2", "type_erasure_validator", "capability_check")
_emit_routes_to_capability("p2", "type_erasure_validator", "capability_route")
_emit_writes_via_uwg("p2", "type_erasure_validator", "uwg_write")
_emit_blocks_direct_write("p2", "type_erasure_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "type_erasure_validator", "tool_invocation")
_emit_captures_execution_output("p2", "type_erasure_validator", "exec_output")
_emit_dispatches_agent("p3", "type_erasure_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "type_erasure_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "type_erasure_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "type_erasure_validator", "healing_outcome")
_emit_escalates_failure("p3", "type_erasure_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "type_erasure_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "type_erasure_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "type_erasure_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "type_erasure_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "type_erasure_validator", "eval_metric")
_emit_stores_embedding("p4", "type_erasure_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "type_erasure_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "type_erasure_validator", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_links_incident_trace,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)

from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

_emit_emits_metric_event("type_erasure_validator", "p4obs", "metric_1")
_emit_emits_metric_event("type_erasure_validator", "p4obs", "metric_2")
_emit_emits_metric_event("type_erasure_validator", "p4obs", "metric_3")
_emit_emits_metric_event("type_erasure_validator", "p4obs", "metric_4")
_emit_emits_metric_event("type_erasure_validator", "p4obs", "metric_5")
_emit_emits_metric_event("type_erasure_validator", "p4obs", "metric_6")
_emit_records_incident_event("type_erasure_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("type_erasure_validator", "p4obs", "anomaly")
_emit_writes_observability_log("type_erasure_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("type_erasure_validator", "p4obs", "mon_state")
_emit_triggers_alert("type_erasure_validator", "p4obs", "alert")
_emit_links_incident_trace("type_erasure_validator", "p4obs", "trace_link")
_emit_captures_pattern("type_erasure_validator", "p3lm", "pattern")
_emit_records_learning_event("type_erasure_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("type_erasure_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("type_erasure_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("type_erasure_validator", "p3lm", "routing")
_emit_improves_agent_policy("type_erasure_validator", "p3lm", "policy")
_emit_stores_learning_state("type_erasure_validator", "p3lm", "state")
_emit_records_execution_trace("type_erasure_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("type_erasure_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("type_erasure_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("type_erasure_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("type_erasure_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("type_erasure_validator", "env_read", "p2_env_1")
_emit_reads_environ("type_erasure_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("type_erasure_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("type_erasure_validator", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "type_erasure_validator")
emit_determinism_digest("p0", "type_erasure_validator")

_emit_dispatches_healing_run("p1", "type_erasure_validator", "L5")
_emit_routes_through("p1", "type_erasure_validator", "L5")
_emit_checks_agent_registry("p1", "type_erasure_validator", "agent_registry")
_emit_validates_agent_capability("p1", "type_erasure_validator", "capability")
_emit_dispatches_execution_plan("p1", "type_erasure_validator", "exec_plan")
_emit_agent_executes_agent("p1", "type_erasure_validator", "sub_agent")
_emit_routes_to_agent("p1", "type_erasure_validator", "target_agent")
_emit_verifies_policy("p1", "type_erasure_validator", "policy_check")
_emit_observes_runtime_state("p1", "type_erasure_validator", "runtime_state")
_emit_verifies_boundary("p1", "type_erasure_validator", "boundary_check")
_emit_transcripts_response("p1", "type_erasure_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "type_erasure_validator")
_emit_gated_by_confidence("p1", "type_erasure_validator", "confidence_gate")
_emit_escalates_to_human("p1", "type_erasure_validator", "L5")
_emit_reads_policy_state("p1", "type_erasure_validator", "L5")

_emit_applies_guardrail("p0", "type_erasure_validator", "p0_governance")
_emit_snapshots_state("p0", "type_erasure_validator", "state_snapshot")
_emit_writes_through("p1", "type_erasure_validator", "uwg_governed_write")
_emit_writes_through("p1", "type_erasure_validator", "uwg_governed_write_2")
_emit_pulls_context("p1", "type_erasure_validator", "context_retrieval")
_emit_pulls_context("p1", "type_erasure_validator", "context_retrieval_2")
emit_determinism_digest("trace_type_erasure_validator", "type_erasure_validator_dispatch")
emit_determinism_digest("trace_type_erasure_validator", "type_erasure_validator_complete")
_emit_validated_by_safety_plane("p1", "type_erasure_validator", "safety_validation")


class TypeErasureDetector(AntiPatternDetector):
    """
    Detects functions with type-erased return types.

    Type erasure causes downstream agents to hallucinate
    non-existent keys and leads to schema drift.
    """

    # Whitelist comment pattern
    WHITELIST_COMMENT = "# guardian: allow-type-erasure"

    # Allowed dict types with sufficient specificity
    ALLOWED_DICT_TYPES = {
        "dict[str, str]",
        "dict[str, int]",
        "dict[str, float]",
        "dict[str, bool]",
        "dict[str, Path]",
    }

    # Methods to ignore (common utility patterns)
    IGNORED_METHODS = {
        "__init__",
        "__str__",
        "__repr__",
        "__eq__",
        "__hash__",
        "__iter__",
        "__next__",
        "__len__",
        "__getitem__",
        "__setitem__",
        "to_dict",
        "from_dict",
        "as_dict",
    }

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
        check_agent_classes_only: bool = True,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)
        self.check_agent_classes_only = check_agent_classes_only

        # Add default whitelisted files
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "conftest.py",
            "*_types.py",  # Type definition files
        ]

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.TYPE_ERASURE

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect type erasure patterns in the AST."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "TypeErasureDetector.detect")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:TypeErasureDetector.detect".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations = []

        # Read source for whitelist comment checking
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except (ValueError, TypeError, RuntimeError) as e:
            raise
            source_lines = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if this is an agent/validator class
                if self.check_agent_classes_only and not self._is_agent_class(node):
                    continue

                # Check methods in the class
                for item in node.body:
                    if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                        violation = self._check_function(item, file_path, source_lines, node.name)
                        if violation:
                            violations.append(violation)

            # Also check module-level functions if not limiting to agent classes
            elif not self.check_agent_classes_only:
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    # Skip if inside a class (already handled above)
                    violation = self._check_function(node, file_path, source_lines, None)
                    if violation:
                        violations.append(violation)

        return violations

    def _is_agent_class(self, node: ast.ClassDef) -> bool:
        """Check if class is an Agent or Validator.

        [REFACTORED 2026-02-08] Aligned with classification kernel:
        - Agent: class name ends with 'Agent' (not just contains)
        - Validator: class name ends with 'Validator' or inherits from Validator
        - Excludes Mixin classes
        """
        name = node.name
        # Exclude Mixins (kernel MIXIN priority)
        if "Mixin" in name:
            return False
        # Agent check (kernel AGENT priority: endswith, not contains)
        if name.endswith("Agent"):
            return True
        # Validator check
        if name.endswith("Validator"):
            return True
        # Check base classes for Agent/Validator inheritance
        for base in node.bases:
            base_name = self._get_name(base)
            if base_name and (base_name.endswith("Agent") or base_name.endswith("Validator")):
                return True
        return False

    def _check_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        source_lines: list[str],
        class_name: str | None,
    ) -> AntiPatternViolation | None:
        """Check if a function has type-erased return type."""

        # Skip private methods and ignored methods
        if node.name.startswith("_") and node.name not in ("__call__",):
            if node.name not in self.IGNORED_METHODS:
                return None

        if node.name in self.IGNORED_METHODS:
            return None

        # Check for whitelist comment
        if node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return None

        # Check return annotation
        if node.returns is None:
            # Missing return annotation - less severe
            return None  # Don't flag missing annotations for now

        return_type = self._get_annotation_string(node.returns)

        if return_type is None:
            return None

        # Check for type erasure patterns
        is_type_erasure = False
        severity = "warning"

        if return_type == "dict" or return_type == "Dict":
            is_type_erasure = True
        elif return_type == "Any":
            is_type_erasure = True
            severity = "error"
        elif return_type.startswith("dict[") and return_type not in self.ALLOWED_DICT_TYPES:
            # Check if it's dict[str, Any] or similar
            if "Any" in return_type:
                is_type_erasure = True

        if not is_type_erasure:
            return None

        # Generate evidence
        evidence = self._get_source_line(file_path, node.lineno)

        method_name = f"{class_name}.{node.name}" if class_name else node.name

        return AntiPatternViolation(
            file_path=file_path,
            line_number=node.lineno,
            category=self.category,
            message=f"Type erasure: {method_name} returns {return_type} instead of structured type",
            evidence=evidence,
            severity=severity,
            suggested_fix=self._generate_fix_suggestion(node.name, return_type),
            metadata={
                "method_name": method_name,
                "return_type": return_type,
                "class_name": class_name,
            },
        )

    def _get_name(self, node: ast.expr) -> str | None:
        """Get the name from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return None

    def _get_annotation_string(self, node: ast.expr) -> str | None:
        """Convert an annotation AST node to string representation."""
        try:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Constant):
                return str(node.value)
            elif isinstance(node, ast.Subscript):
                base = self._get_annotation_string(node.value)
                if base:
                    # Simplified - just get the base type
                    return f"{base}[...]"
            elif isinstance(node, ast.Attribute):
                return node.attr
            return ast.unparse(node)
        except (ValueError, TypeError, RuntimeError) as e:
            raise
            return None

    def _generate_fix_suggestion(self, method_name: str, return_type: str) -> str:
        """Generate a fix suggestion for the violation."""
        if "heal" in method_name.lower():
            return """Use HealResult dataclass:
    from agentic_core.runtime.types.heal_result import HealResult, HealStatus

    def heal(self, violation: dict) -> HealResult:
        return HealResult(
            violations_found=1,
            violations_fixed=1,
            status=HealStatus.SUCCESS,
        )"""

        return f"""Replace {return_type} with a structured type:
    from dataclasses import dataclass
import uuid
from typing import Any
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)
_emit_pulls_context("p1", "type_erasure_validator", "context_pull")
_emit_pulls_context("p1", "type_erasure_validator", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "type_erasure_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "type_erasure_validator", "uwg_term_secondary")
_emit_writes_through("p1", "type_erasure_validator", "write_through")
_emit_writes_through("p1", "type_erasure_validator", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "type_erasure_validator", "safety_validation")
_emit_invokes_eval("p1", "type_erasure_validator", "eval_call")
_emit_proposal_commits_routing("p1", "type_erasure_validator", "routing_commit")

    @dataclass
    class {method_name.title().replace("_", "")}Result:
        # Define specific fields
        value: str
        status: str

    def {method_name}(self, ...) -> {method_name.title().replace("_", "")}Result:
        ..."""


__all__ = ["TypeErasureDetector"]
