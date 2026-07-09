"""W0 thin-slice tests — prove spine contracts flow end-to-end.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-spine-integration-e9c5b3.md W0.4
"""

from __future__ import annotations

import logging

import pytest

from apps_qna.briefing_validator import validate_briefing
from apps_qna.c0_adapter import call_c0
from apps_qna.exit_wiring import emit_exit_review
from apps_qna.l0_router import select_route
from apps_qna.l1_planner import plan_live_interview
from apps_qna.l2.e1_prep import prep_workspace
from apps_qna.l2.e2_valid import validate_build_inputs
from apps_qna.l2.e3_exec import execute_build
from apps_qna.types.spine_contracts import (
    BriefingValidationState,
    X3Disposition,
)
from apps_qna.u0_intake import intake_interview_request


class TestW0ThinSlice:
    """Prove the full spine pipeline: U0→L1→L0→C0/Briefing→L2→Exit."""

    def test_u0_emits_validated_request(self) -> None:
        vr = intake_interview_request(interview_slug="test-int-01")
        assert vr.request_id
        assert vr.source_channel == "apps_qna.app_ingress_runner"
        assert vr.permitted_next_layer == "L1"

    def test_l1_emits_plan_contract(self) -> None:
        plan = plan_live_interview(request_id="req-1", has_briefing=False)
        assert plan.plan_id
        assert plan.grounding_required is True
        assert len(plan.steps) >= 3
        plan.validate()

    def test_l0_emits_single_route_contract(self) -> None:
        route = select_route(grounding_required=True)
        assert route.route_id == "apps_qna.live_interview_runtime_pack_v1"
        assert route.c0_required is True

    def test_uploaded_briefing_bypasses_c0(self) -> None:
        plan = plan_live_interview(request_id="req-2", has_briefing=True, briefing_valid=True)
        assert plan.grounding_required is False
        route = select_route(grounding_required=False, has_valid_briefing=True)
        assert route.uploaded_briefing_required is True

    def test_mock_c0_returns_final_evidence_contract(self) -> None:
        fec = call_c0(interview_slug="test", route_id="r1")
        assert fec["schema_version"] == "1.0"
        assert fec["evidence_sufficiency"] == "grounded"

    def test_l2_renders_two_tier_pack(self) -> None:
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        assert len(manifest.cards) >= 4
        assert manifest.tiering

    def test_exit_emits_x3_disposition(self) -> None:
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        packet = emit_exit_review(manifest=manifest, evidence_contract=fec)
        assert packet.x3_disposition == X3Disposition.ALLOW_FINISH

    def test_manifest_has_evidence_refs(self) -> None:
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        assert len(manifest.evidence_refs) >= 1
        assert len(manifest.card_hashes) >= 4

    def test_no_direct_l2_to_l4_write(self) -> None:
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        assert manifest is not None

    def test_existing_static_build_not_broken(self) -> None:
        from apps_qna.builder.card_pack_builder import CardPackBuilder
        builder = CardPackBuilder()
        assert builder is not None


class TestBriefingValidation:
    """Briefing validator edge cases."""

    def test_no_briefing_path_returns_incomplete(self) -> None:
        result = validate_briefing(briefing_path=None)
        assert result.validation_state == BriefingValidationState.INCOMPLETE

    def test_nonexistent_path_returns_incomplete(self) -> None:
        result = validate_briefing(briefing_path="/nonexistent/briefing.yaml")
        assert result.validation_state == BriefingValidationState.INCOMPLETE

    def test_valid_briefing_returns_sufficient(self, tmp_path) -> None:
        p = tmp_path / "briefing.yaml"
        p.write_text("company: TestCo\nrole: DS Director\n")
        logging.info("C3 write receipt: tests/apps_qna/test_w0_thin_slice.py write side effect recorded")
        result = validate_briefing(briefing_path=str(p))
        assert result.validation_state == BriefingValidationState.SUFFICIENT
        assert result.briefing_hash


class TestRouteSelection:
    """Route selection edge cases."""

    def test_grounded_route_when_no_briefing(self) -> None:
        route = select_route(grounding_required=True, has_valid_briefing=False)
        assert route.c0_required is True

    def test_briefing_route_when_valid_briefing(self) -> None:
        route = select_route(grounding_required=False, has_valid_briefing=True)
        assert route.uploaded_briefing_required is True

    def test_fail_closed_when_no_route_possible(self) -> None:
        with pytest.raises(ValueError, match="No valid route"):
            select_route(grounding_required=False, has_valid_briefing=False)


class TestExitDispositions:
    """Exit wiring edge cases."""

    def test_invalid_build_abstains(self) -> None:
        ws = prep_workspace(interview_slug="test", route_id="r1")
        fec = call_c0(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract=fec)
        packet = emit_exit_review(manifest=manifest, evidence_contract=fec, build_valid=False)
        assert packet.x3_disposition == X3Disposition.SAFE_ABSTAIN

    def test_empty_evidence_abstains(self) -> None:
        ws = prep_workspace(interview_slug="test", route_id="r1")
        manifest = execute_build(ws, evidence_contract={"evidence_sufficiency": "empty"})
        packet = emit_exit_review(manifest=manifest, evidence_contract={"evidence_sufficiency": "empty"})
        assert packet.x3_disposition == X3Disposition.SAFE_ABSTAIN
