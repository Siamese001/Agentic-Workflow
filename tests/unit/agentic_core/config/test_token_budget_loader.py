"""Tests for token_budget_loader module."""
from __future__ import annotations

import pytest

from agentic_core.config.token_budget_loader import (
    DEFAULT_TOKEN_BUDGET,
    TokenBudgetConfig,
    load_token_budget,
)


class TestTokenBudgetConfig:
    """Test TokenBudgetConfig dataclass."""

    def test_valid_config_passes_validation(self):
        """Happy path: valid config passes validation."""
        config = TokenBudgetConfig(
            hard_max_context=262000,
            safe_operating_cap=223000,
            warning_threshold=197000,
            default_reserved_output=12000,
            default_safety_buffer=8000,
            token_rates={"code": 0.35},
        )
        # Should not raise
        config.validate()

    def test_invalid_invariants_raises(self):
        """Failure path: invalid invariants raise ValueError."""
        config = TokenBudgetConfig(
            hard_max_context=1000,
            safe_operating_cap=2000,  # safe > hard
            warning_threshold=500,
            default_reserved_output=100,
            default_safety_buffer=100,
            token_rates={},
        )
        with pytest.raises(ValueError, match="Budget invariants violated"):
            config.validate()

    def test_negative_reserved_output_raises(self):
        """Edge case: negative reserved output raises ValueError."""
        config = TokenBudgetConfig(
            hard_max_context=1000,
            safe_operating_cap=800,
            warning_threshold=600,
            default_reserved_output=-1,  # negative
            default_safety_buffer=100,
            token_rates={},
        )
        with pytest.raises(ValueError, match="Reserved output and safety buffer must be >= 0"):
            config.validate()


class TestLoadTokenBudget:
    """Test load_token_budget function."""

    def test_load_default_model(self):
        """Happy path: load default kimi_k2_5 model."""
        config = load_token_budget("kimi_k2_5")
        assert config.hard_max_context == 262000
        assert config.safe_operating_cap == 223000
        assert config.warning_threshold == 197000
        assert config.default_reserved_output == 12000
        assert config.default_safety_buffer == 8000
        assert "code" in config.token_rates

    def test_invalid_model_raises(self):
        """Failure path: invalid model name raises KeyError."""
        with pytest.raises(KeyError):
            load_token_budget("invalid_model")

    def test_default_budget_loaded(self):
        """Edge case: DEFAULT_TOKEN_BUDGET is pre-loaded."""
        assert DEFAULT_TOKEN_BUDGET.hard_max_context == 262000
        assert isinstance(DEFAULT_TOKEN_BUDGET, TokenBudgetConfig)
