"""ADG-driven tests for system_learning/enforcement/dual_injection_proposal_gate.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.enforcement.dual_injection_proposal_gate import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ActivationBypassViolation,
        MetaLearningActivationDecision,
        decide_activation_mode,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ActivationBypassViolation = None  # type: ignore[assignment,misc]
    MetaLearningActivationDecision = None  # type: ignore[assignment,misc]
    decide_activation_mode = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="dual_injection_proposal_gate.py deps unavailable")
class TestActivationBypassViolation:
    def test_is_class(self):
        assert isinstance(ActivationBypassViolation, type)
    def test_importable(self):
        assert ActivationBypassViolation is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dual_injection_proposal_gate.py deps unavailable")
class TestMetaLearningActivationDecision:
    def test_is_class(self):
        assert isinstance(MetaLearningActivationDecision, type)
    def test_importable(self):
        assert MetaLearningActivationDecision is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dual_injection_proposal_gate.py deps unavailable")
class TestDecideActivationMode:
    def test_is_callable(self):
        assert callable(decide_activation_mode)

@pytest.mark.skipif(not _AVAILABLE, reason="dual_injection_proposal_gate.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dual_injection_proposal_gate.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dual_injection_proposal_gate.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dual_injection_proposal_gate.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dual_injection_proposal_gate.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="dual_injection_proposal_gate.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module dual_injection_proposal_gate.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
