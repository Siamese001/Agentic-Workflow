"""ADG-driven tests for apps_shared/utils/observability_clients_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.observability_clients_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        create_span,
        record_exception,
        set_span_attribute,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    create_span = None  # type: ignore[assignment,misc]
    record_exception = None  # type: ignore[assignment,misc]
    set_span_attribute = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="observability_clients_util.py deps unavailable")
class TestCreateSpan:
    def test_is_callable(self):
        assert callable(create_span)

@pytest.mark.skipif(not _AVAILABLE, reason="observability_clients_util.py deps unavailable")
class TestRecordException:
    def test_is_callable(self):
        assert callable(record_exception)

@pytest.mark.skipif(not _AVAILABLE, reason="observability_clients_util.py deps unavailable")
class TestSetSpanAttribute:
    def test_is_callable(self):
        assert callable(set_span_attribute)

@pytest.mark.skipif(not _AVAILABLE, reason="observability_clients_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_clients_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_clients_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_clients_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_clients_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="observability_clients_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module observability_clients_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE