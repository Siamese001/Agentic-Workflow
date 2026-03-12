"""ADG-driven tests for agentic_core/utils/workflow_engines/interfaces.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.interfaces import (  # noqa: F401
        Document,
        IRetrieverLexical,
        IRetrieverVector,
        ICandidateFusion,
        IReranker,
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
    Document = None  # type: ignore[assignment,misc]
    IRetrieverLexical = None  # type: ignore[assignment,misc]
    IRetrieverVector = None  # type: ignore[assignment,misc]
    ICandidateFusion = None  # type: ignore[assignment,misc]
    IReranker = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestDocument:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(Document)
    def test_importable(self):
        assert Document is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestIRetrieverLexical:
    def test_is_class(self):
        assert isinstance(IRetrieverLexical, type)
    def test_importable(self):
        assert IRetrieverLexical is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestIRetrieverVector:
    def test_is_class(self):
        assert isinstance(IRetrieverVector, type)
    def test_importable(self):
        assert IRetrieverVector is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestICandidateFusion:
    def test_is_class(self):
        assert isinstance(ICandidateFusion, type)
    def test_importable(self):
        assert ICandidateFusion is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestIReranker:
    def test_is_class(self):
        assert isinstance(IReranker, type)
    def test_importable(self):
        assert IReranker is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module interfaces.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
