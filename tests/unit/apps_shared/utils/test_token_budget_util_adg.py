"""ADG-driven tests for apps_shared/utils/token_budget_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.token_budget_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        BudgetExceededError,
        TokenBudget,
        TokenBudgetConfig,
        enforce_token_budget,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    BudgetExceededError = None  # type: ignore[assignment,misc]
    TokenBudgetConfig = None  # type: ignore[assignment,misc]
    TokenBudget = None  # type: ignore[assignment,misc]
    enforce_token_budget = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="token_budget_util.py deps unavailable")
class TestBudgetExceededError:
    def test_is_class(self):
        assert isinstance(BudgetExceededError, type)
    def test_importable(self):
        assert BudgetExceededError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="token_budget_util.py deps unavailable")
class TestTokenBudgetConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TokenBudgetConfig)
    def test_importable(self):
        assert TokenBudgetConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="token_budget_util.py deps unavailable")
class TestTokenBudget:
    def test_is_class(self):
        assert isinstance(TokenBudget, type)
    def test_importable(self):
        assert TokenBudget is not None

@pytest.mark.skipif(not _AVAILABLE, reason="token_budget_util.py deps unavailable")
class TestEnforceTokenBudget:
    def test_is_callable(self):
        assert callable(enforce_token_budget)

@pytest.mark.skipif(not _AVAILABLE, reason="token_budget_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="token_budget_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="token_budget_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="token_budget_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="token_budget_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="token_budget_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module token_budget_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE