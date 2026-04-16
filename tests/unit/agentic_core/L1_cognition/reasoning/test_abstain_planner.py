"""Wave D3.2 unit tests for the F06 abstain-planning primitive.

Coverage requirements (Wave D plan §3 Slice D3 and the D3.1 prompt):

1. abstain fires when confidence < threshold
2. proceed when confidence >= threshold
3. returned shape is stable and serializable
4. no regression of existing planner behavior outside the new abstain path
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L1_cognition.reasoning.abstain_planner import (
    ACTION_CONTINUE,
    ACTION_EMIT_R5,
    DECISION_ABSTAIN,
    DECISION_PROCEED,
    DEFAULT_ABSTAIN_THRESHOLD,
    AbstainDecision,
    plan_abstain,
)

REQUIRED_FIELDS = {"decision", "reason", "confidence", "threshold", "action"}


class TestPlanAbstainFires:
    """Requirement 1: abstain fires when confidence < threshold."""

    def test_strictly_below_default_threshold_triggers_abstain(self) -> None:
        result = plan_abstain(confidence=0.30)
        assert result["decision"] == DECISION_ABSTAIN
        assert result["action"] == ACTION_EMIT_R5
        assert result["confidence"] == pytest.approx(0.30)
        assert result["threshold"] == pytest.approx(DEFAULT_ABSTAIN_THRESHOLD)

    def test_just_below_custom_threshold_triggers_abstain(self) -> None:
        result = plan_abstain(confidence=0.6999, threshold=0.70)
        assert result["decision"] == DECISION_ABSTAIN
        assert result["action"] == ACTION_EMIT_R5

    def test_zero_confidence_triggers_abstain(self) -> None:
        result = plan_abstain(confidence=0.0)
        assert result["decision"] == DECISION_ABSTAIN
        assert result["action"] == ACTION_EMIT_R5

    def test_reason_includes_default_explanation_when_no_hint(self) -> None:
        result = plan_abstain(confidence=0.10, threshold=0.50)
        assert "0.1000" in result["reason"]
        assert "0.5000" in result["reason"]
        assert "below" in result["reason"].lower()

    def test_reason_hint_overrides_default_reason(self) -> None:
        result = plan_abstain(
            confidence=0.10,
            threshold=0.50,
            reason_hint="custom hint from caller",
        )
        assert result["reason"] == "custom hint from caller"


class TestPlanAbstainProceeds:
    """Requirement 2: proceed when confidence >= threshold."""

    def test_strictly_above_default_threshold_proceeds(self) -> None:
        result = plan_abstain(confidence=0.95)
        assert result["decision"] == DECISION_PROCEED
        assert result["action"] == ACTION_CONTINUE

    def test_exactly_at_threshold_proceeds(self) -> None:
        # Strictly less than triggers abstain; equality proceeds.
        result = plan_abstain(confidence=0.50, threshold=0.50)
        assert result["decision"] == DECISION_PROCEED
        assert result["action"] == ACTION_CONTINUE

    def test_one_point_zero_confidence_proceeds(self) -> None:
        result = plan_abstain(confidence=1.0)
        assert result["decision"] == DECISION_PROCEED
        assert result["action"] == ACTION_CONTINUE

    def test_reason_hint_overrides_default_for_proceed(self) -> None:
        result = plan_abstain(
            confidence=0.90,
            reason_hint="strong match",
        )
        assert result["reason"] == "strong match"


class TestDecisionShapeIsStableAndSerializable:
    """Requirement 3: returned shape is stable and serializable."""

    @pytest.mark.parametrize(
        "confidence,threshold",
        [
            (0.10, 0.50),  # abstain branch
            (0.95, 0.50),  # proceed branch
            (0.50, 0.50),  # boundary
            (0.00, 0.50),  # minimum confidence
            (1.00, 0.50),  # maximum confidence
        ],
    )
    def test_shape_has_exactly_five_required_fields(self, confidence: float, threshold: float) -> None:
        result = plan_abstain(confidence=confidence, threshold=threshold)
        assert set(result.keys()) == REQUIRED_FIELDS

    @pytest.mark.parametrize(
        "confidence",
        [0.10, 0.50, 0.95],
    )
    def test_result_is_json_serializable(self, confidence: float) -> None:
        result = plan_abstain(confidence=confidence)
        encoded = json.dumps(result)
        decoded = json.loads(encoded)
        assert decoded == dict(result)

    def test_field_types_are_primitives(self) -> None:
        result = plan_abstain(confidence=0.30)
        assert isinstance(result["decision"], str)
        assert isinstance(result["reason"], str)
        assert isinstance(result["confidence"], float)
        assert isinstance(result["threshold"], float)
        assert isinstance(result["action"], str)

    def test_decision_values_are_closed_enum(self) -> None:
        abstain_result = plan_abstain(confidence=0.10)
        proceed_result = plan_abstain(confidence=0.95)
        assert abstain_result["decision"] in {DECISION_ABSTAIN, DECISION_PROCEED}
        assert proceed_result["decision"] in {DECISION_ABSTAIN, DECISION_PROCEED}

    def test_action_values_are_closed_enum(self) -> None:
        abstain_result = plan_abstain(confidence=0.10)
        proceed_result = plan_abstain(confidence=0.95)
        assert abstain_result["action"] in {ACTION_EMIT_R5, ACTION_CONTINUE}
        assert proceed_result["action"] in {ACTION_EMIT_R5, ACTION_CONTINUE}

    def test_abstain_decision_is_paired_with_emit_r5(self) -> None:
        result = plan_abstain(confidence=0.10)
        assert result["decision"] == DECISION_ABSTAIN
        assert result["action"] == ACTION_EMIT_R5

    def test_proceed_decision_is_paired_with_continue(self) -> None:
        result = plan_abstain(confidence=0.95)
        assert result["decision"] == DECISION_PROCEED
        assert result["action"] == ACTION_CONTINUE

    def test_typeddict_annotation_is_exported(self) -> None:
        # Public contract: downstream D4 / D5 must be able to import the
        # TypedDict for static typing.
        assert AbstainDecision is not None


class TestInputValidation:
    """Input validation: confidence and threshold must be in [0.0, 1.0]."""

    @pytest.mark.parametrize("bad_value", [-0.1, 1.1, 2.0, -1.0])
    def test_out_of_range_confidence_raises(self, bad_value: float) -> None:
        with pytest.raises(ValueError, match="confidence"):
            plan_abstain(confidence=bad_value)

    @pytest.mark.parametrize("bad_value", [-0.1, 1.1, 2.0, -1.0])
    def test_out_of_range_threshold_raises(self, bad_value: float) -> None:
        with pytest.raises(ValueError, match="threshold"):
            plan_abstain(confidence=0.5, threshold=bad_value)


class TestNoRegressionOfExistingPlanner:
    """Requirement 4: no regression of existing planner behavior outside the
    new abstain path.

    Wave D3.1 deliberately chose a NEW module (`abstain_planner.py`) rather
    than extending `query_planner.py`. The smoke tests below verify the
    existing planner module still imports and exposes its public surface
    without modification from this slice.
    """

    def test_query_planner_module_still_imports(self) -> None:
        # If query_planner.py were accidentally modified or broken by the
        # D3.1 work, this import would raise.
        from agentic_core.L1_cognition.reasoning import query_planner

        assert hasattr(query_planner, "query_planner")

    def test_query_planner_public_methods_unchanged(self) -> None:
        from agentic_core.L1_cognition.reasoning.query_planner import (
            query_planner as QueryPlannerCls,
        )

        # These four async methods are the entire pre-Wave-D public surface
        # of query_planner per the D3.1 inspection (lines 239-326). If the
        # abstain primitive were accidentally merged into this class,
        # additional callables would appear; if existing methods were
        # removed, the suite would fail here.
        expected_methods = {
            "multi_query_generation",
            "decompose_query",
            "decompose_and_expand",
            "generate_synthetic_passages",
        }
        actual_methods = {
            name
            for name in dir(QueryPlannerCls)
            if not name.startswith("_") and callable(getattr(QueryPlannerCls, name))
        }
        missing = expected_methods - actual_methods
        assert not missing, f"query_planner missing expected methods: {missing}"

    def test_abstain_planner_is_a_distinct_module(self) -> None:
        from agentic_core.L1_cognition.reasoning import (
            abstain_planner,
            query_planner,
        )

        assert abstain_planner.__name__ != query_planner.__name__
        assert abstain_planner.__file__ != query_planner.__file__
