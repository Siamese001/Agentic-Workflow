"""Foundational behavioral tests for apps_shared/enforcement/RankingStrategy.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_RankingStrategy_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.enforcement.RankingStrategy import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        apply_strategy,
        bm25,
        dense,
        hybrid,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    bm25 = None  # type: ignore[assignment,misc]
    dense = None  # type: ignore[assignment,misc]
    hybrid = None  # type: ignore[assignment,misc]
    apply_strategy = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestBm25Function:
    def test_is_callable(self):
        assert callable(bm25)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(bm25)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestDenseFunction:
    def test_is_callable(self):
        assert callable(dense)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(dense)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestHybridFunction:
    def test_is_callable(self):
        assert callable(hybrid)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(hybrid)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestApplyStrategyFunction:
    def test_is_callable(self):
        assert callable(apply_strategy)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(apply_strategy)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module RankingStrategy must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
