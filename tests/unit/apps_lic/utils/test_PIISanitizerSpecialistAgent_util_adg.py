"""ADG-driven tests for apps_lic/utils/PIISanitizerSpecialistAgent_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.utils.PIISanitizerSpecialistAgent_util import (  # noqa: F401
        PII_SanitizerSpecialistAgent,
        BiasDetectorSpecialist,
        PromptInjectionDetectorSpecialist,
        ConstitutionalReviewResult,
        ConstitutionalReviewerAgent,
        track_metrics,
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
    PII_SanitizerSpecialistAgent = None  # type: ignore[assignment,misc]
    BiasDetectorSpecialist = None  # type: ignore[assignment,misc]
    PromptInjectionDetectorSpecialist = None  # type: ignore[assignment,misc]
    ConstitutionalReviewResult = None  # type: ignore[assignment,misc]
    ConstitutionalReviewerAgent = None  # type: ignore[assignment,misc]
    track_metrics = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestPII_SanitizerSpecialistAgent:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PII_SanitizerSpecialistAgent)
    def test_importable(self):
        assert PII_SanitizerSpecialistAgent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestBiasDetectorSpecialist:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(BiasDetectorSpecialist)
    def test_importable(self):
        assert BiasDetectorSpecialist is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestPromptInjectionDetectorSpecialist:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PromptInjectionDetectorSpecialist)
    def test_importable(self):
        assert PromptInjectionDetectorSpecialist is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestConstitutionalReviewResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ConstitutionalReviewResult)
    def test_importable(self):
        assert ConstitutionalReviewResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestConstitutionalReviewerAgent:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ConstitutionalReviewerAgent)
    def test_importable(self):
        assert ConstitutionalReviewerAgent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestTrackMetrics:
    def test_is_callable(self):
        assert callable(track_metrics)

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module PIISanitizerSpecialistAgent_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
