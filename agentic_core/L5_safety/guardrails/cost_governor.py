import logging
from typing import Dict, Any

class CostGovernor:
    """
    L5 Safety: The Financial Guardrail.
    Tracks and limits spend across models and tools.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.limit = config.get("budget_limit", 10.0)
        self.spend = 0.0

    def track(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculates and records the cost of an LLM call."""
        # Simple math for the sovereign demo
        cost = (input_tokens + output_tokens) * 0.00002
        self.spend += cost
        
        logging.info(f"Governor: Current Spend ${self.spend:.4f} / Limit ${self.limit:.2f}")
        
        if self.spend > self.limit:
            raise Exception(f"BUDGET EXCEEDED: ${self.spend:.2f} exceeds limit of ${self.limit:.2f}")
            
        return cost
