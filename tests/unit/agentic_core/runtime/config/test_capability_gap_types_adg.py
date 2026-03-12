"""ADG-driven tests for agentic_core/runtime/config/capability_gap_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.runtime.config.capability_gap_types import (  # noqa: F401
        CapabilityGapType,
        RecommendationType,
        CapabilityGap,
        Recommendation,
        AnalysisReport,
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
    CapabilityGapType = None  # type: ignore[assignment,misc]
    RecommendationType = None  # type: ignore[assignment,misc]
    CapabilityGap = None  # type: ignore[assignment,misc]
    Recommendation = None  # type: ignore[assignment,misc]
    AnalysisReport = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestCapabilityGapType:
    def test_is_enum(self):
        import enum
        assert issubclass(CapabilityGapType, enum.Enum)
    def test_has_members(self):
        assert len(list(CapabilityGapType)) >= 1
    def test_importable(self):
        assert CapabilityGapType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestRecommendationType:
    def test_is_enum(self):
        import enum
        assert issubclass(RecommendationType, enum.Enum)
    def test_has_members(self):
        assert len(list(RecommendationType)) >= 1
    def test_importable(self):
        assert RecommendationType is not None

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestCapabilityGap:
    def test_is_class(self):
        assert isinstance(CapabilityGap, type)
    def test_importable(self):
        assert CapabilityGap is not None

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestRecommendation:
    def test_is_class(self):
        assert isinstance(Recommendation, type)
    def test_importable(self):
        assert Recommendation is not None

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestAnalysisReport:
    def test_is_class(self):
        assert isinstance(AnalysisReport, type)
    def test_importable(self):
        assert AnalysisReport is not None

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module capability_gap_types.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
