"""Unit tests for agentic_core.runtime.contracts.posture.

W1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 runtime-contract surface.
``posture`` (fan_in=20, L_RUNTIME) supplies the RuntimePosture struct + 5 canonical
posture instances threaded through every emit contract (W6 concern #7). Pure frozen
dataclass + module constants — exhaustive coverage.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts import posture as posture_mod
from agentic_core.runtime.contracts.posture import (
    POSTURE_GENERATION,
    POSTURE_HITL_REQUIRED,
    POSTURE_READ_ONLY,
    POSTURE_RETRIEVAL,
    POSTURE_WRITE_INTENT,
    RuntimePosture,
)


class TestRuntimePostureDefaults:
    def test_default_is_safe_read_only(self) -> None:
        p = RuntimePosture()
        assert p.read_only is True
        assert p.external_call is False
        assert p.write_intent is False
        assert p.hitl_required is False
        assert p.posture_class == "read_only"

    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            RuntimePosture().write_intent = True  # type: ignore[misc]

    def test_slots_no_dict(self) -> None:
        assert not hasattr(RuntimePosture(), "__dict__")

    def test_value_equality(self) -> None:
        assert RuntimePosture() == RuntimePosture()
        assert RuntimePosture(write_intent=True) != RuntimePosture()


class TestCanonicalPostures:
    def test_read_only(self) -> None:
        assert POSTURE_READ_ONLY == RuntimePosture(
            read_only=True, external_call=False, write_intent=False,
            hitl_required=False, posture_class="read_only",
        )

    def test_retrieval(self) -> None:
        assert POSTURE_RETRIEVAL.external_call is True
        assert POSTURE_RETRIEVAL.read_only is False
        assert POSTURE_RETRIEVAL.write_intent is False
        assert POSTURE_RETRIEVAL.posture_class == "retrieval"

    def test_generation(self) -> None:
        assert POSTURE_GENERATION.external_call is True
        assert POSTURE_GENERATION.write_intent is False
        assert POSTURE_GENERATION.posture_class == "generation"

    def test_write_intent(self) -> None:
        assert POSTURE_WRITE_INTENT.write_intent is True
        assert POSTURE_WRITE_INTENT.external_call is False
        assert POSTURE_WRITE_INTENT.hitl_required is False
        assert POSTURE_WRITE_INTENT.posture_class == "write_intent"

    def test_hitl_required(self) -> None:
        assert POSTURE_HITL_REQUIRED.hitl_required is True
        assert POSTURE_HITL_REQUIRED.write_intent is True
        assert POSTURE_HITL_REQUIRED.posture_class == "write_intent"

    def test_only_read_only_is_read_only(self) -> None:
        # Of the 5 canonical postures, exactly one is read-only.
        non_read_only = [
            POSTURE_RETRIEVAL, POSTURE_GENERATION,
            POSTURE_WRITE_INTENT, POSTURE_HITL_REQUIRED,
        ]
        assert POSTURE_READ_ONLY.read_only is True
        assert all(p.read_only is False for p in non_read_only)


class TestModuleExports:
    def test_all_exports_present(self) -> None:
        for name in posture_mod.__all__:
            assert hasattr(posture_mod, name), name

    def test_all_lists_five_canonical_postures(self) -> None:
        canon = {n for n in posture_mod.__all__ if n.startswith("POSTURE_")}
        assert canon == {
            "POSTURE_READ_ONLY", "POSTURE_RETRIEVAL", "POSTURE_GENERATION",
            "POSTURE_WRITE_INTENT", "POSTURE_HITL_REQUIRED",
        }
