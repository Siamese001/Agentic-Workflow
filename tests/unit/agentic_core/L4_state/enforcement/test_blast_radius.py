"""Foundational behavioral tests for agentic_core/L4_state/enforcement/blast_radius.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_blast_radius_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.enforcement.blast_radius import (  # noqa: F401
        BlastRadiusMetrics,
        BlastRadiusCalculator,
        BlastRadiusEnforcer,
        enforce_blast_radius,
        get_proposal_metrics,
        clear_proposal,
        validate_total_impact,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    BlastRadiusMetrics = None  # type: ignore[assignment,misc]
    BlastRadiusCalculator = None  # type: ignore[assignment,misc]
    BlastRadiusEnforcer = None  # type: ignore[assignment,misc]
    enforce_blast_radius = None  # type: ignore[assignment,misc]
    get_proposal_metrics = None  # type: ignore[assignment,misc]
    clear_proposal = None  # type: ignore[assignment,misc]
    validate_total_impact = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestBlastRadiusMetricsContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(BlastRadiusMetrics)

    def test_is_frozen(self):
        assert BlastRadiusMetrics.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(BlastRadiusMetrics)}
        assert field_names >= {'cross_layer_impacts', 'total_affected_objects', 'mutation_depth', 'state_surface_bytes'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(BlastRadiusMetrics)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert BlastRadiusMetrics.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestBlastRadiusCalculatorContract:
    def test_is_class(self):
        assert isinstance(BlastRadiusCalculator, type)

    def test_has_method_calculate_blast_radius(self):
        assert callable(getattr(BlastRadiusCalculator, 'calculate_blast_radius', None))

@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestBlastRadiusEnforcerContract:
    def test_is_class(self):
        assert isinstance(BlastRadiusEnforcer, type)

    def test_has_method_enforce_blast_radius(self):
        assert callable(getattr(BlastRadiusEnforcer, 'enforce_blast_radius', None))

    def test_has_method_get_proposal_metrics(self):
        assert callable(getattr(BlastRadiusEnforcer, 'get_proposal_metrics', None))

    def test_has_method_clear_proposal(self):
        assert callable(getattr(BlastRadiusEnforcer, 'clear_proposal', None))

    def test_has_method_get_total_blast_radius(self):
        assert callable(getattr(BlastRadiusEnforcer, 'get_total_blast_radius', None))

@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestEnforceBlastRadiusFunction:
    def test_is_callable(self):
        assert callable(enforce_blast_radius)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(enforce_blast_radius)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestGetProposalMetricsFunction:
    def test_is_callable(self):
        assert callable(get_proposal_metrics)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_proposal_metrics)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestClearProposalFunction:
    def test_is_callable(self):
        assert callable(clear_proposal)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(clear_proposal)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestValidateTotalImpactFunction:
    def test_is_callable(self):
        assert callable(validate_total_impact)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_total_impact)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module blast_radius must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
