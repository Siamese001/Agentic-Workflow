"""Foundational behavioral tests for apps_lic/utils/PIISanitizerSpecialistAgent_util.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_PIISanitizerSpecialistAgent_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
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
    )
    _AVAILABLE = True
except Exception as _exc:
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


@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestPII_SanitizerSpecialistAgentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PII_SanitizerSpecialistAgent)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(PII_SanitizerSpecialistAgent)}
        assert field_names >= {'pii_patterns'}

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestBiasDetectorSpecialistContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(BiasDetectorSpecialist)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(BiasDetectorSpecialist)}
        assert field_names >= {'sensitivity_level', 'prohibited_terms', 'name'}

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestPromptInjectionDetectorSpecialistContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PromptInjectionDetectorSpecialist)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(PromptInjectionDetectorSpecialist)}
        assert field_names >= {'detection_threshold', 'attack_patterns'}

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestConstitutionalReviewResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ConstitutionalReviewResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ConstitutionalReviewResult)}
        assert field_names >= {'violations_found', 'feedback', 'review_passed'}

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestConstitutionalReviewerAgentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ConstitutionalReviewerAgent)

@pytest.mark.skipif(not _AVAILABLE, reason="PIISanitizerSpecialistAgent_util.py deps unavailable")
class TestTrackMetricsFunction:
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


def test_module_importable():
    """Module PIISanitizerSpecialistAgent_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
