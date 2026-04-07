"""Token budget loader — loads from YAML SSOT."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class TokenBudgetConfig:
    """Token budget configuration for a specific model."""
    hard_max_context: int
    safe_operating_cap: int
    warning_threshold: int
    default_reserved_output: int
    default_safety_buffer: int
    token_rates: dict[str, float]

    def validate(self) -> None:
        """Validate budget invariants."""
        if not (0 < self.warning_threshold <= self.safe_operating_cap <= self.hard_max_context):
            raise ValueError("Budget invariants violated: WARNING_THRESHOLD <= SAFE_OPERATING_CAP <= HARD_MAX_CONTEXT")
        if self.default_reserved_output < 0 or self.default_safety_buffer < 0:
            raise ValueError("Reserved output and safety buffer must be >= 0")


def load_token_budget(model: str = "kimi_k2_5") -> TokenBudgetConfig:
    """Load token budget configuration from YAML."""
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "token_budget.yaml"

    with open(config_path) as f:
        data = yaml.safe_load(f)

    model_data = data["models"][model]
    config = TokenBudgetConfig(**model_data)
    config.validate()
    return config


# Default instance for backward compatibility
DEFAULT_TOKEN_BUDGET = load_token_budget("kimi_k2_5")


__all__ = [
    "TokenBudgetConfig",
    "load_token_budget",
    "DEFAULT_TOKEN_BUDGET",
]
