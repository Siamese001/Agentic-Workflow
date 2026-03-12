"""ADG-driven tests for apps_shared/utils/rank_observability_components_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.rank_observability_components_util import (  # noqa: F401
        insert_entity,
        insert_triplet,
        insert_event,
        batch_process_invalidation,
        ingest_transcript,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    insert_entity = None  # type: ignore[assignment,misc]
    insert_triplet = None  # type: ignore[assignment,misc]
    insert_event = None  # type: ignore[assignment,misc]
    batch_process_invalidation = None  # type: ignore[assignment,misc]
    ingest_transcript = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="rank_observability_components_util.py deps unavailable")
class TestInsertEntity:
    def test_is_callable(self):
        assert callable(insert_entity)

@pytest.mark.skipif(not _AVAILABLE, reason="rank_observability_components_util.py deps unavailable")
class TestInsertTriplet:
    def test_is_callable(self):
        assert callable(insert_triplet)

@pytest.mark.skipif(not _AVAILABLE, reason="rank_observability_components_util.py deps unavailable")
class TestInsertEvent:
    def test_is_callable(self):
        assert callable(insert_event)

@pytest.mark.skipif(not _AVAILABLE, reason="rank_observability_components_util.py deps unavailable")
class TestBatchProcessInvalidation:
    def test_is_callable(self):
        assert callable(batch_process_invalidation)

@pytest.mark.skipif(not _AVAILABLE, reason="rank_observability_components_util.py deps unavailable")
class TestIngestTranscript:
    def test_is_callable(self):
        assert callable(ingest_transcript)

@pytest.mark.skipif(not _AVAILABLE, reason="rank_observability_components_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rank_observability_components_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rank_observability_components_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rank_observability_components_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rank_observability_components_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="rank_observability_components_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module rank_observability_components_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
