"""Unit tests for agentic_core.L3_orchestration.exit_eval.dimension.

Wave 3.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested high-fan-in
exit_eval modules. ``dimension`` (fan_in=21) defines the three-class grader
taxonomy (``GraderClass``), the frozen ``Dimension`` rubric facet with its
``__post_init__`` invariants, and the ``DimensionResult`` scored outcome with
its BUS-P serializer. Exhaustive coverage of the enum, every ValueError path,
and the serialization round-trip.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L3_orchestration.exit_eval.dimension import (
    Dimension,
    DimensionResult,
    GraderClass,
)


class TestGraderClass:
    def test_members(self) -> None:
        assert {g.value for g in GraderClass} == {"code_based", "model_based", "human"}

    def test_is_str_enum(self) -> None:
        # GraderClass subclasses str — value equality holds.
        assert GraderClass.CODE_BASED == "code_based"

    @pytest.mark.parametrize(
        "member,value",
        [
            (GraderClass.CODE_BASED, "code_based"),
            (GraderClass.MODEL_BASED, "model_based"),
            (GraderClass.HUMAN, "human"),
        ],
    )
    def test_value_mapping(self, member: GraderClass, value: str) -> None:
        assert member.value == value


class TestDimensionConstruction:
    def test_minimal_construction(self) -> None:
        d = Dimension(name="groundedness", grader_class=GraderClass.CODE_BASED)
        assert d.name == "groundedness"
        assert d.grader_class is GraderClass.CODE_BASED

    def test_defaults(self) -> None:
        d = Dimension(name="g", grader_class=GraderClass.CODE_BASED)
        assert d.scale == (0.0, 1.0)
        assert d.weight == 1.0
        assert d.is_hard_gate is False
        assert d.threshold == 0.0
        assert d.abstain_allowed is False

    def test_frozen(self) -> None:
        d = Dimension(name="g", grader_class=GraderClass.CODE_BASED)
        with pytest.raises(dataclasses.FrozenInstanceError):
            d.name = "other"  # type: ignore[misc]

    def test_custom_scale_and_threshold(self) -> None:
        d = Dimension(
            name="latency",
            grader_class=GraderClass.CODE_BASED,
            scale=(0.0, 10.0),
            threshold=5.0,
            is_hard_gate=True,
        )
        assert d.scale == (0.0, 10.0)
        assert d.threshold == 5.0
        assert d.is_hard_gate is True

    def test_abstain_allowed_model_based_ok(self) -> None:
        d = Dimension(
            name="judge_dim",
            grader_class=GraderClass.MODEL_BASED,
            abstain_allowed=True,
        )
        assert d.abstain_allowed is True


class TestDimensionPostInitValidation:
    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="name must be non-empty"):
            Dimension(name="", grader_class=GraderClass.CODE_BASED)

    @pytest.mark.parametrize("scale", [(1.0, 1.0), (1.0, 0.0), (0.5, 0.5)])
    def test_scale_min_not_less_than_max_raises(self, scale: tuple[float, float]) -> None:
        with pytest.raises(ValueError, match="scale\\[0\\] must be < scale\\[1\\]"):
            Dimension(name="g", grader_class=GraderClass.CODE_BASED, scale=scale)

    def test_negative_weight_raises(self) -> None:
        with pytest.raises(ValueError, match="weight must be >= 0"):
            Dimension(name="g", grader_class=GraderClass.CODE_BASED, weight=-0.1)

    def test_zero_weight_ok(self) -> None:
        d = Dimension(name="g", grader_class=GraderClass.CODE_BASED, weight=0.0)
        assert d.weight == 0.0

    @pytest.mark.parametrize("threshold", [-0.1, 1.1, 2.0])
    def test_threshold_outside_scale_raises(self, threshold: float) -> None:
        with pytest.raises(ValueError, match="outside scale"):
            Dimension(name="g", grader_class=GraderClass.CODE_BASED, threshold=threshold)

    def test_threshold_at_scale_bounds_ok(self) -> None:
        assert Dimension(name="g", grader_class=GraderClass.CODE_BASED, threshold=0.0).threshold == 0.0
        assert Dimension(name="g", grader_class=GraderClass.CODE_BASED, threshold=1.0).threshold == 1.0

    @pytest.mark.parametrize(
        "grader_class",
        [GraderClass.CODE_BASED, GraderClass.HUMAN],
    )
    def test_abstain_allowed_requires_model_based(self, grader_class: GraderClass) -> None:
        with pytest.raises(ValueError, match="abstain_allowed requires MODEL_BASED"):
            Dimension(name="g", grader_class=grader_class, abstain_allowed=True)


class TestDimensionResult:
    def _make(self, **overrides: object) -> DimensionResult:
        base = {
            "name": "groundedness",
            "score": 0.95,
            "weight": 1.0,
            "threshold": 0.8,
            "passed": True,
            "grader_class": GraderClass.CODE_BASED,
        }
        base.update(overrides)
        return DimensionResult(**base)  # type: ignore[arg-type]

    def test_construction_and_defaults(self) -> None:
        r = self._make()
        assert r.abstain is False
        assert r.is_hard_gate is False
        assert r.evidence == {}

    def test_evidence_default_is_independent(self) -> None:
        a = self._make()
        b = self._make()
        a.evidence["k"] = "v"
        assert b.evidence == {}

    def test_to_bus_row_shape(self) -> None:
        r = self._make(abstain=False)
        row = r.to_bus_row()
        assert row == {
            "name": "groundedness",
            "score": 0.95,
            "weight": 1.0,
            "threshold": 0.8,
            "passed": True,
            "grader_class": "code_based",
            "abstain": False,
        }

    def test_to_bus_row_serializes_grader_class_to_value(self) -> None:
        r = self._make(grader_class=GraderClass.MODEL_BASED, abstain=True)
        row = r.to_bus_row()
        assert row["grader_class"] == "model_based"
        assert row["abstain"] is True

    def test_to_bus_row_omits_evidence(self) -> None:
        # Evidence is intentionally NOT serialized into the bus row.
        r = self._make(evidence={"detail": "x"})
        assert "evidence" not in r.to_bus_row()
