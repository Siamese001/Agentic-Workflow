"""
L5 CONF_CALIB Risk Gate - Structured Risk Decision Engine

Implements deterministic risk evaluation with structured RiskDecision output.
No ML, no wall-clock usage, pure deterministic rules.
"""

from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    """Risk level enumeration for structured decision making."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class RiskDecision:
    """Structured risk decision with deterministic reasons."""

    allow: bool
    level: RiskLevel
    reasons: tuple[str, ...]


class ConfCalibRiskGate:
    """
    CONF_CALIB Risk Gate for deterministic risk evaluation.

    Evaluates payload and D0 injections to produce structured RiskDecision.
    No imports from L0/L2, no wall-clock usage.
    """

    def evaluate(self, *, payload_like: object, d0_injections: str) -> RiskDecision:
        """
        Evaluate risk for given payload and D0 injections.

        Deterministic rules (no ML, no clocks):
        - Start with LOW/allow=True
        - If payload sanitized => at least MEDIUM, reason "SANITIZED_INPUT"
        - If >=5 check_ids => at least MEDIUM, reason "MANY_CHECK_IDS"
        - If D0 contains "DENY_EXECUTION" => HIGH and allow=False, reason "D0_DENY_EXECUTION"
        - Always sort reasons lexicographically

        Args:
            payload_like: Object to evaluate (must not be mutated)
            d0_injections: D0 injection string to evaluate

        Returns:
            Structured RiskDecision with deterministic reasons
        """
        current_level = RiskLevel.LOW
        allow_execution = True
        reasons = []
        if getattr(payload_like, "sanitized", False):
            current_level = RiskLevel.MEDIUM
            reasons.append("SANITIZED_INPUT")
        check_ids = getattr(payload_like, "check_ids", ())
        if len(check_ids) >= 5:
            current_level = RiskLevel.MEDIUM
            reasons.append("MANY_CHECK_IDS")
        if "DENY_EXECUTION" in d0_injections:
            current_level = RiskLevel.HIGH
            allow_execution = False
            reasons.append("D0_DENY_EXECUTION")
        sorted_reasons = tuple(sorted(reasons))
        return RiskDecision(allow=allow_execution, level=current_level, reasons=sorted_reasons)
