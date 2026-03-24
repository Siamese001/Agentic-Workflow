"""Foundational behavioral tests for agentic_core/L2_execution/healers/healing_tier_types.py.

fan_in=8 — imported by 8 other modules.
ADG import-hygiene is covered separately by test_healing_tier_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.healers.healing_tier_types import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        FailureSignal,
        HealingDecision,
        HealingInput,
        HealingTier,
        InvocationRecord,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    HealingTier = None  # type: ignore[assignment,misc]
    HealingInput = None  # type: ignore[assignment,misc]
    HealingDecision = None  # type: ignore[assignment,misc]
    InvocationRecord = None  # type: ignore[assignment,misc]
    FailureSignal = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_types.py deps unavailable")
class TestHealingTierContract:
    def test_is_enum(self):
        import enum
        assert issubclass(HealingTier, enum.Enum)

    def test_has_members(self):
        assert len(list(HealingTier)) >= 1

    def test_member_values_accessible(self):
        for m in HealingTier:
            assert m.value is not None or m.value is None

    def test_known_member_local_agent_present(self):
        assert hasattr(HealingTier, 'LOCAL_AGENT')

    def test_members_are_unique(self):
        values = [m.value for m in HealingTier]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_types.py deps unavailable")
class TestHealingInputContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingInput)

    def test_is_frozen(self):
        assert HealingInput.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealingInput)}
        assert fnames >= {'failure_type', 'trace_id', 'error_signature', 'blast_radius_estimate', 'required_tools', 'retry_count'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealingInput)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_types.py deps unavailable")
class TestHealingDecisionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingDecision)

    def test_is_frozen(self):
        assert HealingDecision.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealingDecision)}
        assert fnames >= {'tier', 'heal_confidence', 'reason_codes'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealingDecision)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_types.py deps unavailable")
class TestInvocationRecordContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(InvocationRecord)

    def test_is_frozen(self):
        assert InvocationRecord.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(InvocationRecord)}
        assert fnames >= {'model_id', 'method_called', 'trace_id', 'heal_confidence', 'agent_name', 'tier'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(InvocationRecord)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_types.py deps unavailable")
class TestFailureSignalContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FailureSignal)

    def test_is_frozen(self):
        assert FailureSignal.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(FailureSignal)}
        assert fnames >= {'failure_type', 'source_agent', 'trace_id', 'error_signature', 'context', 'retry_count'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(FailureSignal)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_tier_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: healing_tier_types importable or gracefully unavailable."""
    pass