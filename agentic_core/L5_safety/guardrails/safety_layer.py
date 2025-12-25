"""L5 Safety Layer Integration.

Coordinates PII Vault, Constitutional Overseer, and Cost Governor.
"""
from typing import Any, Optional, Protocol, Dict, List
import re
import logging
from typing import Any, Dict, TYPE_CHECKING

from agentic_core.L1_cognition.P1_interfaces import ActionRequest

if TYPE_CHECKING:
    from agentic_core.governor import create_cost_governor
    from agentic_core.overseer import create_overseer
    from agentic_core.pii_vault import create_pii_vault

LOGGER = logging.getLogger(__name__)


class L5SafetyLayer:
    """L5 Safety Layer that validates all actions before execution."""

    def __init__(self, cost_limit_usd: float = 5.00):
        """Initialize the safety layer.

        Args:
            cost_limit_usd: Maximum allowed cost in USD
        """
        self.pii_vault = create_pii_vault()
        self.overseer = create_overseer()
        self.cost_governor = create_cost_governor(cost_limit_usd)

        self.session_id = "mission-session"
        self.validation_count = 0
        self.blocked_count = 0

        LOGGER.info("L5 Safety Layer initialized")

    async def validate_action(self, request: ActionRequest) -> bool:
        """Validate an action request through all safety checks.

        Args:
            request: The ActionRequest to validate

        Returns:
            True if action is safe and approved, False otherwise
        """
        self.validation_count += 1

        try:
            # 1. Constitutional Overseer validation
            violation = await self.overseer.validate_action(request)
            if violation.is_violation:
                self.blocked_count += 1
                LOGGER.error(f"L5: Action BLOCKED - {violation.reason}")
                return False

            # 2. PII redaction check (for parameters containing text)
            await self._check_and_redact_pii(request)

            # 3. Cost validation (estimate)
            if not self._validate_cost_estimate(request):
                self.blocked_count += 1
                LOGGER.error("L5: Action BLOCKED - Cost limit would be exceeded")
                return False

            LOGGER.info(f"L5: Action Validated - [SAFE]")
            return True

        except Exception as e:
            self.blocked_count += 1
            LOGGER.error(f"L5: Validation error - {e}")
            return False

    async def _check_and_redact_pii(self, request: ActionRequest):
        """Check request parameters for PII and redact if necessary.

        Args:
            request: ActionRequest to check
        """
        # Check text parameters for PII
        for key, value in request.parameters.items():
            if isinstance(value, str) and len(value) > 10:
                # Check for potential PII patterns
                if any(keyword in value.lower() for keyword in ['email', 'phone', 'ssn', 'address']):
                    redacted = self.pii_vault.redact(self.session_id, value)
                    if redacted != value:
                        LOGGER.warning(f"L5: PII detected and redacted in parameter '{key}'")
                        request.parameters[key] = redacted

    def _validate_cost_estimate(self, request: ActionRequest) -> bool:
        """Validate if the estimated cost is within budget.

        Args:
            request: ActionRequest to validate

        Returns:
            True if cost is acceptable, False otherwise
        """
        # Simple cost estimation based on action type
        estimated_tokens = {
            "tool_execution": 100,
            "file_operations": 50,
            "diagnostic_tool_creation": 500,
        }.get(request.action_type, 100)

        return self.cost_governor.check_action_cost(estimated_tokens)

    def track_action_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Track actual cost after action execution.

        Args:
            model: Model used
            input_tokens: Input tokens consumed
            output_tokens: Output tokens generated

        Returns:
            Cost of the action

        Raises:
            BudgetExceededError: If budget is exceeded
        """
        return self.cost_governor.track(model, input_tokens, output_tokens)

    def get_safety_stats(self) -> Dict[str, Any]:
        """Get safety layer statistics.

        Returns:
            Dictionary with safety statistics
        """
        return {
            "validations_performed": self.validation_count,
            "actions_blocked": self.blocked_count,
            "block_rate_percent": (self.blocked_count / max(self.validation_count, 1)) * 100,
            "pii_vault_stats": self.pii_vault.get_stats(),
            "cost_governor_stats": self.cost_governor.get_stats(),
            "forbidden_patterns_count": len(self.overseer.get_forbidden_patterns())
        }

    def cleanup(self):
        """Cleanup resources and sessions."""
        self.pii_vault.clear_session(self.session_id)
        LOGGER.info("L5 Safety Layer cleanup complete")


def create_l5_safety_layer(cost_limit_usd: float = 5.00) -> L5SafetyLayer:
    """Factory function to create L5 safety layer.

    Args:
        cost_limit_usd: Maximum allowed cost in USD

    Returns:
        L5SafetyLayer instance
    """
    return L5SafetyLayer(cost_limit_usd)
