"""Architectural Guardrails - Real-time validation for agent actions.

This module provides guardrail implementations that prevent agents from
performing architecturally risky actions without proper validation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from .decision_engine import AgentDecisionEngine, ArchitecturalContext, DecisionResult, RiskLevel

logger = logging.getLogger(__name__)


class GuardrailAction(Enum):
    """Actions guardrails can take on agent requests."""

    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    REQUIRE_ALTERNATIVE = "require_alternative"


@dataclass
class GuardrailResult:
    """Result of guardrail validation."""

    action: GuardrailAction
    message: str
    decision_result: DecisionResult
    required_modifications: List[str]
    escalation_required: bool


class ArchitecturalGuardrails:
    """Real-time architectural guardrails for agent actions."""

    def __init__(self, decision_engine: AgentDecisionEngine):
        """Initialize guardrails with decision engine.

        Args:
            decision_engine: AgentDecisionEngine for architectural analysis
        """
        self.decision_engine = decision_engine
        self.blocked_actions = []
        self.warned_actions = []

        logger.info("ArchitecturalGuardrails initialized")

    def validate_action(self, context: ArchitecturalContext) -> GuardrailResult:
        """Validate an agent action against architectural guardrails.

        Args:
            context: Architectural context for the action

        Returns:
            GuardrailResult with validation outcome
        """
        logger.info(f"Validating {context.action_type} action for {context.agent_type}")

        # Get architectural analysis
        decision_result = self.decision_engine.analyze_action(context)

        # Apply guardrail logic
        if decision_result.risk_level == RiskLevel.CRITICAL:
            return self._handle_critical_risk(context, decision_result)
        elif decision_result.risk_level == RiskLevel.HIGH:
            return self._handle_high_risk(context, decision_result)
        elif decision_result.risk_level == RiskLevel.MEDIUM:
            return self._handle_medium_risk(context, decision_result)
        else:
            return self._handle_low_risk(context, decision_result)

    def _handle_critical_risk(
        self, context: ArchitecturalContext, decision_result: DecisionResult
    ) -> GuardrailResult:
        """Handle critical risk actions."""
        logger.warning(f"CRITICAL RISK: Blocking {context.action_type} for {context.agent_type}")

        self.blocked_actions.append(
            {
                "timestamp": self._get_timestamp(),
                "context": context,
                "reason": "Critical architectural risk",
                "violations": len(decision_result.warnings),
            }
        )

        return GuardrailResult(
            action=GuardrailAction.BLOCK,
            message=f"Action BLOCKED due to critical architectural risk: {decision_result.architectural_justification}",
            decision_result=decision_result,
            required_modifications=self._get_critical_modifications(decision_result),
            escalation_required=True,
        )

    def _handle_high_risk(
        self, context: ArchitecturalContext, decision_result: DecisionResult
    ) -> GuardrailResult:
        """Handle high risk actions."""
        logger.warning(f"HIGH RISK: Warning on {context.action_type} for {context.agent_type}")

        self.warned_actions.append(
            {
                "timestamp": self._get_timestamp(),
                "context": context,
                "reason": "High architectural risk",
                "impact": decision_result.insights,
            }
        )

        # Check if safer alternatives exist
        if decision_result.alternatives:
            return GuardrailResult(
                action=GuardrailAction.REQUIRE_ALTERNATIVE,
                message=f"Action requires safer alternative due to high architectural risk",
                decision_result=decision_result,
                required_modifications=[alt["description"] for alt in decision_result.alternatives],
                escalation_required=False,
            )
        else:
            return GuardrailResult(
                action=GuardrailAction.WARN,
                message=f"Action PROCEED WITH CAUTION: {decision_result.architectural_justification}",
                decision_result=decision_result,
                required_modifications=[],
                escalation_required=False,
            )

    def _handle_medium_risk(
        self, context: ArchitecturalContext, decision_result: DecisionResult
    ) -> GuardrailResult:
        """Handle medium risk actions."""
        logger.info(f"MEDIUM RISK: Allowing {context.action_type} with warnings for {context.agent_type}")

        return GuardrailResult(
            action=GuardrailAction.WARN,
            message=f"Action allowed with architectural considerations: {decision_result.architectural_justification}",
            decision_result=decision_result,
            required_modifications=[],
            escalation_required=False,
        )

    def _handle_low_risk(
        self, context: ArchitecturalContext, decision_result: DecisionResult
    ) -> GuardrailResult:
        """Handle low risk actions."""
        logger.info(f"LOW RISK: Allowing {context.action_type} for {context.agent_type}")

        return GuardrailResult(
            action=GuardrailAction.ALLOW,
            message=f"Action approved: {decision_result.architectural_justification}",
            decision_result=decision_result,
            required_modifications=[],
            escalation_required=False,
        )

    def _get_critical_modifications(self, decision_result: DecisionResult) -> List[str]:
        """Get required modifications for critical risk actions."""
        modifications = []

        # Add modifications based on warnings
        for warning in decision_result.warnings:
            if "UWG bypass" in warning:
                modifications.append("Route writes through approved UWG gateways")
            elif "blast radius" in warning:
                modifications.append("Reduce blast radius: reduce scope or implement in phases")

        # Add modifications based on alternatives
        for alt in decision_result.alternatives:
            modifications.append(f"Consider: {alt['description']}")

        return modifications

    def _get_timestamp(self) -> str:
        """Get current timestamp for logging."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    def get_guardrail_statistics(self) -> Dict[str, Any]:
        """Get statistics on guardrail actions."""
        return {
            "total_blocked": len(self.blocked_actions),
            "total_warned": len(self.warned_actions),
            "recent_blocks": [block for block in self.blocked_actions if self._is_recent(block["timestamp"])],
            "recent_warnings": [
                warning for warning in self.warned_actions if self._is_recent(warning["timestamp"])
            ],
            "block_rate": len(self.blocked_actions)
            / max(1, len(self.blocked_actions) + len(self.warned_actions)),
        }

    def _is_recent(self, timestamp: str, hours: int = 24) -> bool:
        """Check if timestamp is within recent hours."""
        from datetime import datetime, timedelta, timezone

        try:
            action_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            return action_time > cutoff
        except (ValueError, AttributeError):
            return False


class HighRiskActionFilter:
    """Filter for identifying high-risk agent actions that require guardrails."""

    HIGH_RISK_PATTERNS = {
        "file_write": ["write", "create", "modify", "delete"],
        "module_import": ["import", "from"],
        "gateway_bypass": ["direct_write", "skip_gateway"],
        "layer_violation": ["cross_layer", "layer_bypass"],
        "critical_path": ["spine", "critical", "core"],
    }

    @classmethod
    def is_high_risk(cls, action_type: str, target_modules: List[str]) -> bool:
        """Check if an action is high risk based on patterns.

        Args:
            action_type: Type of action being performed
            target_modules: List of target modules

        Returns:
            True if action is considered high risk
        """
        action_lower = action_type.lower()

        # Check action type patterns
        for risk_category, patterns in cls.HIGH_RISK_PATTERNS.items():
            if any(pattern in action_lower for pattern in patterns):
                return True

        # Check module patterns
        for module in target_modules:
            module_lower = module.lower()
            for patterns in cls.HIGH_RISK_PATTERNS.values():
                if any(pattern in module_lower for pattern in patterns):
                    return True

        return False

    @classmethod
    def get_required_validations(cls, action_type: str) -> List[str]:
        """Get required validations for a given action type.

        Args:
            action_type: Type of action being performed

        Returns:
            List of required validation types
        """
        validations = []
        action_lower = action_type.lower()

        if any(pattern in action_lower for pattern in cls.HIGH_RISK_PATTERNS["file_write"]):
            validations.extend(["illegal_paths", "uwg_conformance"])

        if any(pattern in action_lower for pattern in cls.HIGH_RISK_PATTERNS["module_import"]):
            validations.extend(["layer_violations", "blast_radius"])

        if any(pattern in action_lower for pattern in cls.HIGH_RISK_PATTERNS["gateway_bypass"]):
            validations.extend(["uwg_conformance", "sovereignty_check"])

        if any(pattern in action_lower for pattern in cls.HIGH_RISK_PATTERNS["layer_violation"]):
            validations.extend(["gravity_imports", "layer_reach"])

        return validations
