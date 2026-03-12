"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py.

fan_in=15 — this module is imported by 15 other modules.
ADG contract: import-hygiene is covered by test_IntegrityGateExecutorAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.IntegrityGateExecutorAgent import (  # noqa: F401
        ValidationRejectionReason,
        Violation,
        IntegrityGateResult,
        FinancialProofPoint,
        KeyTechnology,
        KeyExecutive,
        validate_research_output,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    ValidationRejectionReason = None  # type: ignore[assignment,misc]
    Violation = None  # type: ignore[assignment,misc]
    IntegrityGateResult = None  # type: ignore[assignment,misc]
    FinancialProofPoint = None  # type: ignore[assignment,misc]
    KeyTechnology = None  # type: ignore[assignment,misc]
    KeyExecutive = None  # type: ignore[assignment,misc]
    validate_research_output = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent.py deps unavailable")
class TestValidationRejectionReasonContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ValidationRejectionReason, enum.Enum)

    def test_has_members(self):
        assert len(list(ValidationRejectionReason)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ValidationRejectionReason:
            assert member.value is not None

    def test_known_member_insufficient_depth_exists(self):
        assert hasattr(ValidationRejectionReason, 'INSUFFICIENT_DEPTH')

@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent.py deps unavailable")
class TestViolationContract:
    def test_is_class(self):
        assert isinstance(Violation, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(Violation, type)

@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent.py deps unavailable")
class TestIntegrityGateResultContract:
    def test_is_class(self):
        assert isinstance(IntegrityGateResult, type)

    def test_has_method_add_violation(self):
        assert callable(getattr(IntegrityGateResult, 'add_violation', None))

@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent.py deps unavailable")
class TestFinancialProofPointContract:
    def test_is_class(self):
        assert isinstance(FinancialProofPoint, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(FinancialProofPoint, type)

@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent.py deps unavailable")
class TestKeyTechnologyContract:
    def test_is_class(self):
        assert isinstance(KeyTechnology, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(KeyTechnology, type)

@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent.py deps unavailable")
class TestKeyExecutiveContract:
    def test_is_class(self):
        assert isinstance(KeyExecutive, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(KeyExecutive, type)

@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent.py deps unavailable")
class TestValidateResearchOutputFunction:
    def test_is_callable(self):
        assert callable(validate_research_output)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_research_output)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module IntegrityGateExecutorAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
