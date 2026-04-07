"""Live Exit Control Gate — Evaluation Spine Component A.

Live end-of-inference gate that validates execution results before commit.
Performs:
  - Result structure validation
  - Safety classifier application
  - Confidence threshold check
  - Policy compliance verification

Deterministic, fail-closed, with full ADG traceability.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

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

# ADG wiring for live exit control gate
_emit_records_execution_trace("live_exit_control_gate", "p0", "exit_control_trace")
_emit_applies_guardrail("p0", "live_exit_control_gate", "p0_governance")
emit_replay_key("p0", "live_exit_control_gate")
emit_determinism_digest("p0", "live_exit_control_gate")
_emit_writes_via_uwg("p2", "live_exit_control_gate", "uwg_write")
_emit_blocks_direct_write("p2", "live_exit_control_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "live_exit_control_gate", "tool_invocation")
_emit_captures_execution_output("p2", "live_exit_control_gate", "exec_output")
_emit_dispatches_agent("p3", "live_exit_control_gate", "agent_dispatch")
_emit_dispatches_execution_plan("p3", "live_exit_control_gate", "exec_plan")
_emit_routes_to_agent("p3", "live_exit_control_gate", "target_agent")
_emit_checks_agent_registry("p3", "live_exit_control_gate", "agent_registry")
_emit_validates_agent_capability("p3", "live_exit_control_gate", "capability")
_emit_verifies_policy("p3", "live_exit_control_gate", "policy_check")
_emit_verifies_boundary("p3", "live_exit_control_gate", "boundary_check")
_emit_agent_executes_agent("p3", "live_exit_control_gate", "sub_agent")

logger = logging.getLogger(__name__)


# =============================================================================
# Live Exit Control Types
# =============================================================================


@dataclass(frozen=True)
class ExitControlResult:
    """Result of live exit control gate validation.

    Attributes
    ----------
    artifact_type:
        Always ``EXIT_CONTROL_RESULT``.
    result_id:
        Deterministic SHA-256 ID for this result.
    trace_id:
        Source execution trace identifier.
    allowed:
        True if execution result is allowed to proceed.
    exit_action:
        COMMIT, BLOCK, or ESCALATE.
    block_reason:
        Reason for block (if blocked).
    safety_score:
        Safety classifier score (0.0 to 1.0).
    confidence_score:
        Model confidence score.
    policy_violations:
        Tuple of policy violations detected.
    validation_checks:
        Map of validation check names to pass/fail.
    timestamp_utc:
        Unix timestamp provided by caller.
    """

    artifact_type: Literal["EXIT_CONTROL_RESULT"]
    result_id: str
    trace_id: str
    allowed: bool
    exit_action: Literal["COMMIT", "BLOCK", "ESCALATE"]
    block_reason: str | None
    safety_score: float
    confidence_score: float
    policy_violations: tuple[str, ...]
    validation_checks: dict[str, bool]
    timestamp_utc: int

    def __post_init__(self) -> None:
        if self.artifact_type != "EXIT_CONTROL_RESULT":
            raise ValueError(f"artifact_type must be 'EXIT_CONTROL_RESULT', got {self.artifact_type!r}")
        if not self.result_id:
            raise ValueError("result_id must not be empty")
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if not 0.0 <= self.safety_score <= 1.0:
            raise ValueError(f"safety_score must be in [0.0, 1.0], got {self.safety_score}")
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError(f"confidence_score must be in [0.0, 1.0], got {self.confidence_score}")

    def to_dict(self) -> dict[str, object]:
        return {
            "allowed": self.allowed,
            "artifact_type": self.artifact_type,
            "block_reason": self.block_reason,
            "confidence_score": self.confidence_score,
            "exit_action": self.exit_action,
            "policy_violations": list(self.policy_violations),
            "result_id": self.result_id,
            "safety_score": self.safety_score,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
            "validation_checks": self.validation_checks,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# =============================================================================
# LiveExitControlGate
# =============================================================================


class LiveExitControlGate:
    """Live exit control gate for end-of-inference validation (Component A).

    Validates execution results before commit:
        1. Structure validation
        2. Safety classification
        3. Confidence check
        4. Policy compliance

    Deterministic: Same execution always produces same control decision.
    Fail-closed: Any validation failure results in BLOCK.

    Attributes
    ----------
    safety_threshold:
        Minimum safety score to pass.
    confidence_threshold:
        Minimum confidence to pass.
    require_all_checks:
        If True, all checks must pass.
    """

    DEFAULT_SAFETY_THRESHOLD: float = 0.5
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.7

    def __init__(
        self,
        safety_threshold: float | None = None,
        confidence_threshold: float | None = None,
        require_all_checks: bool = True,
    ) -> None:
        self.safety_threshold = safety_threshold or self.DEFAULT_SAFETY_THRESHOLD
        self.confidence_threshold = confidence_threshold or self.DEFAULT_CONFIDENCE_THRESHOLD
        self.require_all_checks = require_all_checks

    def validate_exit(
        self,
        trace_id: str,
        execution_result: dict,
        timestamp_utc: int,
    ) -> ExitControlResult:
        """Validate execution result at exit gate.

        Parameters
        ----------
        trace_id:
            Source execution trace identifier.
        execution_result:
            The execution result to validate.
        timestamp_utc:
            Unix timestamp provided by caller (no wall-clock reads).

        Returns
        -------
        ExitControlResult
            Deterministic exit control decision.
        """
        _emit_records_execution_trace("live_exit_control_gate", "exit_validation_start", trace_id)

        # Run all validation checks
        validation_checks: dict[str, bool] = {}

        # Check 1: Structure validation
        validation_checks["structure"] = self._validate_structure(execution_result)

        # Check 2: Safety classification
        safety_score = self._classify_safety(execution_result)
        validation_checks["safety"] = safety_score >= self.safety_threshold

        # Check 3: Confidence check
        confidence_score = self._check_confidence(execution_result)
        validation_checks["confidence"] = confidence_score >= self.confidence_threshold

        # Check 4: Policy compliance
        policy_violations = self._check_policy_compliance(execution_result)
        validation_checks["policy"] = len(policy_violations) == 0

        # Determine exit action
        allowed, exit_action, block_reason = self._determine_exit_action(
            validation_checks,
            policy_violations,
            safety_score,
        )

        _emit_records_execution_trace("live_exit_control_gate", "exit_validation_complete", trace_id)

        result = ExitControlResult(
            artifact_type="EXIT_CONTROL_RESULT",
            result_id=stable_sha256_json({
                "trace_id": trace_id,
                "allowed": allowed,
                "exit_action": exit_action,
                "safety_score": safety_score,
                "timestamp_utc": timestamp_utc,
            }),
            trace_id=trace_id,
            allowed=allowed,
            exit_action=exit_action,
            block_reason=block_reason,
            safety_score=safety_score,
            confidence_score=confidence_score,
            policy_violations=tuple(sorted(policy_violations)),
            validation_checks=validation_checks,
            timestamp_utc=timestamp_utc,
        )

        log_level = logging.INFO if allowed else logging.WARNING
        logger.log(
            log_level,
            "Exit control %s: trace_id=%s, action=%s, safety=%.2f, confidence=%.2f",
            "ALLOWED" if allowed else "BLOCKED",
            trace_id,
            exit_action,
            safety_score,
            confidence_score,
        )

        return result

    def _validate_structure(self, execution_result: dict) -> bool:
        """Validate execution result structure."""
        # Check for required fields
        required_fields = {"trace_id", "response"}
        if not required_fields.issubset(execution_result.keys()):
            return False

        # Check response is not empty
        response = execution_result.get("response", "")
        if not response or len(response.strip()) == 0:
            return False

        # Check for valid result type
        result_type = execution_result.get("result_type", "")
        if result_type and result_type not in {"success", "error", "partial"}:
            return False

        return True

    def _classify_safety(self, execution_result: dict) -> float:
        """Classify safety of execution result.

        Returns safety score between 0.0 and 1.0.
        Higher is safer.
        """
        score = 1.0  # Start with perfect safety

        response = execution_result.get("response", "")
        response_lower = response.lower()

        # Check for harmful content indicators
        harmful_indicators = [
            "harmful", "dangerous", "illegal", "malicious",
            "attack", "exploit", "bypass", "hack",
        ]
        for indicator in harmful_indicators:
            if indicator in response_lower:
                score -= 0.2

        # Check for personal information leaks
        pii_indicators = [
            "ssn", "social security", "credit card", "password",
            "api key", "secret", "token",
        ]
        for indicator in pii_indicators:
            if indicator in response_lower:
                score -= 0.3

        # Check for refusal to answer (good safety signal)
        refusal_phrases = [
            "i cannot", "i can't", "i'm not able", "i am not able",
            "i apologize", "i'm unable", "i am unable",
        ]
        if any(phrase in response_lower for phrase in refusal_phrases):
            score += 0.1

        # Check for uncertainty (neutral safety signal)
        uncertainty_phrases = ["i'm not sure", "i don't know", "uncertain"]
        if any(phrase in response_lower for phrase in uncertainty_phrases):
            score -= 0.05

        return max(0.0, min(1.0, score))

    def _check_confidence(self, execution_result: dict) -> float:
        """Check model confidence in execution result."""
        # Use explicit confidence if provided
        explicit_confidence = execution_result.get("confidence")
        if explicit_confidence is not None:
            return float(explicit_confidence)

        # Calculate from uncertainty indicators
        response = execution_result.get("response", "")
        response_lower = response.lower()

        confidence = 0.8  # Default confidence

        # Reduce confidence for hedging language
        hedging_phrases = [
            "might", "maybe", "perhaps", "possibly", "could be",
            "may be", "i think", "i believe",
        ]
        for phrase in hedging_phrases:
            if phrase in response_lower:
                confidence -= 0.05

        # Reduce confidence for very short responses
        if len(response) < 50:
            confidence -= 0.1

        # Reduce confidence for very long responses (potential rambling)
        if len(response) > 2000:
            confidence -= 0.05

        return max(0.0, min(1.0, confidence))

    def _check_policy_compliance(self, execution_result: dict) -> list[str]:
        """Check policy compliance of execution result.

        Returns list of policy violations.
        """
        violations: list[str] = []

        response = execution_result.get("response", "")
        response_lower = response.lower()

        # Check content policies
        content_violations = {
            "hate_speech": ["hate", "discriminat", "racist"],
            "harassment": ["harass", "bully", "threaten"],
            "violence": ["kill", "hurt", "violence", "weapon"],
            "self_harm": ["suicide", "self-harm", "hurt myself"],
            "sexual_content": ["sexual", "pornography", "explicit"],
        }

        for violation_type, indicators in content_violations.items():
            if any(indicator in response_lower for indicator in indicators):
                violations.append(f"content_policy:{violation_type}")

        # Check for instruction following
        instruction_followed = execution_result.get("instruction_followed", True)
        if not instruction_followed:
            violations.append("instruction_following:failed")

        # Check for groundedness (if citation required)
        requires_citation = execution_result.get("requires_citation", False)
        has_citation = "[" in response and "]" in response
        if requires_citation and not has_citation:
            violations.append("groundedness:missing_citation")

        return violations

    def _determine_exit_action(
        self,
        validation_checks: dict[str, bool],
        policy_violations: list[str],
        safety_score: float,
    ) -> tuple[bool, Literal["COMMIT", "BLOCK", "ESCALATE"], str | None]:
        """Determine exit action based on validation results."""
        passed_checks = sum(validation_checks.values())
        total_checks = len(validation_checks)

        # Critical violations result in immediate block
        critical_violations = ["content_policy", "instruction_following"]
        has_critical = any(
            any(cv in pv for cv in critical_violations)
            for pv in policy_violations
        )

        if has_critical or safety_score < 0.3:
            return False, "BLOCK", f"Critical violations: {policy_violations}"

        # Check if all required checks passed
        if self.require_all_checks:
            if passed_checks < total_checks:
                failed_checks = [name for name, passed in validation_checks.items() if not passed]
                return False, "BLOCK", f"Failed checks: {failed_checks}"

        # Safety or policy issues result in escalation
        if safety_score < self.safety_threshold or policy_violations:
            return True, "ESCALATE", f"Safety: {safety_score:.2f}, Violations: {policy_violations}"

        # All checks passed
        return True, "COMMIT", None


__all__ = ["LiveExitControlGate", "ExitControlResult"]
