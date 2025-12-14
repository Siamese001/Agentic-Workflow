import logging

LOGGER = logging.getLogger(__name__)
class BudgetExceededError(Exception):
    def __init__(self, message: str, current_spend: float = None, limit: float = None):
        super().__init__(message)
        self.current_spend = current_spend
        SELF.LIMIT = limit

class CostGovernor:
    def __init__(self, limit_usd: float = 5.00):
        SELF.LIMIT = limit_usd
        SELF.SPEND = 0.0
        # Estimated cost per 1k tokens
        SELF.RATES = {"gpt-4": 0.03, "gpt-3.5-turbo": 0.002, "claude-3-opus": 0.015}

    def track(self, model: str, input_tok: int, output_tok: int) -> float:
        RATE = self.rates.get(model, 0.01)
        COST = ((input_tok + output_tok) / 1000) * rate
        SELF.SPEND += cost

        if self.spend > self.limit:
            raise BudgetExceededError(f"Global budget limit ${self.
                .limit} exceeded (Current: ${self.
                .spend:.
                .2f}).
                .")

        return cost
