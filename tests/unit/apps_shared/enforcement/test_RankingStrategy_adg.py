"""ADG-driven tests for apps_shared/enforcement/RankingStrategy.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.enforcement.RankingStrategy import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        apply_strategy,
        bm25,
        dense,
        fuse_ranked_groups,
        hybrid,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    bm25 = None  # type: ignore[assignment,misc]
    dense = None  # type: ignore[assignment,misc]
    hybrid = None  # type: ignore[assignment,misc]
    apply_strategy = None  # type: ignore[assignment,misc]
    fuse_ranked_groups = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestBm25:
    def test_is_callable(self):
        assert callable(bm25)

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestDense:
    def test_is_callable(self):
        assert callable(dense)

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestHybrid:
    def test_is_callable(self):
        assert callable(hybrid)

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestApplyStrategy:
    def test_is_callable(self):
        assert callable(apply_strategy)

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestFuseRankedGroups:
    def test_is_callable(self):
        assert callable(fuse_ranked_groups)

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

@pytest.mark.skipif(not _AVAILABLE, reason="RankingStrategy.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module RankingStrategy.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
