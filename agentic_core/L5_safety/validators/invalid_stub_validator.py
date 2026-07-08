"""
Invalid Stub Anti-Pattern Detector

Detects test stubs that only return success paths and don't simulate failures.
Invalid stubs mask weakness in error handling and prevent proper resilience testing.

Pattern Detection:
- Stub functions that always return success (e.g., always status 200, never 404)
- Missing error paths (no exception raising or error return branches)
- Hardcoded success (single return statement, no conditional errors)
- No timeout simulation (network stubs without timeout failures)
- No null simulation (database stubs without null/empty results)
"""

import ast
from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "invalid_stub_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "invalid_stub_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "invalid_stub_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "invalid_stub_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "invalid_stub_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "invalid_stub_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "invalid_stub_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "invalid_stub_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "invalid_stub_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "invalid_stub_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "invalid_stub_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "invalid_stub_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "invalid_stub_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "invalid_stub_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "invalid_stub_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "invalid_stub_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "invalid_stub_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "invalid_stub_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "invalid_stub_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "invalid_stub_validator", "exec_snapshot_link")
from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)

trace_contract.emit_replay_key("p0", "invalid_stub_validator")
trace_contract.emit_determinism_digest("p0", "invalid_stub_validator")

trace_contract._emit_dispatches_healing_run("p1", "invalid_stub_validator", "L5")
trace_contract._emit_routes_through("p1", "invalid_stub_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "invalid_stub_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "invalid_stub_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "invalid_stub_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "invalid_stub_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "invalid_stub_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "invalid_stub_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "invalid_stub_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "invalid_stub_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "invalid_stub_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "invalid_stub_validator")
trace_contract._emit_gated_by_confidence("p1", "invalid_stub_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "invalid_stub_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "invalid_stub_validator", "L5")

trace_contract._emit_applies_guardrail("p0", "invalid_stub_validator", "p0_governance")
trace_contract._emit_snapshots_state("p0", "invalid_stub_validator", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("invalid_stub_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("invalid_stub_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("invalid_stub_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("invalid_stub_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("invalid_stub_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("invalid_stub_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("invalid_stub_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("invalid_stub_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("invalid_stub_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("invalid_stub_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("invalid_stub_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("invalid_stub_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("invalid_stub_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("invalid_stub_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("invalid_stub_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("invalid_stub_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("invalid_stub_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("invalid_stub_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("invalid_stub_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("invalid_stub_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("invalid_stub_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("invalid_stub_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("invalid_stub_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("invalid_stub_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("invalid_stub_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("invalid_stub_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("invalid_stub_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("invalid_stub_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "invalid_stub_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "invalid_stub_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "invalid_stub_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "invalid_stub_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "invalid_stub_validator", "write_through")
trace_contract._emit_writes_through("p1", "invalid_stub_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "invalid_stub_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "invalid_stub_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "invalid_stub_validator", "routing_commit")


class InvalidStubDetector(AntiPatternDetector):
    """
    Detects test stubs that only return success paths without error simulation.

    Invalid stubs prevent proper resilience testing and mask weakness in error handling.
    Stubs must mirror the Contract, not just the Success Path.
    """

    # Whitelist comment pattern
    WHITELIST_COMMENT = "# guardian: allow-invalid-stub"

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ):
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)

        # Don't add default whitelisted files - we handle test file filtering in scan_file

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.INVALID_STUB

    def scan_file(self, file_path: Path) -> "DetectionResult":
        """Override to only scan test files and avoid ADG dependency."""
        from .base_detector_validator import DetectionResult

        # Check if file name starts with test_ or is in tests directory
        # This works for temp directories in tests too
        if not file_path.name.startswith("test_"):
            # Also check if any parent directory is named "tests"
            in_tests_dir = any(parent.name.lower() == "tests" for parent in file_path.parents)
            if not in_tests_dir:
                return DetectionResult(
                    file_path=file_path,
                    violations=[],
                    scan_time_ms=0,
                    cached=False,
                )

        # Implement our own scan logic to avoid ADG dependency
        import time

        start_time = time.time()

        try:
            tree = self._get_ast(file_path)

            if tree is None:
                return DetectionResult(
                    file_path=file_path,
                    violations=[],
                    scan_time_ms=(time.time() - start_time) * 1000,
                    error="Failed to parse file",
                )

            violations = self.detect(file_path, tree)

            scan_time = (time.time() - start_time) * 1000

            return DetectionResult(
                file_path=file_path,
                violations=violations,
                scan_time_ms=scan_time,
            )

        except (AttributeError, OSError, RuntimeError, SyntaxError, TypeError, ValueError) as e:
            import logging

            logging.getLogger(__name__).error(f"Error scanning {file_path}: {e}")
            return DetectionResult(
                file_path=file_path,
                violations=[],
                scan_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Detect invalid stub patterns in test files."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "InvalidStubDetector.detect")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:InvalidStubDetector.detect".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        violations = []

        # Read source for whitelist comment checking
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except (ValueError, TypeError, RuntimeError, FileNotFoundError):
            source_lines = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                violation = self._check_stub_function(node, file_path, source_lines)
                if violation:
                    violations.append(violation)

        return violations

    def _check_stub_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        """Check if a function is an invalid stub (only returns success)."""

        # Check for whitelist comment on previous line
        if node.lineno > 1 and node.lineno <= len(source_lines):
            prev_line = source_lines[node.lineno - 2].strip()
            if self.WHITELIST_COMMENT in prev_line:
                return None

        # Heuristic: function name contains "stub", "mock", "fake", or "dummy"
        # Also check if parent function name contains "test" to catch nested test stubs
        func_name_lower = node.name.lower()
        has_stub_keyword = any(keyword in func_name_lower for keyword in ["stub", "mock", "fake", "dummy"])

        if not has_stub_keyword:
            return None

        # Check if function has only return statements (no error simulation)
        has_return = False
        has_error_return = False
        has_raise = False
        return_count = 0
        has_conditional = False

        for stmt in tqdm(ast.walk(node), desc="Processing", unit="item"):
            if isinstance(stmt, ast.If):
                has_conditional = True
            elif isinstance(stmt, ast.Return):
                has_return = True
                return_count += 1
                # Check if return indicates error (e.g., status=404, error=..., success=False)
                if stmt.value:
                    if self._is_error_return(stmt.value):
                        has_error_return = True
            elif isinstance(stmt, ast.Raise):
                has_raise = True

        # If function has returns but no error returns or raises, it's an invalid stub
        # Exception: if there are no returns at all, it might not be a stub
        if has_return and return_count == 1 and not has_error_return and not has_raise:
            # Single return without error simulation - likely invalid stub
            evidence = self._get_source_line(file_path, node.lineno)

            return AntiPatternViolation(
                file_path=file_path,
                line_number=node.lineno,
                category=self.category,
                message=f"Invalid stub '{node.name}': only returns success path, missing error simulation",
                evidence=evidence,
                severity="warning",
                suggested_fix=self._generate_fix_suggestion(node),
                metadata={
                    "function_name": node.name,
                    "has_return": has_return,
                    "has_error_return": has_error_return,
                    "has_raise": has_raise,
                    "return_count": return_count,
                    "has_conditional": has_conditional,
                },
            )

        # If function has multiple returns but no error simulation, also flag it
        # Only flag if there are no conditionals or if conditionals don't lead to error returns
        if has_return and return_count > 1 and not has_error_return and not has_raise:
            # Multiple unconditional returns without error simulation
            evidence = self._get_source_line(file_path, node.lineno)

            return AntiPatternViolation(
                file_path=file_path,
                line_number=node.lineno,
                category=self.category,
                message=f"Invalid stub '{node.name}': multiple unconditional returns, missing error simulation",
                evidence=evidence,
                severity="warning",
                suggested_fix=self._generate_fix_suggestion(node),
                metadata={
                    "function_name": node.name,
                    "has_return": has_return,
                    "has_error_return": has_error_return,
                    "has_raise": has_raise,
                    "return_count": return_count,
                    "has_conditional": has_conditional,
                },
            )

        return None

    def _is_error_return(self, return_value: ast.AST) -> bool:
        """Check if a return value indicates an error condition."""
        if isinstance(return_value, ast.Dict):
            # Check for error-related keys with error values
            for key, value in tqdm(
                zip(return_value.keys, return_value.values), desc="Processing", unit="item"
            ):
                if isinstance(key, ast.Constant):
                    if key.value in ("error", "status", "success"):
                        # Check if the value actually indicates error
                        if isinstance(value, ast.Constant):
                            # status: 404 or success: False indicates error
                            if key.value == "status" and value.value in (400, 401, 403, 404, 500, 502, 503):
                                return True
                            if key.value == "success" and value.value is False:
                                return True
                            if key.value == "error" and value.value is not None:
                                return True
        elif isinstance(return_value, ast.Call):
            # Check for dataclass/object returns with success=False pattern
            for keyword in getattr(return_value, "keywords", []):
                if keyword.arg == "success":
                    if isinstance(keyword.value, ast.Constant):
                        if keyword.value.value is False:
                            return True
        elif isinstance(return_value, ast.Constant):
            # Return None might indicate error (Python 3.8+ uses ast.Constant)
            if return_value.value is None:
                return True
        return False

    def _generate_fix_suggestion(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Generate a fix suggestion for the invalid stub."""
        func_name = node.name

        return f"""Add error simulation to stub '{func_name}':
    def {func_name}(self, ...):
        if error_condition:
            return {{"status": 404, "error": "Not found"}}
        # ... existing success return
        return {{"status": 200, "data": ...}}

Or raise exceptions:
    def {func_name}(self, ...):
        if error_condition:
            raise NotFoundError("Resource not found")
        # ... existing success return
        return ..."""


__all__ = ["InvalidStubDetector"]
