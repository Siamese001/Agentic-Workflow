"""ADG-driven tests for L2_execution/types/vllm_token_budget_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.vllm_token_budget_types import (
    VLLM_MAX_TOKENS_DEFAULT,
    VLLM_MAX_TOKENS_EXTENDED,
    VLLM_MAX_TOKENS_ABSOLUTE,
    SAFETY_MARGIN_TOKENS,
)


class TestVllmTokenBudgetConstants:
    def test_default_is_int(self):
        assert isinstance(VLLM_MAX_TOKENS_DEFAULT, int)

    def test_extended_is_int(self):
        assert isinstance(VLLM_MAX_TOKENS_EXTENDED, int)

    def test_absolute_is_int(self):
        assert isinstance(VLLM_MAX_TOKENS_ABSOLUTE, int)

    def test_safety_margin_is_int(self):
        assert isinstance(SAFETY_MARGIN_TOKENS, int)

    def test_default_less_than_or_equal_absolute(self):
        assert VLLM_MAX_TOKENS_DEFAULT <= VLLM_MAX_TOKENS_ABSOLUTE

    def test_extended_less_than_or_equal_absolute(self):
        assert VLLM_MAX_TOKENS_EXTENDED <= VLLM_MAX_TOKENS_ABSOLUTE

    def test_safety_margin_positive(self):
        assert SAFETY_MARGIN_TOKENS > 0
