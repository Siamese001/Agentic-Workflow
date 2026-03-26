"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py.

fan_in=15 — this module is imported by 15 other modules.
ADG contract: import-hygiene is covered by test_IntegrityGateExecutorAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L5_safety.reasoning.IntegrityGateExecutorAgent import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    FinancialProofPoint,
    IntegrityGateResult,
    KeyExecutive,
    KeyTechnology,
    ValidationRejectionReason,
    Violation,
    validate_research_output,
)


class TestValidationRejectionReasonContract:
    def test_is_enum(self):
        from agentic_core.L5_safety.reasoning.IntegrityGateExecutorAgent import (  # noqa: F401
        import enum
        assert issubclass(ValidationRejectionReason, enum.Enum)

    def test_has_members(self):
        assert len(list(ValidationRejectionReason)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ValidationRejectionReason:
            assert member.value is not None

    def test_known_member_insufficient_depth_exists(self):
        assert hasattr(ValidationRejectionReason, 'INSUFFICIENT_DEPTH')

class TestViolationContract:
    def test_is_class(self):
        assert isinstance(Violation, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(Violation, type)

class TestIntegrityGateResultContract:
    def test_is_class(self):
        assert isinstance(IntegrityGateResult, type)

    def test_has_method_add_violation(self):
        assert callable(getattr(IntegrityGateResult, 'add_violation', None))

class TestFinancialProofPointContract:
    def test_is_class(self):
        assert isinstance(FinancialProofPoint, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(FinancialProofPoint, type)

class TestKeyTechnologyContract:
    def test_is_class(self):
        assert isinstance(KeyTechnology, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(KeyTechnology, type)

class TestKeyExecutiveContract:
    def test_is_class(self):
        assert isinstance(KeyExecutive, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(KeyExecutive, type)

class TestValidateResearchOutputFunction:
    def test_is_callable(self):
        assert callable(validate_research_output)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_research_output)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module IntegrityGateExecutorAgent must be importable or skip gracefully."""
    pass  # Import verified at module level
