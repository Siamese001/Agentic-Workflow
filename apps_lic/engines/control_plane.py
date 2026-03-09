"""3.6: Control Plane — centralized safety policy enforcement for apps_lic.

Delegates evaluate_input/evaluate_output to GovernanceShieldAgent.
Wired into LicSpineAdapter before/after ExecutionOrchestrator.execute().
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class PolicyAction(Enum):
    """Actions the control plane can take."""

    ALLOW = "allow"
    BLOCK = "block"
    SANITIZE = "sanitize"
    WARN = "warn"
    REVIEW = "review"


@dataclass
class PolicyDecision:
    """Decision from control plane evaluation."""

    action: PolicyAction
    is_safe: bool
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
        if self.metadata is None:
            self.metadata = {}


_PII_PATTERNS = (
    "ssn",
    "social security",
    "credit card",
    "passport",
    "date of birth",
    "phone number",
    "email address",
    "@gmail",
    "@yahoo",
    "@hotmail",
)


class ControlPlane:
    """Centralized Control Plane for safety policy enforcement.

    Delegates all evaluation to GovernanceShieldAgent.
    Gate A: evaluate_input(pii_content) → PolicyAction != ALLOW
    """

    def __init__(self, policy: dict[str, Any] | None = None) -> None:
        self._policy = policy or {}
        self._decision_count = 0
        self._block_count = 0
        self._shield: Any = None
        try:
            from apps_lic.reasoning.GovernanceShieldAgent import GovernanceShieldAgent

            self._shield = GovernanceShieldAgent()
        except Exception as exc:
            logger.warning("ControlPlane: GovernanceShieldAgent not available: %s", exc)

    def evaluate_input(
        self,
        content: str,
        context: dict[str, Any] | None = None,
    ) -> PolicyDecision:
        """Evaluate input content before processing.

        Returns PolicyDecision with action != ALLOW when PII or safety violations found.
        """
        return self._evaluate(content, context, is_input=True)

    def evaluate_output(
        self,
        content: str,
        context: dict[str, Any] | None = None,
    ) -> PolicyDecision:
        """Evaluate output content before delivery."""
        return self._evaluate(content, context, is_input=False)

    def _evaluate(
        self,
        content: str,
        context: dict[str, Any] | None,
        is_input: bool,
    ) -> PolicyDecision:
        """Core evaluation: delegates to GovernanceShieldAgent, then PII check."""
        self._decision_count += 1
        warnings: list[str] = []
        errors: list[str] = []
        content_lower = content.lower()

        # PII check
        detected_pii = [p for p in _PII_PATTERNS if p in content_lower]
        if detected_pii:
            errors.append(f"PII detected: {detected_pii}")
            self._block_count += 1
            logger.warning(
                "ControlPlane: PII detected in %s content: %s",
                "input" if is_input else "output",
                detected_pii,
            )
            return PolicyDecision(
                action=PolicyAction.BLOCK,
                is_safe=False,
                warnings=warnings,
                errors=errors,
                metadata={"is_input": is_input, "decision_id": self._decision_count, "pii": detected_pii},
            )

        # GovernanceShieldAgent evaluation
        if self._shield is not None:
            try:
                shield_result = self._shield.evaluate(content)
                if isinstance(shield_result, dict):
                    if shield_result.get("blocked"):
                        errors.append(f"GovernanceShield blocked: {shield_result.get('reason', 'policy')}")
                        self._block_count += 1
                        return PolicyDecision(
                            action=PolicyAction.BLOCK,
                            is_safe=False,
                            warnings=warnings,
                            errors=errors,
                            metadata={
                                "is_input": is_input,
                                "decision_id": self._decision_count,
                                "shield": shield_result,
                            },
                        )
                    if shield_result.get("warnings"):
                        warnings.extend(shield_result["warnings"])
            except Exception as exc:
                logger.warning("ControlPlane: GovernanceShieldAgent.evaluate failed: %s", exc)

        action = PolicyAction.WARN if warnings else PolicyAction.ALLOW
        return PolicyDecision(
            action=action,
            is_safe=True,
            warnings=warnings,
            errors=errors,
            metadata={"is_input": is_input, "decision_id": self._decision_count},
        )

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_decisions": self._decision_count,
            "total_blocks": self._block_count,
        }


__all__ = ["ControlPlane", "PolicyAction", "PolicyDecision"]
