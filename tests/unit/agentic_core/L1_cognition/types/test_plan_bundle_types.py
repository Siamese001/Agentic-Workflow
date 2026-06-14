"""Unit tests for agentic_core.L1_cognition.types.plan_bundle_types.

Wave 6.1 (P2 untested-module coverage) — L1 PLAN BUNDLE outputs.
``PlanBundle`` (frozen, hash-stable M1-M4 aggregator) and
``RuleAwarePlanningFrame`` (the merge-stage projection). Covers defaults,
str-tuple validation, positivity guards, deterministic bundle_hash, and the
to_dict round-trips.
"""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.types.plan_bundle_types import (
    PlanBundle,
    PlanBundleViolation,
    RuleAwarePlanningFrame,
)


class TestPlanBundleDefaults:
    def test_empty_bundle_constructs(self) -> None:
        b = PlanBundle()
        assert b.schemas == ()
        assert b.max_steps == 10
        assert b.max_wallclock_ms == 60_000

    def test_bundle_hash_auto_computed_when_empty(self) -> None:
        b = PlanBundle()
        assert b.bundle_hash
        assert len(b.bundle_hash) == 64  # sha256 hexdigest

    def test_frozen(self) -> None:
        b = PlanBundle()
        with pytest.raises(Exception):  # FrozenInstanceError
            b.max_steps = 5  # type: ignore[misc]


class TestPlanBundleValidation:
    def test_str_passed_as_tuple_field_raises(self) -> None:
        with pytest.raises(PlanBundleViolation, match="schemas must be a tuple"):
            PlanBundle(schemas="not-a-tuple")  # type: ignore[arg-type]

    def test_non_str_item_raises(self) -> None:
        with pytest.raises(PlanBundleViolation, match=r"route_heuristics\[0\] must be str"):
            PlanBundle(route_heuristics=(123,))  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad", [0, -1])
    def test_non_positive_max_steps_raises(self, bad: int) -> None:
        with pytest.raises(PlanBundleViolation, match="max_steps must be positive"):
            PlanBundle(max_steps=bad)

    @pytest.mark.parametrize("bad", [0, -100])
    def test_non_positive_max_wallclock_raises(self, bad: int) -> None:
        with pytest.raises(PlanBundleViolation, match="max_wallclock_ms must be positive"):
            PlanBundle(max_wallclock_ms=bad)


class TestPlanBundleDigest:
    def test_hash_is_deterministic(self) -> None:
        a = PlanBundle(schemas=("s1", "s2"), policy_bounds=("p1",))
        b = PlanBundle(schemas=("s1", "s2"), policy_bounds=("p1",))
        assert a.bundle_hash == b.bundle_hash

    def test_hash_changes_with_content(self) -> None:
        a = PlanBundle(schemas=("s1",))
        b = PlanBundle(schemas=("s2",))
        assert a.bundle_hash != b.bundle_hash

    def test_explicit_hash_preserved(self) -> None:
        b = PlanBundle(bundle_hash="explicit-pin")
        assert b.bundle_hash == "explicit-pin"


class TestPlanBundleToDict:
    def test_to_dict_shape(self) -> None:
        b = PlanBundle(schemas=("s",), max_steps=3)
        d = b.to_dict()
        assert d["schemas"] == ["s"]
        assert d["max_steps"] == 3
        assert d["max_wallclock_ms"] == 60_000
        assert d["bundle_hash"] == b.bundle_hash

    def test_to_dict_lists_all_str_tuple_fields(self) -> None:
        d = PlanBundle().to_dict()
        for fname in PlanBundle._STR_TUPLE_FIELDS:
            assert isinstance(d[fname], list)


class TestRuleAwarePlanningFrame:
    def test_defaults_empty(self) -> None:
        f = RuleAwarePlanningFrame()
        assert f.can_be_proposed == ()
        assert f.must_be_grounded == ()
        assert f.must_be_escalated == ()

    def test_str_field_raises(self) -> None:
        with pytest.raises(PlanBundleViolation, match="can_be_proposed must be a tuple"):
            RuleAwarePlanningFrame(can_be_proposed="x")  # type: ignore[arg-type]

    def test_non_str_item_raises(self) -> None:
        with pytest.raises(PlanBundleViolation, match=r"must_be_grounded\[0\] must be str"):
            RuleAwarePlanningFrame(must_be_grounded=(7,))  # type: ignore[arg-type]

    def test_to_dict(self) -> None:
        f = RuleAwarePlanningFrame(
            can_be_proposed=("a",), must_be_grounded=("b",), must_be_escalated=("c",)
        )
        assert f.to_dict() == {
            "can_be_proposed": ["a"],
            "must_be_grounded": ["b"],
            "must_be_escalated": ["c"],
        }
