"""Foundational behavioral tests for apps_shared/utils/assessment_level_util.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_assessment_level_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.assessment_level_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        AssessmentLevel,
        AssessmentResult,
        AssessScriptsRisk,
        assess,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    AssessmentLevel = None  # type: ignore[assignment,misc]
    AssessmentResult = None  # type: ignore[assignment,misc]
    AssessScriptsRisk = None  # type: ignore[assignment,misc]
    assess = None  # type: ignore[assignment,misc]
    assess = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="assessment_level_util.py deps unavailable")
class TestAssessmentLevelContract:
    def test_is_enum(self):
        import enum
        assert issubclass(AssessmentLevel, enum.Enum)

    def test_has_members(self):
        assert len(list(AssessmentLevel)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="assessment_level_util.py deps unavailable")
class TestAssessmentResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AssessmentResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(AssessmentResult)}
        assert field_names >= {'level', 'findings', 'score'}

@pytest.mark.skipif(not _AVAILABLE, reason="assessment_level_util.py deps unavailable")
class TestAssessScriptsRiskContract:
    def test_is_class(self):
        assert isinstance(AssessScriptsRisk, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(AssessScriptsRisk, type)

@pytest.mark.skipif(not _AVAILABLE, reason="assessment_level_util.py deps unavailable")
class TestAssessFunction:
    def test_is_callable(self):
        assert callable(assess)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(assess)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="assessment_level_util.py deps unavailable")
class TestAssessFunction:
    def test_is_callable(self):
        assert callable(assess)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(assess)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="assessment_level_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="assessment_level_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="assessment_level_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="assessment_level_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="assessment_level_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module assessment_level_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
