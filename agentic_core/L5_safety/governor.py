import logging

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)


class BudgetExceededError(Exception):
    def __init__(self, message: str, current_spend: float = None, limit: float = None):
        super().__init__(message)
        self.current_spend = current_spend
        self.LIMIT = limit


class CostGovernor:
    def __init__(self, limit_usd: float = 5.00):
        self.LIMIT = limit_usd
        self.SPEND = 0.0
        # Estimated cost per 1k tokens
        self.RATES = {"gpt-4": 0.03,
                      "gpt-3.5-turbo": 0.002, "claude-3-opus": 0.015}

    def track(self, model: str, input_tok: int, output_tok: int) -> float:
        RATE = self.RATES.get(model, 0.01)
        COST = ((input_tok + output_tok) / 1000) * RATE
        self.SPEND += COST

        if self.SPEND > self.LIMIT:
            raise BudgetExceededError(f"Global budget limit ${self.LIMIT} exceeded. Current spend: ${self.SPEND}")

        return COST