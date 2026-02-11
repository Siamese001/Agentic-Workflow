"""
Contract tests for the L2 PhaseSpec skeleton.

Proves:
1. Phase names match expected legacy ordering exactly.
2. No duplicate phase names.
3. All tuple fields are tuples and empty for this wave.
4. Dataclasses are frozen (mutation raises).
5. __all__ exports exactly the three expected symbols.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L2_execution.types import l2_phase_spec
from agentic_core.L2_execution.types.l2_phase_spec import (
    LEGACY_MIRROR_PLAN,
    L2ExecutionPlan,
    PhaseSpec,
)

EXPECTED_PHASE_NAMES: tuple[str, ...] = (
    "pre_audit",
    "discovery",
    "reconciliation",
    "alignment",
    "arch_validation",
    "healing",
    "certification",
)


class TestPhaseOrdering:
    """Phase names must match expected legacy ordering exactly."""

    def test_exact_names_and_order(self) -> None:
        actual = tuple(p.name for p in LEGACY_MIRROR_PLAN.phases)
        assert actual == EXPECTED_PHASE_NAMES

    def test_phase_count(self) -> None:
        assert len(LEGACY_MIRROR_PLAN.phases) == 7

    def test_no_duplicate_names(self) -> None:
        names = [p.name for p in LEGACY_MIRROR_PLAN.phases]
        assert len(names) == len(set(names))


class TestTupleFields:
    """All tuple fields must be tuples (not lists) and empty for this wave."""

    TUPLE_FIELD_NAMES = ("guardian_ids", "healer_ids", "rerun_guardians", "inputs_from_prior")

    def test_all_tuple_fields_are_tuples(self) -> None:
        for phase in LEGACY_MIRROR_PLAN.phases:
            for field_name in self.TUPLE_FIELD_NAMES:
                value = getattr(phase, field_name)
                assert isinstance(value, tuple), (
                    f"{phase.name}.{field_name} is {type(value).__name__}, expected tuple"
                )

    def test_all_tuple_fields_empty(self) -> None:
        for phase in LEGACY_MIRROR_PLAN.phases:
            for field_name in self.TUPLE_FIELD_NAMES:
                value = getattr(phase, field_name)
                assert value == (), f"{phase.name}.{field_name} is not empty: {value}"

    def test_approval_required_false(self) -> None:
        for phase in LEGACY_MIRROR_PLAN.phases:
            assert phase.approval_required is False, f"{phase.name}.approval_required is not False"

    def test_phases_field_is_tuple(self) -> None:
        assert isinstance(LEGACY_MIRROR_PLAN.phases, tuple)


class TestFrozenImmutability:
    """Dataclasses must be frozen — mutation must raise."""

    def test_phase_spec_frozen(self) -> None:
        phase = LEGACY_MIRROR_PLAN.phases[0]
        with pytest.raises(dataclasses.FrozenInstanceError):
            phase.name = "tampered"

    def test_phase_spec_frozen_tuple_field(self) -> None:
        phase = LEGACY_MIRROR_PLAN.phases[0]
        with pytest.raises(dataclasses.FrozenInstanceError):
            phase.guardian_ids = ("injected",)

    def test_execution_plan_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            LEGACY_MIRROR_PLAN.phases = ()


class TestModuleExports:
    """__all__ must contain exactly the three expected symbols."""

    def test_all_contents(self) -> None:
        assert set(l2_phase_spec.__all__) == {"PhaseSpec", "L2ExecutionPlan", "LEGACY_MIRROR_PLAN"}

    def test_all_length(self) -> None:
        assert len(l2_phase_spec.__all__) == 3

    def test_exported_types_importable(self) -> None:
        assert PhaseSpec is not None
        assert L2ExecutionPlan is not None
        assert LEGACY_MIRROR_PLAN is not None
