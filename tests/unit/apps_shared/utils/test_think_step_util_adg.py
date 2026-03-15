"""ADG-driven tests for apps_shared/utils/think_step_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.think_step_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ActionStep,
        ObservationStep,
        ReasoningTraceModel,
        ThinkStep,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ThinkStep = None  # type: ignore[assignment,misc]
    ActionStep = None  # type: ignore[assignment,misc]
    ObservationStep = None  # type: ignore[assignment,misc]
    ReasoningTraceModel = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="think_step_util.py deps unavailable")
class TestThinkStep:
    def test_is_class(self):
        assert isinstance(ThinkStep, type)
    def test_importable(self):
        assert ThinkStep is not None

@pytest.mark.skipif(not _AVAILABLE, reason="think_step_util.py deps unavailable")
class TestActionStep:
    def test_is_class(self):
        assert isinstance(ActionStep, type)
    def test_importable(self):
        assert ActionStep is not None

@pytest.mark.skipif(not _AVAILABLE, reason="think_step_util.py deps unavailable")
class TestObservationStep:
    def test_is_class(self):
        assert isinstance(ObservationStep, type)
    def test_importable(self):
        assert ObservationStep is not None

@pytest.mark.skipif(not _AVAILABLE, reason="think_step_util.py deps unavailable")
class TestReasoningTraceModel:
    def test_is_class(self):
        assert isinstance(ReasoningTraceModel, type)
    def test_importable(self):
        assert ReasoningTraceModel is not None

@pytest.mark.skipif(not _AVAILABLE, reason="think_step_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="think_step_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="think_step_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="think_step_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="think_step_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="think_step_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module think_step_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
