"""Tests for v4-doctrine extension fields on L1PlanContractV2.

Covers: SupportTarget, LowestViableAgency, EscalationHint,
ClarifyOrAbstainMarker — and their cross-field invariants.
"""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.L1_cognition.types.plan_contract_types import (
    Assumption,
    AssumptionGrade,
    ClarifyOrAbstainMarker,
    EscalationHint,
    ExpectedGroundTruth,
    L1PlanContractV2,
    LowestViableAgency,
    PlanContractViolation,
    PlanTaskStep,
    PlannerTelemetry,
    ProposedRoute,
    QuerySpec,
    ReasoningMode,
    Reversibility,
    RiskBand,
    RouteRisk,
    SupportTarget,
)


def _eg() -> ExpectedGroundTruth:
    return ExpectedGroundTruth(
        signal_kind="tool_result", shape_hint="dict", success_predicate="ok"
    )


def _step() -> PlanTaskStep:
    return PlanTaskStep(step_id="s1", description="d", expected_ground_truth=_eg())


def _risk() -> RouteRisk:
    return RouteRisk(
        cost_band=RiskBand.LOW,
        latency_band=RiskBand.LOW,
        safety_band=RiskBand.LOW,
        reversibility=Reversibility.READ,
    )


def _telemetry() -> PlannerTelemetry:
    return PlannerTelemetry(
        refinements_used=0, wall_clock_ms=1, token_usage=1, critic_iterations=0
    )


def _plan(**overrides: Any) -> L1PlanContractV2:
    defaults: dict[str, Any] = dict(
        plan_id="p",
        request_id="r",
        policy_hash="h",
        proposed_route=ProposedRoute.R1A,
        reasoning_mode=ReasoningMode.DIRECT,
        query_spec=None,
        task_spec=(_step(),),
        route_risk=_risk(),
        confidence_score=0.9,
        grounding_required=False,
        declared_assumptions=(),
        unresolved_gaps=(),
        published_rationale="r",
        planner_telemetry=_telemetry(),
    )
    defaults.update(overrides)
    return L1PlanContractV2(**defaults)


class TestEnumValues:
    def test_support_target_values(self):
        assert {s.value for s in SupportTarget} == {
            "none",
            "citation",
            "direct_span",
            "code_location",
            "policy_clause",
            "evidence_bundle",
        }

    def test_lowest_viable_agency_values(self):
        assert {a.value for a in LowestViableAgency} == {
            "answer_directly",
            "grounded_read",
            "single_action",
            "workflow",
            "fallback",
        }

    def test_escalation_hint_values(self):
        # v5 doctrine § P4 ESCALATION MARKERS — 8-row + NONE.
        assert {e.value for e in EscalationHint} == {
            "none",
            "high_impact",
            "irreversible",
            "ambiguous_authority",
            "unsafe",
            "insufficient_support",
            "policy_conflict",
            "private_data",
            "external_egress",
        }

    def test_clarify_or_abstain_marker_values(self):
        assert {m.value for m in ClarifyOrAbstainMarker} == {
            "none",
            "clarify",
            "abstain",
            "fallback",
        }


class TestDefaults:
    def test_defaults_back_compat(self):
        # No v4 fields supplied — must default and validate.
        p = _plan()
        p.validate()
        assert p.support_target == SupportTarget.NONE
        assert p.lowest_viable_agency == LowestViableAgency.ANSWER_DIRECTLY
        assert p.escalation_hint == EscalationHint.NONE
        assert p.clarify_or_abstain_marker == ClarifyOrAbstainMarker.NONE


class TestSupportTargetInvariant:
    def test_citation_without_grounding_fails(self):
        with pytest.raises(PlanContractViolation, match="support_target"):
            _plan(
                support_target=SupportTarget.CITATION, grounding_required=False
            ).validate()

    def test_citation_with_grounding_validates(self):
        _plan(
            support_target=SupportTarget.CITATION,
            grounding_required=True,
            query_spec=QuerySpec(query_text="q", freshness_window_s=10, max_results=5),
        ).validate()

    def test_none_support_target_no_grounding_required(self):
        _plan(support_target=SupportTarget.NONE, grounding_required=False).validate()

    def test_code_location_does_not_require_grounding(self):
        # CODE_LOCATION is local repo evidence — grounding not required.
        _plan(
            support_target=SupportTarget.CODE_LOCATION, grounding_required=False
        ).validate()


class TestClarifyMarkerInvariant:
    def test_clarify_route_requires_marker(self):
        with pytest.raises(PlanContractViolation, match="CLARIFY"):
            _plan(
                proposed_route=ProposedRoute.CLARIFY,
                grounding_required=False,
                clarify_or_abstain_marker=ClarifyOrAbstainMarker.NONE,
            ).validate()

    def test_clarify_route_with_marker_validates(self):
        _plan(
            proposed_route=ProposedRoute.CLARIFY,
            grounding_required=False,
            clarify_or_abstain_marker=ClarifyOrAbstainMarker.CLARIFY,
        ).validate()


class TestEnumTypeChecks:
    def test_support_target_string_rejected(self):
        with pytest.raises(PlanContractViolation, match="support_target"):
            _plan(support_target="none").validate()  # type: ignore[arg-type]

    def test_lowest_viable_agency_string_rejected(self):
        with pytest.raises(PlanContractViolation, match="lowest_viable_agency"):
            _plan(lowest_viable_agency="answer_directly").validate()  # type: ignore[arg-type]

    def test_escalation_hint_string_rejected(self):
        with pytest.raises(PlanContractViolation, match="escalation_hint"):
            _plan(escalation_hint="none").validate()  # type: ignore[arg-type]

    def test_clarify_marker_string_rejected(self):
        with pytest.raises(PlanContractViolation, match="clarify_or_abstain_marker"):
            _plan(clarify_or_abstain_marker="none").validate()  # type: ignore[arg-type]


class TestSerialization:
    def test_to_dict_includes_v4_fields(self):
        p = _plan(
            support_target=SupportTarget.NONE,
            lowest_viable_agency=LowestViableAgency.GROUNDED_READ,
            escalation_hint=EscalationHint.HIGH_IMPACT,
            clarify_or_abstain_marker=ClarifyOrAbstainMarker.NONE,
        )
        d = p.to_dict()
        assert d["support_target"] == "none"
        assert d["lowest_viable_agency"] == "grounded_read"
        assert d["escalation_hint"] == "high_impact"
        assert d["clarify_or_abstain_marker"] == "none"

    def test_to_v1_drops_v4_fields(self):
        p = _plan(escalation_hint=EscalationHint.HIGH_IMPACT)
        v1 = p.to_v1()
        v1.validate()
        # v1 has no escalation_hint attribute.
        assert not hasattr(v1, "escalation_hint")
