"""Tests for PlanBundle + RuleAwarePlanningFrame + load_plan_bundle."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.reasoning.intent_parser import parse_intent
from agentic_core.L1_cognition.reasoning.plan_bundle_loader import (
    derive_rule_aware_frame,
    load_plan_bundle,
)
from agentic_core.L1_cognition.types.plan_bundle_types import (
    PlanBundle,
    PlanBundleViolation,
    RuleAwarePlanningFrame,
)


class TestPlanBundle:
    def test_default_bundle_validates_and_hashes(self):
        b = PlanBundle()
        assert b.bundle_hash != ""
        assert len(b.bundle_hash) == 64  # sha256 hex

    def test_two_default_bundles_have_same_hash(self):
        assert PlanBundle().bundle_hash == PlanBundle().bundle_hash

    def test_different_content_yields_different_hash(self):
        b1 = PlanBundle(schemas=("a",))
        b2 = PlanBundle(schemas=("b",))
        assert b1.bundle_hash != b2.bundle_hash

    def test_bad_tuple_member_fails(self):
        with pytest.raises(PlanBundleViolation, match="schemas"):
            PlanBundle(schemas=(123,))  # type: ignore[arg-type]

    def test_string_in_tuple_field_fails(self):
        with pytest.raises(PlanBundleViolation):
            PlanBundle(schemas="not-a-tuple")  # type: ignore[arg-type]

    def test_zero_max_steps_fails(self):
        with pytest.raises(PlanBundleViolation, match="max_steps"):
            PlanBundle(max_steps=0)

    def test_to_dict_round_trip(self):
        b = PlanBundle(schemas=("s1",), policy_bounds=("p1",))
        d = b.to_dict()
        assert d["schemas"] == ["s1"]
        assert d["policy_bounds"] == ["p1"]
        assert d["bundle_hash"] == b.bundle_hash


class TestLoadPlanBundle:
    def test_loader_returns_valid_bundle(self):
        b = load_plan_bundle(schemas=["a", "b"], policy_bounds=("p",))
        assert b.schemas == ("a", "b")
        assert b.policy_bounds == ("p",)
        assert b.bundle_hash


class TestDeriveRuleAwareFrame:
    def test_high_risk_intent_appears_in_escalated(self):
        intent = parse_intent("Delete production database", request_id="r1")
        bundle = load_plan_bundle()
        frame = derive_rule_aware_frame(intent, bundle)
        assert any("high_risk" in p for p in frame.must_be_escalated)

    def test_grounding_predicates_routed_correctly(self):
        intent = parse_intent("anything", request_id="r1")
        bundle = load_plan_bundle(
            policy_bounds=("must cite evidence", "format constraint"),
        )
        frame = derive_rule_aware_frame(intent, bundle)
        assert "must cite evidence" in frame.must_be_grounded
        assert "format constraint" not in frame.must_be_grounded

    def test_route_heuristics_routed_to_proposable(self):
        intent = parse_intent("anything", request_id="r1")
        bundle = load_plan_bundle(
            route_heuristics=("R1A for cached", "R3 for grounded"),
            approved_templates=("simple-answer",),
        )
        frame = derive_rule_aware_frame(intent, bundle)
        assert "R1A for cached" in frame.can_be_proposed
        assert "simple-answer" in frame.can_be_proposed


class TestRuleAwarePlanningFrame:
    def test_to_dict_shape(self):
        f = RuleAwarePlanningFrame(
            can_be_proposed=("a",),
            must_be_grounded=("b",),
            must_be_escalated=("c",),
        )
        assert f.to_dict() == {
            "can_be_proposed": ["a"],
            "must_be_grounded": ["b"],
            "must_be_escalated": ["c"],
        }

    def test_string_field_rejected(self):
        with pytest.raises(PlanBundleViolation):
            RuleAwarePlanningFrame(can_be_proposed="not-a-tuple")  # type: ignore[arg-type]
