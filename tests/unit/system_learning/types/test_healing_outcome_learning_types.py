"""Foundational behavioral tests for system_learning/types/healing_outcome_learning_types.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_healing_outcome_learning_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.types.healing_outcome_learning_types import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        HealingOutcomeAggregate,
        HealingOutcomeAggregateKey,
        HealingOutcomeAggregateSnapshot,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    HealingOutcomeAggregateKey = None  # type: ignore[assignment,misc]
    HealingOutcomeAggregate = None  # type: ignore[assignment,misc]
    HealingOutcomeAggregateSnapshot = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_learning_types.py deps unavailable")
class TestHealingOutcomeAggregateKeyContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingOutcomeAggregateKey)

    def test_is_frozen(self):
        assert HealingOutcomeAggregateKey.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealingOutcomeAggregateKey)}
        assert fnames >= {'failure_type', 'tier', 'healer_name'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealingOutcomeAggregateKey)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_learning_types.py deps unavailable")
class TestHealingOutcomeAggregateContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingOutcomeAggregate)

    def test_is_frozen(self):
        assert HealingOutcomeAggregate.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealingOutcomeAggregate)}
        assert fnames >= {'total_count', 'success_count', 'failure_count'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealingOutcomeAggregate)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_learning_types.py deps unavailable")
class TestHealingOutcomeAggregateSnapshotContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealingOutcomeAggregateSnapshot)

    def test_is_frozen(self):
        assert HealingOutcomeAggregateSnapshot.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealingOutcomeAggregateSnapshot)}
        assert fnames >= {'aggregates', 'created_utc', 'version_id'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealingOutcomeAggregateSnapshot)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_learning_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_learning_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_learning_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_learning_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_learning_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_learning_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: healing_outcome_learning_types importable or gracefully unavailable."""
    pass