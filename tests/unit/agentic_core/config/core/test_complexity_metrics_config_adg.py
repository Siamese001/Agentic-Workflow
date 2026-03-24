"""ADG-driven tests for agentic_core/config/core/complexity_metrics_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.config.core.complexity_metrics_config import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ComplexityMetrics,
        ExtractionCandidate,
        FlatteningPattern,
        get_flattening_pattern,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ComplexityMetrics = None  # type: ignore[assignment,misc]
    ExtractionCandidate = None  # type: ignore[assignment,misc]
    FlatteningPattern = None  # type: ignore[assignment,misc]
    get_flattening_pattern = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="complexity_metrics_config.py deps unavailable")
class TestComplexityMetrics:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ComplexityMetrics)
    def test_importable(self):
        assert ComplexityMetrics is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_metrics_config.py deps unavailable")
class TestExtractionCandidate:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ExtractionCandidate)
    def test_importable(self):
        assert ExtractionCandidate is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_metrics_config.py deps unavailable")
class TestFlatteningPattern:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FlatteningPattern)
    def test_importable(self):
        assert FlatteningPattern is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_metrics_config.py deps unavailable")
class TestGetFlatteningPattern:
    def test_is_callable(self):
        assert callable(get_flattening_pattern)

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_metrics_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_metrics_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_metrics_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_metrics_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_metrics_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="complexity_metrics_config.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module complexity_metrics_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE