from __future__ import annotations
import logging
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
from typing import Any, Dict, Optional
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.mixins import SubatomicTestingMixin

class CostGovernorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    L5 Safety: The Financial Guardrail.
    Tracks and limits spend across models and tools.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.limit = config.get('budget_limit', 10.0)
        self.spend = 0.0

    def track(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculates and records the cost of an LLM call."""
        cost: Any = (input_tokens + output_tokens) * 2e-05
        self.spend += cost
        logging.info(f'Governor: Current Spend ${self.spend:.4f} / Limit ${self.limit:.2f}')
        if self.spend > self.limit:
            raise Exception(f'BUDGET EXCEEDED: ${self.spend:.2f} exceeds limit of ${self.limit:.2f}')
        return cost

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L5 safety agent - operational only."""
        # Call parent heal_repository if available
        if hasattr(super(), 'heal_repository'):
            super().heal_repository()
        
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)
