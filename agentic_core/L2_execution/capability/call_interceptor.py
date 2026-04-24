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
    # W1-P1.3 (gap plan b7c4e2 G8): populated when the E2 validate-before-execute
    # gate short-circuits with a HITL confirmation requirement or a hard rejection.
    needs_hitl_confirmation: bool = False
    e2_verdict: dict[str, Any] | None = None


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
        """Intercept and validate call.

        W1-P1.3 (gap plan b7c4e2 G8): when ``context["tool_contract"]`` is a
        ``ToolContract`` instance, the E2 validate-before-execute gate runs
        AFTER argument/injection/risk checks but BEFORE returning an
        allow verdict. High-consequence or irreversible-non-read tools
        short-circuit with ``needs_hitl_confirmation=True`` and no further
        execution; the caller must route to [5] HITL and re-invoke with a
        ``e2_hitl_approval_ticket`` in the contract metadata.
        """
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

        # W1-P1.3: E2 validate-before-execute short-circuit (opt-in, gap plan G8).
        e2_result = self._maybe_run_e2_gate(context, risk_tier)
        if e2_result is not None:
            return e2_result

        return InterceptResult(
            is_allowed=True,
            risk_tier=risk_tier,
            injection_detected=False,
            argument_valid=True,
        )

    def _maybe_run_e2_gate(
        self,
        context: dict[str, Any],
        risk_tier: str,
    ) -> InterceptResult | None:
        """Run the E2 validate-before-execute gate when a ToolContract is attached.

        Returns a non-None ``InterceptResult`` to short-circuit with a HITL
        confirmation requirement or hard rejection; returns None to continue
        with the normal allow path. Imports are local so this module stays
        loadable when the W1 safety modules are absent.
        """
        tool_contract = context.get("tool_contract")
        if tool_contract is None:
            return None

        try:
            from agentic_core.L2_execution.enforcement.e2_validate_before_execute import (  # noqa: PLC0415
                ConfirmBeforeExecute,
                E2RejectedBeforeExecute,
                evaluate_work_order,
            )
            from agentic_core.L2_execution.types.execution_tool_contract import (  # noqa: PLC0415
                ToolContract,
            )
        except ImportError:  # guardian: allow-return-none-swallow -- optional safety/contracts module unavailable; None signals gate unavailable to caller
            return None

        if not isinstance(tool_contract, ToolContract):
            return None

        try:
            evaluate_work_order(tool_contract)
        except ConfirmBeforeExecute as exc:
            return InterceptResult(
                is_allowed=False,
                risk_tier=risk_tier,
                injection_detected=False,
                argument_valid=True,
                rejection_reason="e2_hitl_required",
                needs_hitl_confirmation=True,
                e2_verdict=exc.verdict.to_dict(),
            )
        except E2RejectedBeforeExecute as exc:
            return InterceptResult(
                is_allowed=False,
                risk_tier="CRITICAL",
                injection_detected=False,
                argument_valid=True,
                rejection_reason="e2_policy_rejected",
                needs_hitl_confirmation=False,
                e2_verdict=exc.verdict.to_dict(),
            )
        return None

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
