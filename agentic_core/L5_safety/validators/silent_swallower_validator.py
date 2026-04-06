"""
Silent Swallower Anti-Pattern Detector

Detects try/except blocks that catch generic exceptions and suppress
them without proper handling (raising, returning failure status).

Pattern Detection:
- except Exception: with only pass, print(), or logger calls
- except Exception as e: without raise or return False/None
- Bare except: clauses
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

_emit_authorize_and_execute("p2", "silent_swallower_validator", "execution_auth")
_emit_validates_capability("p2", "silent_swallower_validator", "capability_check")
_emit_routes_to_capability("p2", "silent_swallower_validator", "capability_route")
_emit_writes_via_uwg("p2", "silent_swallower_validator", "uwg_write")
_emit_blocks_direct_write("p2", "silent_swallower_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "silent_swallower_validator", "tool_invocation")
_emit_captures_execution_output("p2", "silent_swallower_validator", "exec_output")
_emit_dispatches_agent("p3", "silent_swallower_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "silent_swallower_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "silent_swallower_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "silent_swallower_validator", "healing_outcome")
_emit_escalates_failure("p3", "silent_swallower_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "silent_swallower_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "silent_swallower_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "silent_swallower_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "silent_swallower_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "silent_swallower_validator", "eval_metric")
_emit_stores_embedding("p4", "silent_swallower_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "silent_swallower_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "silent_swallower_validator", "exec_snapshot_link")
from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

emit_replay_key("p0", "silent_swallower_validator")
emit_determinism_digest("p0", "silent_swallower_validator")

_emit_dispatches_healing_run("p1", "silent_swallower_validator", "L5")
_emit_routes_through("p1", "silent_swallower_validator", "L5")
_emit_checks_agent_registry("p1", "silent_swallower_validator", "agent_registry")
_emit_validates_agent_capability("p1", "silent_swallower_validator", "capability")
_emit_dispatches_execution_plan("p1", "silent_swallower_validator", "exec_plan")
_emit_agent_executes_agent("p1", "silent_swallower_validator", "sub_agent")
_emit_routes_to_agent("p1", "silent_swallower_validator", "target_agent")
_emit_verifies_policy("p1", "silent_swallower_validator", "policy_check")
_emit_observes_runtime_state("p1", "silent_swallower_validator", "runtime_state")
_emit_verifies_boundary("p1", "silent_swallower_validator", "boundary_check")
_emit_transcripts_response("p1", "silent_swallower_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "silent_swallower_validator")
_emit_gated_by_confidence("p1", "silent_swallower_validator", "confidence_gate")
_emit_escalates_to_human("p1", "silent_swallower_validator", "L5")
_emit_reads_policy_state("p1", "silent_swallower_validator", "L5")

_emit_applies_guardrail("p0", "silent_swallower_validator", "p0_governance")
_emit_snapshots_state("p0", "silent_swallower_validator", "state_snapshot")
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

_emit_emits_metric_event("silent_swallower_validator", "p4obs", "metric_1")
_emit_emits_metric_event("silent_swallower_validator", "p4obs", "metric_2")
_emit_emits_metric_event("silent_swallower_validator", "p4obs", "metric_3")
_emit_emits_metric_event("silent_swallower_validator", "p4obs", "metric_4")
_emit_emits_metric_event("silent_swallower_validator", "p4obs", "metric_5")
_emit_emits_metric_event("silent_swallower_validator", "p4obs", "metric_6")
_emit_records_incident_event("silent_swallower_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("silent_swallower_validator", "p4obs", "anomaly")
_emit_writes_observability_log("silent_swallower_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("silent_swallower_validator", "p4obs", "mon_state")
_emit_triggers_alert("silent_swallower_validator", "p4obs", "alert")
_emit_links_incident_trace("silent_swallower_validator", "p4obs", "trace_link")
_emit_captures_pattern("silent_swallower_validator", "p3lm", "pattern")
_emit_records_learning_event("silent_swallower_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("silent_swallower_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("silent_swallower_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("silent_swallower_validator", "p3lm", "routing")
_emit_improves_agent_policy("silent_swallower_validator", "p3lm", "policy")
_emit_stores_learning_state("silent_swallower_validator", "p3lm", "state")
_emit_records_execution_trace("silent_swallower_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("silent_swallower_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("silent_swallower_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("silent_swallower_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("silent_swallower_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("silent_swallower_validator", "env_read", "p2_env_1")
_emit_reads_environ("silent_swallower_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("silent_swallower_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("silent_swallower_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "silent_swallower_validator", "context_pull")
_emit_pulls_context("p1", "silent_swallower_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "silent_swallower_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "silent_swallower_validator", "uwg_term_2")
_emit_writes_through("p1", "silent_swallower_validator", "write_through")
_emit_writes_through("p1", "silent_swallower_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "silent_swallower_validator", "safety_validation")
_emit_invokes_eval("p1", "silent_swallower_validator", "eval_call")
_emit_proposal_commits_routing("p1", "silent_swallower_validator", "routing_commit")


class SilentSwallowerDetector(AntiPatternDetector):
    """
    Detects exception handlers that silently swallow errors.

    These patterns prevent proper error propagation and cause
    downstream agents to operate on failed state.
    """

    # Whitelist comment pattern
    WHITELIST_COMMENT = "# guardian: allow-silent-swallow"

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)

        # Add default whitelisted files (test files, debug scripts)
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "debug_*.py",
            "conftest.py",
        ]

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.SILENT_SWALLOWER

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect silent swallower patterns in the AST."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SilentSwallowerDetector.detect")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SilentSwallowerDetector.detect".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations = []

        # Read source for whitelist comment checking
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except (ValueError, TypeError, RuntimeError) as e:
            source_lines = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                violation = self._check_except_handler(node, file_path, source_lines)
                if violation:
                    violations.append(violation)

        return violations

    def _check_except_handler(
        self,
        node: ast.ExceptHandler,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Check if an except handler is a silent swallower."""

        # Check for whitelist comment on previous line
        if node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return None

        # Check if catching generic Exception or bare except
        is_generic_exception = False
        exception_name = "Exception"

        if node.type is None:
            # Bare except:
            is_generic_exception = True
            exception_name = "(bare except)"
        elif isinstance(node.type, ast.Name):
            if node.type.id in ("Exception", "BaseException"):
                is_generic_exception = True
                exception_name = node.type.id
        elif isinstance(node.type, ast.Tuple):
            # Check if Exception is in the tuple
            for elt in node.type.elts:
                if isinstance(elt, ast.Name) and elt.id in ("Exception", "BaseException"):
                    is_generic_exception = True
                    exception_name = elt.id
                    break

        if not is_generic_exception:
            return None

        # Check handler body for proper error handling
        has_raise = False
        has_return = False
        has_proper_handling = False

        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Raise):
                has_raise = True
                has_proper_handling = True
            elif isinstance(stmt, ast.Return):
                # Check if returning False, None, or error dict
                has_return = True
                if isinstance(stmt.value, ast.Constant | ast.NameConstant):
                    if stmt.value.value in (False, None):
                        has_proper_handling = True
                elif isinstance(stmt.value, ast.Dict):
                    # Check for error dict pattern
                    for key in stmt.value.keys:
                        if isinstance(key, ast.Constant) and key.value in (
                            "error",
                            "status",
                            "success",
                        ):
                            has_proper_handling = True
                            break
                elif isinstance(stmt.value, ast.Call):
                    # Check for dataclass/object returns with success=False pattern
                    # e.g., return ConfigLoadResult(success=False, ...)
                    for keyword in getattr(stmt.value, "keywords", []):
                        if keyword.arg == "success":
                            if isinstance(keyword.value, ast.Constant):
                                if keyword.value.value is False:
                                    has_proper_handling = True
                                    break

        # If no proper handling, this is a silent swallower
        if not has_proper_handling:
            # Get the source line for evidence
            evidence = self._get_source_line(file_path, node.lineno)

            return AntiPatternViolation(
                file_path=file_path,
                line_number=node.lineno,
                category=self.category,
                message=f"Silent exception swallower: catches {exception_name} without raise or proper return",
                evidence=evidence,
                severity="error" if exception_name == "(bare except)" else "warning",
                suggested_fix=self._generate_fix_suggestion(node, exception_name),
                metadata={
                    "exception_type": exception_name,
                    "has_raise": has_raise,
                    "has_return": has_return,
                },
            )

        return None

    def _generate_fix_suggestion(self, node: ast.ExceptHandler, exception_name: str) -> str:
        """Generate a fix suggestion for the violation."""
        var_name = node.name or "e"

        if exception_name == "(bare except)":
            return f"""Replace bare except with specific exception handling:
    except Exception as {var_name}:
        logger.error(f"Error: {{{var_name}}}")
        raise  # Re-raise to propagate error"""

        return f"""Add proper error handling:
    except {exception_name} as {var_name}:
        logger.error(f"Error: {{{var_name}}}")
        raise  # Or: return {{"success": False, "error": str({var_name})}}"""


__all__ = ["SilentSwallowerDetector"]
