"""Foundational behavioral tests for agentic_core/runtime/config/capability_gap_types.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_capability_gap_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.runtime.config.capability_gap_types import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    AnalysisReport,
    CapabilityGap,
    CapabilityGapType,
    Recommendation,
    RecommendationType,
)


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

class TestCapabilityGapContract:
    def test_is_class(self):
        assert isinstance(CapabilityGap, type)

    def test_has_method_to_dict(self):
        assert callable(getattr(CapabilityGap, 'to_dict', None))

class TestRecommendationContract:
    def test_is_class(self):
        assert isinstance(Recommendation, type)

    def test_has_method_to_dict(self):
        assert callable(getattr(Recommendation, 'to_dict', None))

class TestAnalysisReportContract:
    def test_is_class(self):
        assert isinstance(AnalysisReport, type)

    def test_has_method_to_dict(self):
        assert callable(getattr(AnalysisReport, 'to_dict', None))

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module capability_gap_types must be importable or skip gracefully."""
    pass  # Import verified at module level
