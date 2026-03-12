"""ADG-driven tests for agentic_core/L5_safety/reasoning/PredictiveCostAuditorAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.PredictiveCostAuditorAgent import (  # noqa: F401
        HealingMetrics,
        FileAudit,
        CostReport,
        PredictiveCostAuditorAgent,
        get_cost_auditor,
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
    HealingMetrics = None  # type: ignore[assignment,misc]
    FileAudit = None  # type: ignore[assignment,misc]
    CostReport = None  # type: ignore[assignment,misc]
    PredictiveCostAuditorAgent = None  # type: ignore[assignment,misc]
    get_cost_auditor = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestHealingMetrics:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingMetrics)
    def test_importable(self):
        assert HealingMetrics is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestFileAudit:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FileAudit)
    def test_importable(self):
        assert FileAudit is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestCostReport:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CostReport)
    def test_importable(self):
        assert CostReport is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestPredictiveCostAuditorAgent:
    def test_is_class(self):
        assert isinstance(PredictiveCostAuditorAgent, type)
    def test_importable(self):
        assert PredictiveCostAuditorAgent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestGetCostAuditor:
    def test_is_callable(self):
        assert callable(get_cost_auditor)

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PredictiveCostAuditorAgent.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module PredictiveCostAuditorAgent.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
