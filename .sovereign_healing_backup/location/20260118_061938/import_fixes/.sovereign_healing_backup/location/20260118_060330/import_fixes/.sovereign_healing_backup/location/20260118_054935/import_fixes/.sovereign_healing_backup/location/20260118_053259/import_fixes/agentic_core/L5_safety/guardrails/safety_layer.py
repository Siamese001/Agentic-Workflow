from __future__ import annotations
"""L5 Safety Layer Integration.

Coordinates PII Vault, Constitutional Overseer, and Cost Governor.
"""
import logging
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol
from agentic_core.L1_cognition.P1_interfaces import ActionRequest

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

if TYPE_CHECKING:
    from agentic_core.governor import create_cost_governor
    from agentic_core.overseer import create_overseer
    from agentic_core.PiiVault import create_pii_vault
Logger: Any = logging.getLogger(__name__)

class L5SafetyLayer:
    """L5 Safety Layer that validates all actions before execution."""

    def __init__(self, cost_limit_usd: float=5.0):
        """Initialize the safety layer.

        Args:
            cost_limit_usd: Maximum allowed cost in USD
        """
        self.PiiVault = create_pii_vault()
        self.overseer = create_overseer()
        self.CostGovernor = create_cost_governor(cost_limit_usd)
        self.session_id = 'mission-session'
        self.validation_count = 0
        self.blocked_count = 0
        LOGGER.info('L5 Safety Layer initialized')

    async def validate_action(self, request: ActionRequest) -> bool:
        """Validate an action request through all safety checks.

        Args:
            request: The ActionRequest to validate

        Returns:
            True if action is safe and approved, False otherwise
        """
        self.validation_count += 1
        try:
            Violation: Any = await self.overseer.validate_action(request)
            if Violation.is_violation:
                self.blocked_count += 1
                LOGGER.error(f'L5: Action BLOCKED - {Violation.reason}')
                return False
            await self._check_and_redact_pii(request)
            if not self._validate_cost_estimate(request):
                self.blocked_count += 1
                LOGGER.error('L5: Action BLOCKED - Cost limit would be exceeded')
                return False
            LOGGER.info(f'L5: Action Validated - [SAFE]')
            return True
        except Exception as e:
            self.blocked_count += 1
            LOGGER.error(f'L5: Validation error - {e}')
            return False

    async def _check_and_redact_pii(self, request: ActionRequest):
        """Check request parameters for PII and redact if necessary.

        Args:
            request: ActionRequest to check
        """
        for key, value in request.parameters.items():
            if isinstance(value, str) and len(value) > 10:
                if any((keyword in value.lower() for keyword in ['email', 'phone', 'ssn', 'address'])):
                    redacted = self.PiiVault.redact(self.session_id, value)
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
        estimated_tokens = {'tool_execution': 100, 'file_operations': 50, 'diagnostic_tool_creation': 500}.get(request.action_type, 100)
        return self.CostGovernor.check_action_cost(estimated_tokens)

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
        return self.CostGovernor.track(model, input_tokens, output_tokens)

    def get_safety_stats(self) -> Dict[str, Any]:
        """Get safety layer statistics.

        Returns:
            Dictionary with safety statistics
        """
        return {'validations_performed': self.validation_count, 'actions_blocked': self.blocked_count, 'block_rate_percent': self.blocked_count / max(self.validation_count, 1) * 100, 'pii_vault_stats': self.PiiVault.get_stats(), 'cost_governor_stats': self.CostGovernor.get_stats(), 'forbidden_patterns_count': len(self.overseer.get_forbidden_patterns())}

    def cleanup(self) -> Any:
        """Cleanup resources and sessions."""
        self.PiiVault.clear_session(self.session_id)
        LOGGER.info('L5 Safety Layer cleanup complete')

def create_l5_safety_layer(cost_limit_usd: float=5.0) -> L5SafetyLayer:
    """Factory function to create L5 safety layer.

    Args:
        cost_limit_usd: Maximum allowed cost in USD

    Returns:
        L5SafetyLayer instance
    """
    return L5SafetyLayer(cost_limit_usd)