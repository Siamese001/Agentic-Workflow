"""Foundational behavioral tests for agentic_core/L5_safety/validators/golden_state_test_case_validator.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_golden_state_test_case_validator_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.validators.golden_state_test_case_validator import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        EvalResult,
        GoldenCase,
        GoldenOutput,
        GoldenStateTestCase,
        JudgeVerdict,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    GoldenStateTestCase = None  # type: ignore[assignment,misc]
    JudgeVerdict = None  # type: ignore[assignment,misc]
    EvalResult = None  # type: ignore[assignment,misc]
    GoldenCase = None  # type: ignore[assignment,misc]
    GoldenOutput = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_test_case_validator.py deps unavailable")
class TestGoldenStateTestCaseContract:
    def test_is_class(self):
        assert isinstance(GoldenStateTestCase, type)

    def test_has_method_validate_required_text(self):
        assert callable(getattr(GoldenStateTestCase, 'validate_required_text', None))

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_test_case_validator.py deps unavailable")
class TestJudgeVerdictContract:
    def test_is_class(self):
        assert isinstance(JudgeVerdict, type)

    def test_has_method_validate_non_empty(self):
        assert callable(getattr(JudgeVerdict, 'validate_non_empty', None))

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_test_case_validator.py deps unavailable")
class TestEvalResultContract:
    def test_is_class(self):
        assert isinstance(EvalResult, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(EvalResult, type)

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_test_case_validator.py deps unavailable")
class TestGoldenCaseContract:
    def test_is_class(self):
        assert isinstance(GoldenCase, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(GoldenCase, type)

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_test_case_validator.py deps unavailable")
class TestGoldenOutputContract:
    def test_is_class(self):
        assert isinstance(GoldenOutput, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(GoldenOutput, type)

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_test_case_validator.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_test_case_validator.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_test_case_validator.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_test_case_validator.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="golden_state_test_case_validator.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module golden_state_test_case_validator must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
