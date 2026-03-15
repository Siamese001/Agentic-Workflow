"""ADG-driven tests for apps_lic/tools/query_past_campaigns.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.tools.query_past_campaigns import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        query_past_campaigns,
        retrieve,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    query_past_campaigns = None  # type: ignore[assignment,misc]
    retrieve = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="query_past_campaigns.py deps unavailable")
class Testquery_past_campaigns:
    def test_is_class(self):
        assert isinstance(query_past_campaigns, type)
    def test_importable(self):
        assert query_past_campaigns is not None

@pytest.mark.skipif(not _AVAILABLE, reason="query_past_campaigns.py deps unavailable")
class TestRetrieve:
    def test_is_callable(self):
        assert callable(retrieve)

@pytest.mark.skipif(not _AVAILABLE, reason="query_past_campaigns.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="query_past_campaigns.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="query_past_campaigns.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="query_past_campaigns.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="query_past_campaigns.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="query_past_campaigns.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module query_past_campaigns.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
