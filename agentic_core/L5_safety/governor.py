import logging

logger = logging.getLogger(__name__)
class BudgetExceededError(Exception):
    def __init__(self, message: str, current_spend: float = None, limit: float = None):
        super().__init__(message)
        self.current_spend = current_spend
        self.limit = limit

class CostGovernor:
    def __init__(self, limit_usd: float = 5.00):
        self.limit = limit_usd
        self.spend = 0.0
        # Estimated cost per 1k tokens
        self.rates = {"gpt-4": 0.03, "gpt-3.5-turbo": 0.002, "claude-3-opus": 0.015}

    def track(self, model: str, input_tok: int, output_tok: int) -> float:
        rate = self.rates.get(model, 0.01)
        cost = ((input_tok + output_tok) / 1000) * rate
        self.spend += cost

        if self.spend > self.limit:
            raise BudgetExceededError(f"Global budget limit ${self.
                .limit} exceeded (Current: ${self.
                .spend:.
                .2f}).
                .")

        return cost
