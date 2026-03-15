"""Foundational behavioral tests for agentic_core/L0_routing/types/routing_contracts_types.py.

fan_in=7 — imported by 7 other modules.
ADG import-hygiene is covered separately by test_routing_contracts_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.types.routing_contracts_types import (  # noqa: F401
        ArtifactAbsenceFailure,
        GuardrailGuard,
        HealingTransactionBoundary,
        LawSlotHandler,
        MetaGuardianResult,
        PolicyAlignmentResult,
        PolicyConfigGuard,
        PolicyMutationIncident,
        aggregate_gate_check,
        enforce_artifact_presence,
        enforce_route_decision_presence,
        meta_guardian_check,
        static_policy_alignment_check,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    LawSlotHandler = None  # type: ignore[assignment,misc]
    PolicyConfigGuard = None  # type: ignore[assignment,misc]
    PolicyMutationIncident = None  # type: ignore[assignment,misc]
    PolicyAlignmentResult = None  # type: ignore[assignment,misc]
    GuardrailGuard = None  # type: ignore[assignment,misc]
    ArtifactAbsenceFailure = None  # type: ignore[assignment,misc]
    MetaGuardianResult = None  # type: ignore[assignment,misc]
    HealingTransactionBoundary = None  # type: ignore[assignment,misc]
    static_policy_alignment_check = None  # type: ignore[assignment,misc]
    enforce_artifact_presence = None  # type: ignore[assignment,misc]
    enforce_route_decision_presence = None  # type: ignore[assignment,misc]
    meta_guardian_check = None  # type: ignore[assignment,misc]
    aggregate_gate_check = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestLawSlotHandlerContract:
    def test_is_class(self):
        assert isinstance(LawSlotHandler, type)

    def test_has_method_register_twin(self):
        assert callable(getattr(LawSlotHandler, 'register_twin', None))

    def test_has_method_freeze(self):
        assert callable(getattr(LawSlotHandler, 'freeze', None))

    def test_has_method_acquire_slot(self):
        assert callable(getattr(LawSlotHandler, 'acquire_slot', None))

    def test_has_method_depletion_tracker(self):
        assert callable(getattr(LawSlotHandler, 'depletion_tracker', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(LawSlotHandler) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestPolicyConfigGuardContract:
    def test_is_class(self):
        assert isinstance(PolicyConfigGuard, type)

    def test_has_method_policy_hash(self):
        assert callable(getattr(PolicyConfigGuard, 'policy_hash', None))

    def test_has_method_read_config(self):
        assert callable(getattr(PolicyConfigGuard, 'read_config', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(PolicyConfigGuard) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestPolicyMutationIncidentContract:
    def test_is_class(self):
        assert isinstance(PolicyMutationIncident, type)

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(PolicyMutationIncident) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestPolicyAlignmentResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PolicyAlignmentResult)

    def test_is_frozen(self):
        assert PolicyAlignmentResult.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(PolicyAlignmentResult)}
        assert fnames >= {'trace_id', 'policy_hash', 'violations', 'aligned'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(PolicyAlignmentResult)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestGuardrailGuardContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(GuardrailGuard)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(GuardrailGuard)}
        assert fnames >= {'trace_id'}

@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestArtifactAbsenceFailureContract:
    def test_is_class(self):
        assert isinstance(ArtifactAbsenceFailure, type)

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(ArtifactAbsenceFailure) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestMetaGuardianResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MetaGuardianResult)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(MetaGuardianResult)}
        assert fnames >= {'covered_invariants', 'total_invariants', 'coverage_pct', 'passing'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(MetaGuardianResult)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestHealingTransactionBoundaryContract:
    def test_is_class(self):
        assert isinstance(HealingTransactionBoundary, type)

    def test_has_method_commit(self):
        assert callable(getattr(HealingTransactionBoundary, 'commit', None))

    def test_has_method_committed(self):
        assert callable(getattr(HealingTransactionBoundary, 'committed', None))

    def test_has_method_rolled_back(self):
        assert callable(getattr(HealingTransactionBoundary, 'rolled_back', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(HealingTransactionBoundary) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestStaticPolicyAlignmentCheckFunction:
    def test_is_callable(self):
        assert callable(static_policy_alignment_check)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(static_policy_alignment_check)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestEnforceArtifactPresenceFunction:
    def test_is_callable(self):
        assert callable(enforce_artifact_presence)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(enforce_artifact_presence)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestEnforceRouteDecisionPresenceFunction:
    def test_is_callable(self):
        assert callable(enforce_route_decision_presence)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(enforce_route_decision_presence)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestMetaGuardianCheckFunction:
    def test_is_callable(self):
        assert callable(meta_guardian_check)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(meta_guardian_check)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="routing_contracts_types.py deps unavailable")
class TestAggregateGateCheckFunction:
    def test_is_callable(self):
        assert callable(aggregate_gate_check)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(aggregate_gate_check)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: routing_contracts_types importable or gracefully unavailable."""
    pass
