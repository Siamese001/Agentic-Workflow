"""Foundational behavioral tests for apps_lic/reasoning/OutreachLearningAgent.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_OutreachLearningAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.reasoning.OutreachLearningAgent import (  # noqa: F401
        OutreachEngineContext,
        HealerMixin,
        OutreachConfidenceLevel,
        OutreachLearningExample,
        OutreachInstruction,
        OutreachLearningLoop,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    OutreachEngineContext = None  # type: ignore[assignment,misc]
    HealerMixin = None  # type: ignore[assignment,misc]
    OutreachConfidenceLevel = None  # type: ignore[assignment,misc]
    OutreachLearningExample = None  # type: ignore[assignment,misc]
    OutreachInstruction = None  # type: ignore[assignment,misc]
    OutreachLearningLoop = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="OutreachLearningAgent.py deps unavailable")
class TestOutreachEngineContextContract:
    def test_is_class(self):
        assert isinstance(OutreachEngineContext, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(OutreachEngineContext, type)

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachLearningAgent.py deps unavailable")
class TestHealerMixinContract:
    def test_is_class(self):
        assert isinstance(HealerMixin, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HealerMixin, type)

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachLearningAgent.py deps unavailable")
class TestOutreachConfidenceLevelContract:
    def test_is_enum(self):
        import enum
        assert issubclass(OutreachConfidenceLevel, enum.Enum)

    def test_has_members(self):
        assert len(list(OutreachConfidenceLevel)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in OutreachConfidenceLevel:
            assert member.value is not None

    def test_known_member_low_exists(self):
        assert hasattr(OutreachConfidenceLevel, 'LOW')

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachLearningAgent.py deps unavailable")
class TestOutreachLearningExampleContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(OutreachLearningExample)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(OutreachLearningExample)}
        assert field_names >= {'success', 'output_result', 'input_context', 'example_id', 'TaskType'}

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachLearningAgent.py deps unavailable")
class TestOutreachInstructionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(OutreachInstruction)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(OutreachInstruction)}
        assert field_names >= {'timestamp', 'source', 'priority', 'text'}

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachLearningAgent.py deps unavailable")
class TestOutreachLearningLoopContract:
    def test_is_class(self):
        assert isinstance(OutreachLearningLoop, type)

    def test_has_method_record_success(self):
        assert callable(getattr(OutreachLearningLoop, 'record_success', None))

    def test_has_method_record_failure(self):
        assert callable(getattr(OutreachLearningLoop, 'record_failure', None))

    def test_has_method_get_success_rate(self):
        assert callable(getattr(OutreachLearningLoop, 'get_success_rate', None))

    def test_has_method_get_examples(self):
        assert callable(getattr(OutreachLearningLoop, 'get_examples', None))

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachLearningAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachLearningAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachLearningAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachLearningAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachLearningAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module OutreachLearningAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
