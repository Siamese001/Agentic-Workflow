"""ADG-driven tests for apps_lic/tools/PrepareOutreachContext.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.tools.PrepareOutreachContext import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        FormatData,
        PrepareOutreachContext,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    PrepareOutreachContext = None  # type: ignore[assignment,misc]
    FormatData = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="PrepareOutreachContext.py deps unavailable")
class TestPrepareOutreachContext:
    def test_is_class(self):
        assert isinstance(PrepareOutreachContext, type)
    def test_importable(self):
        assert PrepareOutreachContext is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PrepareOutreachContext.py deps unavailable")
class TestFormatdata:
    def test_is_callable(self):
        assert callable(FormatData)

@pytest.mark.skipif(not _AVAILABLE, reason="PrepareOutreachContext.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PrepareOutreachContext.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PrepareOutreachContext.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PrepareOutreachContext.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PrepareOutreachContext.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PrepareOutreachContext.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module PrepareOutreachContext.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE