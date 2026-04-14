"""Token budget loader - loads from YAML SSOT."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "token_budget.yaml"


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
        if not (0 < self.warning_threshold <= self.safe_operating_cap <= self.hard_max_context):
            raise ValueError(
                "Budget invariants violated: WARNING_THRESHOLD <= SAFE_OPERATING_CAP <= HARD_MAX_CONTEXT"
            )
        if self.default_reserved_output < 0 or self.default_safety_buffer < 0:
            raise ValueError("Reserved output and safety buffer must be >= 0")


@lru_cache(maxsize=1)
def _load_raw_config() -> dict:
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(f"Token budget config not found: {CONFIG_PATH}")
    with CONFIG_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict) or not isinstance(data.get("models"), dict):
        raise ValueError(f"Token budget file must contain a top-level 'models' mapping: {CONFIG_PATH}")
    return data


def load_token_budget(model: str = "kimi_k2_5") -> TokenBudgetConfig:
    data = _load_raw_config()
    try:
        model_data = data["models"][model]
    except KeyError as exc:
        raise KeyError(f"Unknown token budget model '{model}' in {CONFIG_PATH}") from exc
    if not isinstance(model_data, dict):
        raise ValueError(f"Token budget entry for '{model}' must be a mapping")
    config = TokenBudgetConfig(**model_data)
    config.validate()
    return config


def get_default_token_budget() -> TokenBudgetConfig:
    return load_token_budget("kimi_k2_5")


__all__ = [
    "TokenBudgetConfig",
    "load_token_budget",
    "get_default_token_budget",
]
