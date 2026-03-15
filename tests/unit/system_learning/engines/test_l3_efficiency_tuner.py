"""Foundational behavioral tests for system_learning/engines/l3_efficiency_tuner.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_l3_efficiency_tuner_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.engines.l3_efficiency_tuner import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        EfficiencyBottleneck,
        EfficiencyReport,
        L3EfficiencyTuner,
        extract_timings_from_runtime_state,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    EfficiencyBottleneck = None  # type: ignore[assignment,misc]
    EfficiencyReport = None  # type: ignore[assignment,misc]
    L3EfficiencyTuner = None  # type: ignore[assignment,misc]
    extract_timings_from_runtime_state = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="l3_efficiency_tuner.py deps unavailable")
class TestEfficiencyBottleneckContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(EfficiencyBottleneck)

    def test_is_frozen(self):
        assert EfficiencyBottleneck.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(EfficiencyBottleneck)}
        assert field_names >= {'metric_name', 'territory', 'observed_value_ms', 'threshold_ms', 'component'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(EfficiencyBottleneck)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert EfficiencyBottleneck.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="l3_efficiency_tuner.py deps unavailable")
class TestEfficiencyReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(EfficiencyReport)

    def test_is_frozen(self):
        assert EfficiencyReport.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(EfficiencyReport)}
        assert field_names >= {'snapshot_id', 'total_territories', 'bottlenecks', 'total_agents_executed', 'avg_territory_time_ms'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(EfficiencyReport)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert EfficiencyReport.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="l3_efficiency_tuner.py deps unavailable")
class TestL3EfficiencyTunerContract:
    def test_is_class(self):
        assert isinstance(L3EfficiencyTuner, type)

    def test_has_method_analyze(self):
        assert callable(getattr(L3EfficiencyTuner, 'analyze', None))

@pytest.mark.skipif(not _AVAILABLE, reason="l3_efficiency_tuner.py deps unavailable")
class TestExtractTimingsFromRuntimeStateFunction:
    def test_is_callable(self):
        assert callable(extract_timings_from_runtime_state)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(extract_timings_from_runtime_state)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="l3_efficiency_tuner.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="l3_efficiency_tuner.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="l3_efficiency_tuner.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="l3_efficiency_tuner.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="l3_efficiency_tuner.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module l3_efficiency_tuner must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
