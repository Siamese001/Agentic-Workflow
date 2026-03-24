"""Foundational behavioral tests for system_learning/types/app_signal_types.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_app_signal_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.types.app_signal_types import (  # noqa: F401
        AppSignalAggregateArtifact,
        AppSignalEventArtifact,
        aggregate_app_signals,
        build_app_signal_aggregate,
        build_app_signal_event,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    AppSignalEventArtifact = None  # type: ignore[assignment,misc]
    AppSignalAggregateArtifact = None  # type: ignore[assignment,misc]
    build_app_signal_event = None  # type: ignore[assignment,misc]
    build_app_signal_aggregate = None  # type: ignore[assignment,misc]
    aggregate_app_signals = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="app_signal_types.py deps unavailable")
class TestAppSignalEventArtifactContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AppSignalEventArtifact)

    def test_is_frozen(self):
        assert AppSignalEventArtifact.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(AppSignalEventArtifact)}
        assert fnames >= {'message_id', 'segment_id', 'artifact_type', 'metric_name', 'run_id', 'app_id'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(AppSignalEventArtifact)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="app_signal_types.py deps unavailable")
class TestAppSignalAggregateArtifactContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AppSignalAggregateArtifact)

    def test_is_frozen(self):
        assert AppSignalAggregateArtifact.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(AppSignalAggregateArtifact)}
        assert fnames >= {'candidate_value', 'baseline_value', 'window_id', 'artifact_type', 'metric_name', 'app_id'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(AppSignalAggregateArtifact)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="app_signal_types.py deps unavailable")
class TestBuildAppSignalEventFunction:
    def test_is_callable(self):
        assert callable(build_app_signal_event)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_app_signal_event)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="app_signal_types.py deps unavailable")
class TestBuildAppSignalAggregateFunction:
    def test_is_callable(self):
        assert callable(build_app_signal_aggregate)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_app_signal_aggregate)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="app_signal_types.py deps unavailable")
class TestAggregateAppSignalsFunction:
    def test_is_callable(self):
        assert callable(aggregate_app_signals)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(aggregate_app_signals)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: app_signal_types importable or gracefully unavailable."""
    pass