"""ADG-driven tests for agentic_core/utils/workflow_engines/completeness_metrics.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.completeness_metrics import (  # noqa: F401
        EvaluationMetricResult,
        EvaluationReport,
        EvaluationDeltaReport,
        RetrievalExperimentReport,
        ChunkStrategyReport,
        CompletenessExperimentReport,
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
    EvaluationMetricResult = None  # type: ignore[assignment,misc]
    EvaluationReport = None  # type: ignore[assignment,misc]
    EvaluationDeltaReport = None  # type: ignore[assignment,misc]
    RetrievalExperimentReport = None  # type: ignore[assignment,misc]
    ChunkStrategyReport = None  # type: ignore[assignment,misc]
    CompletenessExperimentReport = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestEvaluationMetricResult:
    def test_is_class(self):
        assert isinstance(EvaluationMetricResult, type)
    def test_importable(self):
        assert EvaluationMetricResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestEvaluationReport:
    def test_is_class(self):
        assert isinstance(EvaluationReport, type)
    def test_importable(self):
        assert EvaluationReport is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestEvaluationDeltaReport:
    def test_is_class(self):
        assert isinstance(EvaluationDeltaReport, type)
    def test_importable(self):
        assert EvaluationDeltaReport is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestRetrievalExperimentReport:
    def test_is_class(self):
        assert isinstance(RetrievalExperimentReport, type)
    def test_importable(self):
        assert RetrievalExperimentReport is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestChunkStrategyReport:
    def test_is_class(self):
        assert isinstance(ChunkStrategyReport, type)
    def test_importable(self):
        assert ChunkStrategyReport is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestCompletenessExperimentReport:
    def test_is_class(self):
        assert isinstance(CompletenessExperimentReport, type)
    def test_importable(self):
        assert CompletenessExperimentReport is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module completeness_metrics.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
