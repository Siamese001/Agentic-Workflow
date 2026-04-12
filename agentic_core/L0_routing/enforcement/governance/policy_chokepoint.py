"""C0 G6: POLICY CHOKEPOINT - Actual enforcement decision.

10C-REQ-115: Reject remediate certify record injection detection
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class DecisionType(Enum):
    """Policy chokepoint decisions."""

    REJECT = auto()  # Block and deny
    REMEDIATE = auto()  # Allow with modification
    CERTIFY = auto()  # Allow as-is
    ESCALATE = auto()  # Send to HITL


@dataclass
class ChokepointDecision:
    """Result of policy chokepoint."""

    decision: DecisionType
    is_allowed: bool
    reason: str
    modification: dict[str, Any] | None = None
    injection_detected: bool = False
    confidence: float = 1.0


class PolicyChokepoint:
    """C0 G6: Policy chokepoint.

    10C-REQ-115: Reject remediate certify record injection detection.
    """

    def __init__(self) -> None:
        self._policy_rules: list[dict[str, Any]] = []
        self._injection_patterns: list[str] = []
        self._decision_count: dict[DecisionType, int] = {d: 0 for d in DecisionType}

    def evaluate(
        self,
        request: dict[str, Any],
        context: dict[str, Any],
        risk_score: float = 0.0,
    ) -> ChokepointDecision:
        """Evaluate request at policy chokepoint."""
        # Check for injection
        injection = self._detect_injection(request)
        if injection:
            self._decision_count[DecisionType.REJECT] += 1
            return ChokepointDecision(
                decision=DecisionType.REJECT,
                is_allowed=False,
                reason="injection_detected",
                injection_detected=True,
                confidence=1.0,
            )

        # Check policy rules
        for rule in self._policy_rules:
            match = self._check_rule(request, context, rule)
            if match:
                decision = rule.get("decision", "CERTIFY")
                decision_type = DecisionType[decision]
                self._decision_count[decision_type] += 1

                return ChokepointDecision(
                    decision=decision_type,
                    is_allowed=decision_type in (DecisionType.CERTIFY, DecisionType.REMEDIATE),
                    reason=rule.get("reason", "policy_match"),
                    modification=rule.get("modification")
                    if decision_type == DecisionType.REMEDIATE
                    else None,
                    confidence=rule.get("confidence", 0.9),
                )

        # Default: certify if low risk
        if risk_score < 0.3:
            self._decision_count[DecisionType.CERTIFY] += 1
            return ChokepointDecision(
                decision=DecisionType.CERTIFY,
                is_allowed=True,
                reason="low_risk_default",
                confidence=0.95,
            )

        # Default: escalate for medium-high risk
        self._decision_count[DecisionType.ESCALATE] += 1
        return ChokepointDecision(
            decision=DecisionType.ESCALATE,
            is_allowed=False,
            reason="risk_requires_hitl",
            confidence=risk_score,
        )

    def _detect_injection(self, request: dict[str, Any]) -> bool:
        """Detect prompt injection attempts."""
        text = str(request.get("prompt", "")) + str(request.get("input", ""))

        for pattern in self._injection_patterns:
            if pattern.lower() in text.lower():
                return True

        # Check for common injection patterns
        injection_markers = [
            "ignore previous instructions",
            "disregard the above",
            "system override",
            "admin mode",
            "ignore all rules",
        ]

        for marker in injection_markers:
            if marker in text.lower():
                return True

        return False

    def _check_rule(
        self,
        request: dict[str, Any],
        context: dict[str, Any],
        rule: dict[str, Any],
    ) -> bool:
        """Check if request matches a policy rule."""
        conditions = rule.get("conditions", [])

        for condition in conditions:
            field = condition.get("field")
            op = condition.get("op", "eq")
            value = condition.get("value")

            request_value = request.get(field) or context.get(field)

            if op == "eq" and request_value != value:
                return False
            if op == "ne" and request_value == value:
                return False
            if op == "in" and request_value not in value:
                return False
            if op == "contains" and value not in str(request_value):
                return False

        return True

    def add_policy_rule(self, rule: dict[str, Any]) -> None:
        """Add a policy rule."""
        self._policy_rules.append(rule)

    def add_injection_pattern(self, pattern: str) -> None:
        """Add an injection detection pattern."""
        self._injection_patterns.append(pattern)

    def get_decision_stats(self) -> dict[str, int]:
        """Get decision statistics."""
        return {d.name: count for d, count in self._decision_count.items()}
