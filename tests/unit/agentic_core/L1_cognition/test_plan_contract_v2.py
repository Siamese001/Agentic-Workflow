"""Tests for L1PlanContractV2 and supporting types (ADR-043).

Covers:
- Enum shapes (ProposedRoute, AssumptionGrade, RiskBand, Reversibility)
- Valid v2 contract construction + validate() pass
- Required-field and shape violations
- grounding_required ⇒ query_spec required invariant
- CLARIFY + grounding incompatibility
- Scratchpad redaction canary fails closed
- to_dict() round-trip
- to_v1() / from_v1() back-compat shim
"""

from __future__ import annotations

import pytest
from dataclasses import FrozenInstanceError

from agentic_core.L1_cognition.types.plan_contract_types import (
    Assumption,
    AssumptionGrade,
    ExpectedGroundTruth,
    L1PlanContract,
    L1PlanContractV2,
    PlanContractViolation,
    PlanTaskStep,
    PlannerTelemetry,
    ProposedRoute,
    QuerySpec,
    ReasoningMode,
    Reversibility,
    RiskBand,
    RouteRisk,
)


def _eg() -> ExpectedGroundTruth:
    return ExpectedGroundTruth(
        signal_kind="tool_result",
        shape_hint="dict[str, Any]",
        success_predicate="rows > 0",
    )


def _step(step_id: str = "s1") -> PlanTaskStep:
    return PlanTaskStep(step_id=step_id, description="do the thing", expected_ground_truth=_eg())


def _risk() -> RouteRisk:
    return RouteRisk(
        cost_band=RiskBand.LOW,
        latency_band=RiskBand.LOW,
        safety_band=RiskBand.LOW,
        reversibility=Reversibility.READ,
    )


def _telemetry() -> PlannerTelemetry:
    return PlannerTelemetry(
        refinements_used=1,
        wall_clock_ms=25,
        token_usage=500,
        critic_iterations=1,
    )


def _valid_v2(**overrides) -> L1PlanContractV2:
    defaults = dict(
        plan_id="plan-v2-001",
        request_id="req-001",
        policy_hash="sha256:policy",
        proposed_route=ProposedRoute.R3,
        reasoning_mode=ReasoningMode.DECOMPOSED,
        query_spec=QuerySpec(query_text="q", freshness_window_s=3600, max_results=10),
        task_spec=(_step("s1"), _step("s2")),
        route_risk=_risk(),
        confidence_score=0.88,
        grounding_required=True,
        declared_assumptions=(Assumption(statement="x", grade=AssumptionGrade.DIRECTLY_OBSERVED),),
        unresolved_gaps=("gap one",),
        published_rationale="planner selected R3 because grounding was required",
        planner_telemetry=_telemetry(),
    )
    defaults.update(overrides)
    return L1PlanContractV2(**defaults)


class TestEnums:
    def test_proposed_route_values(self):
        assert {r.value for r in ProposedRoute} == {"R1A", "R1B", "R3", "R4", "R5", "CLARIFY"}

    def test_assumption_grade_values(self):
        assert {g.value for g in AssumptionGrade} == {"DIRECTLY_OBSERVED", "DERIVED", "UNRESOLVED"}

    def test_risk_bands(self):
        assert {b.value for b in RiskBand} == {"LOW", "MED", "HIGH"}

    def test_reversibility(self):
        assert {r.value for r in Reversibility} == {"READ", "ACTION", "WRITE"}


class TestValidV2:
    def test_valid_contract_validates(self):
        _valid_v2().validate()

    def test_grounding_false_with_no_query_spec_validates(self):
        _valid_v2(grounding_required=False, query_spec=None).validate()

    def test_single_step_validates(self):
        _valid_v2(task_spec=(_step(),)).validate()

    def test_confidence_boundaries_validate(self):
        _valid_v2(confidence_score=0.0).validate()
        _valid_v2(confidence_score=1.0).validate()

    def test_empty_assumptions_and_gaps_allowed(self):
        _valid_v2(declared_assumptions=(), unresolved_gaps=()).validate()


class TestV2Violations:
    def test_grounding_required_without_query_spec_fails(self):
        with pytest.raises(PlanContractViolation, match="query_spec"):
            _valid_v2(grounding_required=True, query_spec=None).validate()

    def test_clarify_route_with_grounding_fails(self):
        with pytest.raises(PlanContractViolation, match="CLARIFY"):
            _valid_v2(
                proposed_route=ProposedRoute.CLARIFY,
                grounding_required=True,
            ).validate()

    def test_empty_task_spec_fails(self):
        with pytest.raises(PlanContractViolation, match="task_spec"):
            _valid_v2(task_spec=()).validate()

    def test_task_spec_bare_string_fails(self):
        with pytest.raises(PlanContractViolation):
            _valid_v2(task_spec="one-big-step").validate()

    def test_task_spec_wrong_type_fails(self):
        with pytest.raises(PlanContractViolation, match="PlanTaskStep"):
            _valid_v2(task_spec=({"step": "raw dict"},)).validate()

    def test_confidence_out_of_range_fails(self):
        with pytest.raises(PlanContractViolation):
            _valid_v2(confidence_score=1.5).validate()

    def test_wrong_route_type_fails(self):
        with pytest.raises(PlanContractViolation, match="proposed_route"):
            _valid_v2(proposed_route="R3").validate()

    def test_wrong_risk_type_fails(self):
        with pytest.raises(PlanContractViolation, match="route_risk"):
            _valid_v2(route_risk={"cost": "low"}).validate()

    def test_assumption_wrong_type_fails(self):
        with pytest.raises(PlanContractViolation, match="declared_assumptions"):
            _valid_v2(declared_assumptions=("plain string",)).validate()

    def test_unresolved_gaps_wrong_type_fails(self):
        with pytest.raises(PlanContractViolation, match="unresolved_gaps"):
            _valid_v2(unresolved_gaps=(123,)).validate()

    def test_empty_published_rationale_fails(self):
        with pytest.raises(PlanContractViolation):
            _valid_v2(published_rationale="   ").validate()

    def test_scratchpad_canary_fails_closed(self):
        bad = "<<<PRIVATE_SCRATCHPAD leaked internal thought >>>"
        with pytest.raises(PlanContractViolation, match="scratchpad"):
            _valid_v2(published_rationale=bad).validate()


class TestSerialization:
    def test_to_dict_roundtrip_shape(self):
        d = _valid_v2().to_dict()
        for key in (
            "plan_id",
            "request_id",
            "policy_hash",
            "proposed_route",
            "reasoning_mode",
            "query_spec",
            "task_spec",
            "route_risk",
            "confidence_score",
            "grounding_required",
            "declared_assumptions",
            "unresolved_gaps",
            "published_rationale",
            "planner_telemetry",
        ):
            assert key in d, f"missing key {key}"

    def test_enum_fields_serialized_as_strings(self):
        d = _valid_v2(proposed_route=ProposedRoute.R4).to_dict()
        assert d["proposed_route"] == "R4"
        assert d["reasoning_mode"] == "DECOMPOSED"

    def test_nested_task_spec_dictified(self):
        d = _valid_v2().to_dict()
        assert isinstance(d["task_spec"], list)
        first = d["task_spec"][0]
        assert "expected_ground_truth" in first
        assert first["expected_ground_truth"]["signal_kind"] == "tool_result"

    def test_query_spec_none_serializes_to_none(self):
        d = _valid_v2(grounding_required=False, query_spec=None).to_dict()
        assert d["query_spec"] is None


class TestBackCompatShim:
    def _valid_v1(self) -> L1PlanContract:
        return L1PlanContract(
            plan_id="legacy-1",
            request_id="req-1",
            policy_hash="sha256:pol",
            reasoning_mode=ReasoningMode.DIRECT,
            grounding_required=False,
            confidence_score=0.9,
            steps=({"action": "ret"},),
        )

    def test_from_v1_then_validate_round_trips(self):
        v1 = self._valid_v1()
        v2 = L1PlanContractV2.from_v1(
            v1,
            proposed_route=ProposedRoute.R1A,
            route_risk=_risk(),
            task_spec=(_step(),),
        )
        v2.validate()
        assert v2.plan_id == v1.plan_id
        assert v2.confidence_score == v1.confidence_score

    def test_to_v1_projects_to_legacy_shape(self):
        v2 = _valid_v2(grounding_required=False, query_spec=None)
        v1 = v2.to_v1()
        v1.validate()
        assert v1.plan_id == v2.plan_id
        assert len(v1.steps) == len(v2.task_spec)

    def test_from_v1_default_telemetry_is_zeroed(self):
        v2 = L1PlanContractV2.from_v1(
            self._valid_v1(),
            proposed_route=ProposedRoute.R1A,
            route_risk=_risk(),
            task_spec=(_step(),),
        )
        assert v2.planner_telemetry.refinements_used == 0
        assert v2.planner_telemetry.critic_iterations == 0


class TestImmutability:
    def test_v2_is_frozen(self):
        c = _valid_v2()
        with pytest.raises(FrozenInstanceError):
            c.plan_id = "changed"  # type: ignore[misc]

    def test_task_spec_is_tuple(self):
        assert isinstance(_valid_v2().task_spec, tuple)

    def test_nested_dataclasses_frozen(self):
        risk = _risk()
        with pytest.raises(FrozenInstanceError):
            risk.cost_band = RiskBand.HIGH  # type: ignore[misc]
