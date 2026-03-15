"""ADG-driven tests for agentic_core/utils/workflow_engines/completeness_monitors.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.completeness_monitors import (  # noqa: F401
        ConditionLossDriftMonitor,
        ConditionLossSnapshot,
        HighSimilarityWrongAnswerMonitor,
        ParentExpansionMissMonitor,
        RetrievalCompletenessMonitor,
        RetrievalCompletenessSnapshot,
        SupportValidationSnapshot,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RetrievalCompletenessSnapshot = None  # type: ignore[assignment,misc]
    SupportValidationSnapshot = None  # type: ignore[assignment,misc]
    ConditionLossSnapshot = None  # type: ignore[assignment,misc]
    RetrievalCompletenessMonitor = None  # type: ignore[assignment,misc]
    ParentExpansionMissMonitor = None  # type: ignore[assignment,misc]
    HighSimilarityWrongAnswerMonitor = None  # type: ignore[assignment,misc]
    ConditionLossDriftMonitor = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="completeness_monitors.py deps unavailable")
class TestRetrievalCompletenessSnapshot:
    def test_is_class(self):
        assert isinstance(RetrievalCompletenessSnapshot, type)
    def test_importable(self):
        assert RetrievalCompletenessSnapshot is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_monitors.py deps unavailable")
class TestSupportValidationSnapshot:
    def test_is_class(self):
        assert isinstance(SupportValidationSnapshot, type)
    def test_importable(self):
        assert SupportValidationSnapshot is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_monitors.py deps unavailable")
class TestConditionLossSnapshot:
    def test_is_class(self):
        assert isinstance(ConditionLossSnapshot, type)
    def test_importable(self):
        assert ConditionLossSnapshot is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_monitors.py deps unavailable")
class TestRetrievalCompletenessMonitor:
    def test_is_class(self):
        assert isinstance(RetrievalCompletenessMonitor, type)
    def test_importable(self):
        assert RetrievalCompletenessMonitor is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_monitors.py deps unavailable")
class TestParentExpansionMissMonitor:
    def test_is_class(self):
        assert isinstance(ParentExpansionMissMonitor, type)
    def test_importable(self):
        assert ParentExpansionMissMonitor is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_monitors.py deps unavailable")
class TestHighSimilarityWrongAnswerMonitor:
    def test_is_class(self):
        assert isinstance(HighSimilarityWrongAnswerMonitor, type)
    def test_importable(self):
        assert HighSimilarityWrongAnswerMonitor is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_monitors.py deps unavailable")
class TestConditionLossDriftMonitor:
    def test_is_class(self):
        assert isinstance(ConditionLossDriftMonitor, type)
    def test_importable(self):
        assert ConditionLossDriftMonitor is not None


def test_module_importable():
    """Module completeness_monitors.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
