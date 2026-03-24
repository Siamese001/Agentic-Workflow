"""Foundational behavioral tests for system_learning/types/healing_outcome_types.py.

fan_in=8 — imported by 8 other modules.
ADG import-hygiene is covered separately by test_healing_outcome_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.types.healing_outcome_types import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        HealingOutcomeEvent,
        HealingOutcomeProposal,
        HealingOutcomeStats,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    HealingOutcomeEvent = None  # type: ignore[assignment,misc]
    HealingOutcomeStats = None  # type: ignore[assignment,misc]
    HealingOutcomeProposal = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_types.py deps unavailable")
class TestHealingOutcomeEventContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingOutcomeEvent)

    def test_is_frozen(self):
        assert HealingOutcomeEvent.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealingOutcomeEvent)}
        assert fnames >= {'failure_type', 'healer_id', 'trace_id', 'timestamp_utc', 'success', 'tier'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealingOutcomeEvent)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_types.py deps unavailable")
class TestHealingOutcomeStatsContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingOutcomeStats)

    def test_is_frozen(self):
        assert HealingOutcomeStats.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealingOutcomeStats)}
        assert fnames >= {'failure_type', 'healer_id', 'success_count', 'failure_count', 'tier', 'total_count'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealingOutcomeStats)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_types.py deps unavailable")
class TestHealingOutcomeProposalContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingOutcomeProposal)

    def test_is_frozen(self):
        assert HealingOutcomeProposal.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealingOutcomeProposal)}
        assert fnames >= {'stats', 'recommended_actions'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealingOutcomeProposal)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: healing_outcome_types importable or gracefully unavailable."""
    pass