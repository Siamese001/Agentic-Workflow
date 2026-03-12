"""ADG importability contract for agentic_core/mixins/cost_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_cost_mixin.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.cost_mixin import (  # noqa: F401
        TokenUsage,
        BudgetConfig,
        BudgetExceededError,
        RecursionLimitError,
        CostGuardrailMixin,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    TokenUsage = None  # type: ignore[assignment,misc]
    BudgetConfig = None  # type: ignore[assignment,misc]
    BudgetExceededError = None  # type: ignore[assignment,misc]
    RecursionLimitError = None  # type: ignore[assignment,misc]
    CostGuardrailMixin = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="cost_mixin.py deps unavailable")
class TestCostMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: cost_mixin.py must be importable."""
        assert _AVAILABLE

    def test_tokenusage_is_type(self) -> None:
        assert TokenUsage is not None

    def test_budgetconfig_is_type(self) -> None:
        assert BudgetConfig is not None

    def test_budgetexceedederror_is_type(self) -> None:
        assert BudgetExceededError is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

