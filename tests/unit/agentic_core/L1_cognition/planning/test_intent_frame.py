"""Tests for IntentFrame + parse_intent (doc § PARSE INTENT, I1-I4)."""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.L1_cognition.reasoning.intent_parser import parse_intent
from agentic_core.L1_cognition.types.intent_frame_types import (
    AmbiguityRegister,
    AmbiguityResolutionStrategy,
    ConstraintBinding,
    IntentFrame,
    IntentFrameViolation,
    OutputTargetKind,
    WorkClass,
)


class TestIntentFrameValidation:
    def _valid(self, **overrides: Any) -> IntentFrame:
        defaults: dict[str, Any] = dict(
            request_id="req-1",
            goal="Summarize the quarterly results",
            success_condition="User receives a 1-page summary",
            constraints=(),
            details=(),
            output_target_kind=OutputTargetKind.ANSWER,
            work_class=WorkClass.SUMMARIZE,
        )
        defaults.update(overrides)
        return IntentFrame(**defaults)

    def test_valid_frame_validates(self):
        self._valid().validate()

    def test_empty_goal_fails(self):
        with pytest.raises(IntentFrameViolation, match="goal"):
            self._valid(goal="   ").validate()

    def test_wrong_work_class_fails(self):
        with pytest.raises(IntentFrameViolation, match="work_class"):
            self._valid(work_class="summarize").validate()

    def test_wrong_output_kind_fails(self):
        with pytest.raises(IntentFrameViolation, match="output_target_kind"):
            self._valid(output_target_kind="answer").validate()

    def test_constraints_must_be_tuple_of_bindings(self):
        with pytest.raises(IntentFrameViolation):
            self._valid(constraints=("must do X",)).validate()

    def test_details_must_be_tuple_of_str(self):
        with pytest.raises(IntentFrameViolation):
            self._valid(details=(123,)).validate()

    def test_to_dict_round_trip(self):
        frame = self._valid()
        d = frame.to_dict()
        assert d["work_class"] == "summarize"
        assert d["output_target_kind"] == "answer"
        assert "ambiguity" in d


class TestParseIntent:
    def test_minimal_request(self):
        f = parse_intent("Summarize today's news", request_id="r1")
        f.validate()
        assert f.request_id == "r1"
        # Heuristic should classify factual or summarize, both acceptable.
        assert f.work_class in (WorkClass.SUMMARIZE, WorkClass.FACTUAL)

    def test_must_constraint_extracted(self):
        f = parse_intent(
            "Find pricing. The answer must cite a source.",
            request_id="r1",
        )
        bindings = [c for c in f.constraints if c.severity == "must"]
        assert bindings, "expected must-constraint to be extracted"

    def test_avoid_constraint_extracted(self):
        f = parse_intent(
            "Generate a draft. Do not include emojis.",
            request_id="r1",
        )
        avoids = [c for c in f.constraints if c.severity == "avoid"]
        assert avoids

    def test_high_risk_inferred(self):
        f = parse_intent("Delete the production database", request_id="r1")
        assert f.high_risk is True

    def test_low_risk_default(self):
        f = parse_intent("Tell me a joke", request_id="r1")
        assert f.high_risk is False

    def test_caller_overrides_take_precedence(self):
        f = parse_intent(
            "anything",
            request_id="r1",
            goal="explicit goal",
            success_condition="explicit success",
            work_class=WorkClass.ANALYZE,
            output_target_kind=OutputTargetKind.PLAN,
            high_risk=True,
        )
        assert f.goal == "explicit goal"
        assert f.work_class == WorkClass.ANALYZE
        assert f.output_target_kind == OutputTargetKind.PLAN
        assert f.high_risk is True

    def test_unresolved_triggers_clarify_strategy(self):
        f = parse_intent(
            "Do the thing",
            request_id="r1",
            unresolved=("which thing?",),
        )
        assert f.ambiguity.resolution_strategy == AmbiguityResolutionStrategy.CLARIFY
        assert f.ambiguity.has_unresolved() is True

    def test_action_keyword_infers_action_target(self):
        f = parse_intent("Execute the migration script", request_id="r1")
        assert f.output_target_kind == OutputTargetKind.ACTION


class TestAmbiguityRegister:
    def test_default_empty(self):
        ar = AmbiguityRegister()
        assert not ar.has_unresolved()
        assert ar.resolution_strategy == AmbiguityResolutionStrategy.ASSUME

    def test_to_dict_shape(self):
        ar = AmbiguityRegister(
            known=("a",),
            assumed=("b",),
            unresolved=("c",),
            resolution_strategy=AmbiguityResolutionStrategy.CLARIFY,
        )
        d = ar.to_dict()
        assert d["known"] == ["a"]
        assert d["resolution_strategy"] == "clarify"


class TestConstraintBinding:
    def test_to_dict(self):
        c = ConstraintBinding(statement="must cite", severity="must")
        d = c.to_dict()
        assert d == {"statement": "must cite", "severity": "must", "source": "user"}
