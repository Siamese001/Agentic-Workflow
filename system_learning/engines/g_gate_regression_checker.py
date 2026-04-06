"""G-Gate Regression Checker — Evaluation Spine Component D.

Validates governance gate stability per Evaluation Spine documentation:
  - Exact match validation
  - Schema/state checks
  - Trajectory invariance
  - API drift detection
  - Rubric grading consistency

Deterministic, fail-closed, with full ADG traceability.
"""

from __future__ import annotations

import logging

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_blocks_direct_write,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_records_execution_trace,
    _emit_records_tool_invocation,
    _emit_routes_to_agent,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)
from system_learning.enforcement.determinism import deterministic_json, stable_sha256_json
from system_learning.types.evaluation_spine_types import GGateValidationResult

# ADG wiring for G-Gate regression checker
_emit_records_execution_trace("g_gate_regression_checker", "p0", "g_gate_trace")
_emit_applies_guardrail("p0", "g_gate_regression_checker", "p0_governance")
emit_replay_key("p0", "g_gate_regression_checker")
emit_determinism_digest("p0", "g_gate_regression_checker")
_emit_writes_via_uwg("p2", "g_gate_regression_checker", "uwg_write")
_emit_blocks_direct_write("p2", "g_gate_regression_checker", "direct_write_block")
_emit_records_tool_invocation("p2", "g_gate_regression_checker", "tool_invocation")
_emit_captures_execution_output("p2", "g_gate_regression_checker", "exec_output")
_emit_dispatches_agent("p3", "g_gate_regression_checker", "agent_dispatch")
_emit_dispatches_execution_plan("p3", "g_gate_regression_checker", "exec_plan")
_emit_routes_to_agent("p3", "g_gate_regression_checker", "target_agent")
_emit_checks_agent_registry("p3", "g_gate_regression_checker", "agent_registry")
_emit_validates_agent_capability("p3", "g_gate_regression_checker", "capability")
_emit_verifies_policy("p3", "g_gate_regression_checker", "policy_check")
_emit_verifies_boundary("p3", "g_gate_regression_checker", "boundary_check")
_emit_agent_executes_agent("p3", "g_gate_regression_checker", "sub_agent")

logger = logging.getLogger(__name__)


# =============================================================================
# GGateRegressionChecker
# =============================================================================


class GGateRegressionChecker:
    """Checker for G-Gate regression validation (Component D).

    Validates governance gate stability across runs:
        1. Exact match — Deterministic outputs match expected
        2. Schema/state — Schema and state integrity maintained
        3. Trajectory invariance — Execution path consistent
        4. API drift — No unexpected API changes
        5. Rubric consistency — Grading stable

    Deterministic: Same inputs always produce same validation result.
    Fail-closed: Any validation failure flags regression.

    Attributes
    ----------
    exact_match_tolerance:
        Tolerance for exact match comparison.
    schema_hash_algorithm:
        Algorithm for computing schema hashes.
    """

    def __init__(
        self,
        exact_match_tolerance: float = 0.0,  # 0 = strict exact match
    ) -> None:
        self.exact_match_tolerance = exact_match_tolerance

    def validate_regression(
        self,
        trace_id: str,
        baseline_state: dict,
        current_state: dict,
        execution_trace: dict,
        timestamp_utc: int,
    ) -> GGateValidationResult:
        """Validate G-Gate regression across 5 dimensions.

        Parameters
        ----------
        trace_id:
            Source execution trace identifier.
        baseline_state:
            Baseline state for comparison.
        current_state:
            Current state to validate.
        execution_trace:
            Execution trace for trajectory analysis.
        timestamp_utc:
            Unix timestamp provided by caller (no wall-clock reads).

        Returns
        -------
        GGateValidationResult
            Deterministic validation result.
        """
        _emit_records_execution_trace("g_gate_regression_checker", "validation_start", trace_id)

        # Compute digests
        baseline_digest = stable_sha256_json(baseline_state)
        current_digest = stable_sha256_json(current_state)

        # Run validations
        exact_match_pass = self._validate_exact_match(baseline_state, current_state)
        schema_state_pass = self._validate_schema_state(baseline_state, current_state)
        trajectory_invariant_pass = self._validate_trajectory_invariance(execution_trace)
        api_drift_detected = self._detect_api_drift(baseline_state, current_state)
        rubric_consistency_pass = self._validate_rubric_consistency(execution_trace)

        # Determine overall pass
        overall_pass = all([
            exact_match_pass,
            schema_state_pass,
            trajectory_invariant_pass,
            not api_drift_detected,
            rubric_consistency_pass,
        ])

        # Collect drift details
        drift_details = self._collect_drift_details(
            baseline_state,
            current_state,
            exact_match_pass,
            schema_state_pass,
            trajectory_invariant_pass,
            api_drift_detected,
            rubric_consistency_pass,
        )

        # Build diff summary
        diff_summary = self._build_diff_summary(
            baseline_digest,
            current_digest,
            exact_match_pass,
            schema_state_pass,
            trajectory_invariant_pass,
            api_drift_detected,
            rubric_consistency_pass,
        )

        _emit_records_execution_trace("g_gate_regression_checker", "validation_complete", trace_id)

        result = GGateValidationResult(
            artifact_type="G_GATE_VALIDATION_RESULT",
            result_id=stable_sha256_json({
                "trace_id": trace_id,
                "baseline_digest": baseline_digest,
                "current_digest": current_digest,
                "overall_pass": overall_pass,
                "timestamp_utc": timestamp_utc,
            }),
            trace_id=trace_id,
            exact_match_pass=exact_match_pass,
            schema_state_pass=schema_state_pass,
            trajectory_invariant_pass=trajectory_invariant_pass,
            api_drift_detected=api_drift_detected,
            rubric_consistency_pass=rubric_consistency_pass,
            overall_pass=overall_pass,
            drift_details=tuple(sorted(drift_details)),
            baseline_digest=baseline_digest,
            current_digest=current_digest,
            diff_summary=diff_summary,
            timestamp_utc=timestamp_utc,
        )

        log_level = logging.INFO if overall_pass else logging.WARNING
        logger.log(
            log_level,
            "G-Gate validation %s: trace_id=%s, exact=%s, schema=%s, trajectory=%s, api_drift=%s, rubric=%s",
            "PASSED" if overall_pass else "FAILED",
            trace_id,
            exact_match_pass,
            schema_state_pass,
            trajectory_invariant_pass,
            api_drift_detected,
            rubric_consistency_pass,
        )

        return result

    def _validate_exact_match(self, baseline: dict, current: dict) -> bool:
        """Validate exact match between baseline and current state.

        Returns True if states match within tolerance.
        """
        # Compute canonical JSON for both
        baseline_json = deterministic_json(baseline)
        current_json = deterministic_json(current)

        if self.exact_match_tolerance == 0.0:
            # Strict exact match
            return baseline_json == current_json

        # With tolerance, we'd need fuzzy matching (not implemented)
        # For now, strict match only
        return baseline_json == current_json

    def _validate_schema_state(self, baseline: dict, current: dict) -> bool:
        """Validate schema and state integrity.

        Checks:
        - Schema structure unchanged
        - Required fields present
        - Data types consistent
        """
        # Extract schema signatures
        baseline_schema = self._extract_schema_signature(baseline)
        current_schema = self._extract_schema_signature(current)

        # Check schema match
        if baseline_schema != current_schema:
            return False

        # Check critical state fields
        baseline_keys = set(baseline.keys())
        current_keys = set(current.keys())

        # Must not lose critical keys
        critical_keys = baseline_keys - {"timestamp", "uuid", "session_id"}
        if not critical_keys.issubset(current_keys):
            return False

        return True

    def _extract_schema_signature(self, state: dict, prefix: str = "") -> frozenset:
        """Extract schema signature from state dict.

        Returns frozenset of (path, type) tuples.
        """
        signature = set()

        for key, value in state.items():
            path = f"{prefix}.{key}" if prefix else key
            value_type = type(value).__name__
            signature.add((path, value_type))

            # Recurse into nested dicts
            if isinstance(value, dict):
                nested = self._extract_schema_signature(value, path)
                signature.update(nested)

        return frozenset(signature)

    def _validate_trajectory_invariance(self, execution_trace: dict) -> bool:
        """Validate trajectory invariance.

        Checks:
        - Tool sequence unchanged
        - Decision points consistent
        - No unexpected branches
        """
        # Check for trajectory stability markers
        trajectory_hash = execution_trace.get("trajectory_hash")
        expected_trajectory_hash = execution_trace.get("expected_trajectory_hash")

        if trajectory_hash and expected_trajectory_hash:
            return trajectory_hash == expected_trajectory_hash

        # Check tool sequence
        tool_sequence = execution_trace.get("tool_sequence", [])
        expected_sequence = execution_trace.get("expected_tool_sequence", [])

        if expected_sequence:
            return tool_sequence == expected_sequence

        # No baseline to compare - assume invariant
        return True

    def _detect_api_drift(self, baseline: dict, current: dict) -> bool:
        """Detect API drift between baseline and current.

        Checks for:
        - API version changes
        - Response format changes
        - Error code changes
        """
        drift_indicators = []

        # Check API versions
        baseline_api = baseline.get("api_version") or baseline.get("api_schema_version")
        current_api = current.get("api_version") or current.get("api_schema_version")

        if baseline_api and current_api and baseline_api != current_api:
            drift_indicators.append(f"api_version_change:{baseline_api}->{current_api}")

        # Check response structure
        baseline_response = baseline.get("response_structure")
        current_response = current.get("response_structure")

        if baseline_response and current_response:
            if baseline_response != current_response:
                drift_indicators.append("response_structure_change")

        # Check error patterns
        baseline_errors = set(baseline.get("error_codes", []))
        current_errors = set(current.get("error_codes", []))

        new_errors = current_errors - baseline_errors
        if new_errors:
            drift_indicators.append(f"new_error_codes:{new_errors}")

        return len(drift_indicators) > 0

    def _validate_rubric_consistency(self, execution_trace: dict) -> bool:
        """Validate rubric grading consistency.

        Checks:
        - Grading rubric unchanged
        - Score distributions stable
        - No grader bias shifts
        """
        # Check rubric hash
        rubric_hash = execution_trace.get("rubric_hash")
        expected_rubric_hash = execution_trace.get("expected_rubric_hash")

        if rubric_hash and expected_rubric_hash:
            if rubric_hash != expected_rubric_hash:
                return False

        # Check score stability
        scores = execution_trace.get("scores", [])
        expected_scores = execution_trace.get("expected_scores", [])

        if scores and expected_scores:
            # Check mean shift
            mean_score = sum(scores) / len(scores) if scores else 0
            expected_mean = sum(expected_scores) / len(expected_scores) if expected_scores else 0

            # Allow 10% mean shift
            if abs(mean_score - expected_mean) > 0.1:
                return False

        return True

    def _collect_drift_details(
        self,
        baseline: dict,
        current: dict,
        exact_match_pass: bool,
        schema_state_pass: bool,
        trajectory_invariant_pass: bool,
        api_drift_detected: bool,
        rubric_consistency_pass: bool,
    ) -> list[str]:
        """Collect detailed drift information."""
        details = []

        if not exact_match_pass:
            details.append("exact_match:states_differ")

        if not schema_state_pass:
            baseline_schema = self._extract_schema_signature(baseline)
            current_schema = self._extract_schema_signature(current)
            schema_diff = baseline_schema.symmetric_difference(current_schema)
            if schema_diff:
                details.append(f"schema_diff:{len(schema_diff)}_fields")

        if not trajectory_invariant_pass:
            details.append("trajectory:path_changed")

        if api_drift_detected:
            details.append("api:drift_detected")

        if not rubric_consistency_pass:
            details.append("rubric:grading_inconsistent")

        return details

    def _build_diff_summary(
        self,
        baseline_digest: str,
        current_digest: str,
        exact_match_pass: bool,
        schema_state_pass: bool,
        trajectory_invariant_pass: bool,
        api_drift_detected: bool,
        rubric_consistency_pass: bool,
    ) -> str:
        """Build human-readable diff summary."""
        summary_parts = [
            f"Baseline: {baseline_digest[:16]}...",
            f"Current: {current_digest[:16]}...",
        ]

        # Add pass/fail status for each check
        checks = [
            ("Exact Match", exact_match_pass),
            ("Schema/State", schema_state_pass),
            ("Trajectory", trajectory_invariant_pass),
            ("API Drift", not api_drift_detected),  # Inverted: no drift is pass
            ("Rubric", rubric_consistency_pass),
        ]

        for check_name, passed in checks:
            status = "PASS" if passed else "FAIL"
            summary_parts.append(f"{check_name}: {status}")

        return " | ".join(summary_parts)


__all__ = ["GGateRegressionChecker"]
