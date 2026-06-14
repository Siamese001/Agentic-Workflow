"""Unit tests for agentic_core.runtime.contracts.runtime_gate_verdict_bundle.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
``runtime_gate_verdict_bundle`` (L_RUNTIME, W2) aggregates the D1/D2 cache-gate
outcomes plus the safety-veto outcome bucket. Frozen dataclass with enum-coercing
__post_init__, similarity-range / non-negative guards, and an anti-cheat
producer_component check. Coverage targets the two enum member sets, string→enum
coercion, every guard branch, frozen behavior, and the to_dict enum-value mapping.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.contracts.runtime_gate_verdict_bundle import (
    GateOutcome,
    RuntimeGateVerdictBundle,
    VetoOutcome,
)


def _valid(**overrides: object) -> RuntimeGateVerdictBundle:
    kwargs: dict = {
        "d1_outcome": GateOutcome.MISS,
        "d2_outcome": GateOutcome.HIT,
        "veto_outcome": VetoOutcome.ALLOWED,
    }
    kwargs.update(overrides)
    return RuntimeGateVerdictBundle(**kwargs)  # type: ignore[arg-type]


class TestEnums:
    def test_gate_outcome_members(self) -> None:
        assert {g.value for g in GateOutcome} == {"HIT", "MISS", "SKIPPED"}

    def test_veto_outcome_members(self) -> None:
        assert {v.value for v in VetoOutcome} == {
            "NOT_INVOKED",
            "ALLOWED",
            "BLOCKED",
            "UNKNOWN",
            "ERROR",
            "TIMEOUT",
            "PARSE_FAIL",
        }

    def test_str_enum_identity(self) -> None:
        assert GateOutcome.HIT == "HIT"
        assert VetoOutcome.BLOCKED == "BLOCKED"


class TestConstructionDefaults:
    def test_defaults(self) -> None:
        b = _valid()
        assert b.d2_similarity == 0.0
        assert b.veto_primary_mode == ""
        assert b.llm_judge_invocation_count == 0
        assert b.veto_latency_ms == 0.0
        assert b.reason_codes == ()
        assert b.producer_component == (
            "agentic_core.runtime.entrypoints.integrated_safe_reuse_run"
        )


class TestEnumCoercion:
    def test_string_outcomes_coerced(self) -> None:
        b = _valid(d1_outcome="HIT", d2_outcome="SKIPPED", veto_outcome="BLOCKED")
        assert b.d1_outcome is GateOutcome.HIT
        assert b.d2_outcome is GateOutcome.SKIPPED
        assert b.veto_outcome is VetoOutcome.BLOCKED

    def test_invalid_outcome_string_raises(self) -> None:
        with pytest.raises(ValueError):
            _valid(d1_outcome="NONSENSE")


class TestGuards:
    @pytest.mark.parametrize("sim", [-0.01, 1.01, 2.0])
    def test_similarity_out_of_range_raises(self, sim: float) -> None:
        with pytest.raises(ValueError, match="d2_similarity must be in"):
            _valid(d2_similarity=sim)

    @pytest.mark.parametrize("sim", [0.0, 0.5, 1.0])
    def test_similarity_in_range_ok(self, sim: float) -> None:
        assert _valid(d2_similarity=sim).d2_similarity == sim

    def test_negative_invocation_count_raises(self) -> None:
        with pytest.raises(ValueError, match="llm_judge_invocation_count must be non-negative"):
            _valid(llm_judge_invocation_count=-1)

    def test_non_core_producer_raises(self) -> None:
        with pytest.raises(ValueError, match="producer_component must be a"):
            _valid(producer_component="tests.harness.fake_producer")

    def test_core_producer_ok(self) -> None:
        b = _valid(producer_component="agentic_core.runtime.something")
        assert b.producer_component == "agentic_core.runtime.something"


class TestFrozen:
    def test_frozen(self) -> None:
        with pytest.raises(dataclasses.FrozenInstanceError):
            _valid().d2_similarity = 0.9  # type: ignore[misc]


class TestToDict:
    def test_enum_fields_serialized_as_values(self) -> None:
        d = _valid(
            d1_outcome=GateOutcome.MISS,
            d2_outcome=GateOutcome.HIT,
            veto_outcome=VetoOutcome.ALLOWED,
        ).to_dict()
        assert d["d1_outcome"] == "MISS"
        assert d["d2_outcome"] == "HIT"
        assert d["veto_outcome"] == "ALLOWED"

    def test_to_dict_carries_scalar_fields(self) -> None:
        d = _valid(d2_similarity=0.75, reason_codes=("d2_semantic_hit",)).to_dict()
        assert d["d2_similarity"] == 0.75
        assert d["reason_codes"] == ("d2_semantic_hit",)
