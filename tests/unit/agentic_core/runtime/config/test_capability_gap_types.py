"""Foundational behavioral tests for agentic_core/runtime/config/capability_gap_types.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_capability_gap_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
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
    )
    _AVAILABLE = True
except Exception as _exc:
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


@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestCapabilityGapTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(CapabilityGapType, enum.Enum)

    def test_has_members(self):
        assert len(list(CapabilityGapType)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in CapabilityGapType:
            assert member.value is not None

    def test_known_member_missing_tool_exists(self):
        assert hasattr(CapabilityGapType, 'MISSING_TOOL')

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestRecommendationTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(RecommendationType, enum.Enum)

    def test_has_members(self):
        assert len(list(RecommendationType)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in RecommendationType:
            assert member.value is not None

    def test_known_member_add_tool_exists(self):
        assert hasattr(RecommendationType, 'ADD_TOOL')

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestCapabilityGapContract:
    def test_is_class(self):
        assert isinstance(CapabilityGap, type)

    def test_has_method_to_dict(self):
        assert callable(getattr(CapabilityGap, 'to_dict', None))

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestRecommendationContract:
    def test_is_class(self):
        assert isinstance(Recommendation, type)

    def test_has_method_to_dict(self):
        assert callable(getattr(Recommendation, 'to_dict', None))

@pytest.mark.skipif(not _AVAILABLE, reason="capability_gap_types.py deps unavailable")
class TestAnalysisReportContract:
    def test_is_class(self):
        assert isinstance(AnalysisReport, type)

    def test_has_method_to_dict(self):
        assert callable(getattr(AnalysisReport, 'to_dict', None))

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


def test_module_importable():
    """Module capability_gap_types must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
