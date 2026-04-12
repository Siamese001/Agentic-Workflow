"""C7 G5: INTERCEPT THE CALL - Validate arguments and check risk.

10C-REQ-159: Validate argument shape route target injection checks risk tiering
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class InterceptResult:
    """Result of call interception."""

    is_allowed: bool
    risk_tier: str
    injection_detected: bool
    argument_valid: bool
    rejection_reason: str = ""
    modified_args: dict[str, Any] | None = None


class CallInterceptor:
    """C7 G5: Call interceptor.

    10C-REQ-159: Validate argument shape route target injection checks
    assess risk tiering against current policy.
    """

    def __init__(self) -> None:
        self._injection_patterns: list[str] = [
            "ignore previous",
            "disregard",
            "system prompt",
            "admin override",
        ]
        self._risk_thresholds = {
            "LOW": 0.3,
            "MEDIUM": 0.5,
            "HIGH": 0.7,
            "CRITICAL": 0.9,
        }

    def intercept(
        self,
        target: str,
        args: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> InterceptResult:
        """Intercept and validate call."""
        context = context or {}

        # Validate argument shape
        arg_valid = self._validate_arguments(args, target)
        if not arg_valid:
            return InterceptResult(
                is_allowed=False,
                risk_tier="CRITICAL",
                injection_detected=False,
                argument_valid=False,
                rejection_reason="argument_shape_invalid",
            )

        # Check for injection
        injection = self._detect_injection(args)
        if injection:
            return InterceptResult(
                is_allowed=False,
                risk_tier="CRITICAL",
                injection_detected=True,
                argument_valid=True,
                rejection_reason="injection_detected",
            )

        # Assess risk tier
        risk_score = self._assess_risk(args, context)
        risk_tier = self._tier_from_score(risk_score)

        # Check against policy
        if risk_score > self._risk_thresholds["HIGH"]:
            return InterceptResult(
                is_allowed=False,
                risk_tier=risk_tier,
                injection_detected=False,
                argument_valid=True,
                rejection_reason=f"risk_too_high:{risk_score:.2f}",
            )

        return InterceptResult(
            is_allowed=True,
            risk_tier=risk_tier,
            injection_detected=False,
            argument_valid=True,
        )

    def _validate_arguments(self, args: dict[str, Any], target: str) -> bool:
        """Validate argument shape for target."""
        # Check for required fields
        if "operation" not in args:
            return False

        # Type validation
        for key, value in args.items():
            if key == "timeout" and not isinstance(value, (int, float)):
                return False
            if key == "retry_count" and not isinstance(value, int):
                return False

        return True

    def _detect_injection(self, args: dict[str, Any]) -> bool:
        """Detect prompt injection in arguments."""
        text = str(args.get("prompt", "")) + str(args.get("input", ""))
        text_lower = text.lower()

        for pattern in self._injection_patterns:
            if pattern in text_lower:
                return True

        return False

    def _assess_risk(self, args: dict[str, Any], context: dict[str, Any]) -> float:
        """Assess risk score for call."""
        score = 0.0

        # External calls are higher risk
        if "http" in str(args.get("target", "")):
            score += 0.3

        # Large timeouts are higher risk
        timeout = args.get("timeout", 30)
        if timeout > 300:  # > 5 minutes
            score += 0.2

        # Write operations are higher risk
        if "write" in str(args.get("operation", "")):
            score += 0.4

        return min(score, 1.0)

    def _tier_from_score(self, score: float) -> str:
        """Convert risk score to tier."""
        for tier, threshold in sorted(self._risk_thresholds.items(), key=lambda x: x[1]):
            if score <= threshold:
                return tier
        return "CRITICAL"

    def add_injection_pattern(self, pattern: str) -> None:
        """Add injection detection pattern."""
        self._injection_patterns.append(pattern.lower())
