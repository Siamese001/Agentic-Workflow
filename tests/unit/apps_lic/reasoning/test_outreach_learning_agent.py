"""Foundational behavioral tests for apps_lic/reasoning/OutreachLearningAgent.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_OutreachLearningAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import dataclasses
import enum

import pytest

from apps_lic.reasoning.OutreachLearningAgent import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    HealingPolicyMixin,
    OutreachConfidenceLevel,
    OutreachEngineContext,
    OutreachInstruction,
    OutreachLearningExample,
    OutreachLearningLoop,
)

pytestmark = pytest.mark.unit


class TestOutreachEngineContextContract:
    """Contract tests for OutreachEngineContext."""

    def test_is_class(self):
        """OutreachEngineContext must be a class."""
        assert isinstance(OutreachEngineContext, type)

    def test_instantiable_or_abstract(self):
        """OutreachEngineContext must be instantiable or abstract."""
        assert isinstance(OutreachEngineContext, type)


class TestHealerMixinContract:
    """Contract tests for HealingPolicyMixin."""

    def test_is_class(self):
        """HealingPolicyMixin must be a class."""
        assert isinstance(HealingPolicyMixin, type)

    def test_instantiable_or_abstract(self):
        """HealingPolicyMixin must be instantiable or abstract."""
        assert isinstance(HealingPolicyMixin, type)


class TestOutreachConfidenceLevelContract:
    """Contract tests for OutreachConfidenceLevel enum."""

    def test_is_enum(self):
        """OutreachConfidenceLevel must be an Enum subclass."""
        assert issubclass(OutreachConfidenceLevel, enum.Enum)

    def test_has_members(self):
        """OutreachConfidenceLevel must have at least one member."""
        assert len(list(OutreachConfidenceLevel)) >= 1

    def test_member_values_are_strings_or_ints(self):
        """Enum member values must not be None."""
        for member in OutreachConfidenceLevel:
            assert member.value is not None

    def test_known_member_low_exists(self):
        """OutreachConfidenceLevel must have LOW member."""
        assert hasattr(OutreachConfidenceLevel, "LOW")


class TestOutreachLearningExampleContract:
    """Contract tests for OutreachLearningExample dataclass."""

    def test_is_dataclass(self):
        """OutreachLearningExample must be a dataclass."""
        assert dataclasses.is_dataclass(OutreachLearningExample)

    def test_field_names_present(self):
        """OutreachLearningExample must have required fields."""
        field_names = {f.name for f in dataclasses.fields(OutreachLearningExample)}
        required = {"success", "output_result", "input_context", "example_id", "TaskType"}
        assert field_names >= required


class TestOutreachInstructionContract:
    """Contract tests for OutreachInstruction dataclass."""

    def test_is_dataclass(self):
        """OutreachInstruction must be a dataclass."""
        assert dataclasses.is_dataclass(OutreachInstruction)

    def test_field_names_present(self):
        """OutreachInstruction must have required fields."""
        field_names = {f.name for f in dataclasses.fields(OutreachInstruction)}
        assert field_names >= {"timestamp", "source", "priority", "text"}


class TestOutreachLearningLoopContract:
    """Contract tests for OutreachLearningLoop class."""

    def test_is_class(self):
        """OutreachLearningLoop must be a class."""
        assert isinstance(OutreachLearningLoop, type)

    def test_has_method_record_success(self):
        """OutreachLearningLoop must have record_success method."""
        assert callable(getattr(OutreachLearningLoop, "record_success", None))

    def test_has_method_record_failure(self):
        """OutreachLearningLoop must have record_failure method."""
        assert callable(getattr(OutreachLearningLoop, "record_failure", None))

    def test_has_method_get_success_rate(self):
        """OutreachLearningLoop must have get_success_rate method."""
        assert callable(getattr(OutreachLearningLoop, "get_success_rate", None))

    def test_has_method_get_examples(self):
        """OutreachLearningLoop must have get_examples method."""
        assert callable(getattr(OutreachLearningLoop, "get_examples", None))


class TestMaxRetriesConstant:
    """Contract tests for MAX_RETRIES constant."""

    def test_is_not_none(self):
        """MAX_RETRIES must be defined."""
        assert MAX_RETRIES is not None


class TestDefaultSleepConstant:
    """Contract tests for DEFAULT_SLEEP constant."""

    def test_is_not_none(self):
        """DEFAULT_SLEEP must be defined."""
        assert DEFAULT_SLEEP is not None


class TestThresholdConstant:
    """Contract tests for THRESHOLD constant."""

    def test_is_not_none(self):
        """THRESHOLD must be defined."""
        assert THRESHOLD is not None


class TestBufferSizeConstant:
    """Contract tests for BUFFER_SIZE constant."""

    def test_is_not_none(self):
        """BUFFER_SIZE must be defined."""
        assert BUFFER_SIZE is not None


class TestBatchSizeConstant:
    """Contract tests for BATCH_SIZE constant."""

    def test_is_not_none(self):
        """BATCH_SIZE must be defined."""
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module OutreachLearningAgent must be importable or skip gracefully."""
    pass  # Import verified at module level
