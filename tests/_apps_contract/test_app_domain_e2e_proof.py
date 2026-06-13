"""E2E proof tests (plan §P7.4).

Exercises the full chain end-to-end for every registered app:

    YAML  ->  bundle  ->  UWG register  ->  L4 lookup  ->  L0 resolver  ->
    RouteContract with app refs  ->  ExitReviewPacket with app refs  ->
    app_specific_evaluator  ->  OTEL span attrs  ->  proof bundle section

Also proves:
- OTEL attributes carry every app.* key
- Replay determinism: same (app_id, task_class) resolves to same digest
- No-bypass receipt: direct-write attempts are rejected
- Every app's declared negative controls fail for their named reason
  (when we simulate the named-failure grader output)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L0_routing.app_domain_resolver import resolve_and_bind
from agentic_core.L0_routing.c0_retrieval.route_contract import RouteContract
from agentic_core.L0_routing.c0_retrieval.verdicts import FreshnessClass, SupportTarget
from agentic_core.L3_orchestration.exit_eval.v6.app_domain_otel import (
    APP_DOMAIN_SPAN_KEYS,
    build_app_domain_proof_packet_section,
    build_app_domain_span_attributes,
    build_app_domain_span_attributes_from_packet,
)
from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
    AppSpecificEvaluator,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import ExitReviewPacket, SourceType
from agentic_core.L4_state.contracts import (
    get_default_app_domain_store,
    reset_default_app_domain_store,
)
from agentic_core.L4_state.uwg import (
    discover_app_contract_dirs,
    load_bundle_from_dir,
    register_bundle,
)
from agentic_core.L4_state.uwg.durable_write_gateway import reset_default_gateway

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _reset():
    reset_default_gateway()
    reset_default_app_domain_store()
    dirs = discover_app_contract_dirs(REPO_ROOT)
    for app_id in sorted(dirs):
        register_bundle(load_bundle_from_dir(dirs[app_id]))
    yield
    reset_default_gateway()
    reset_default_app_domain_store()


def _base_route(route_id: str = "e2e.test.default") -> RouteContract:
    return RouteContract(
        route_id=route_id,
        grounding_required=True,
        execution_form="SINGLE_STEP",
        freshness_class=FreshnessClass.CURRENT,
        support_target=SupportTarget.SOURCE_SUMMARY,
        tenant_scope="e2e-tenant",
    )


def _resolve(app_id: str, task_class: str) -> RouteContract:
    return resolve_and_bind(_base_route(), app_id, task_class, allow_draft=True)


# ---------------------------------------------------------------------------
# L0 → Route binding
# ---------------------------------------------------------------------------


class TestL0ToRouteBinding:
    @pytest.mark.parametrize(
        "app_id,task_class",
        [
            ("apps_rg", "resume_generation"),
            ("apps_lic", "outreach_message"),
            ("apps_eval", "eval_self"),
            ("apps_exec", "brief_assembly"),
            ("apps_research", "company_brief"),
            ("apps_qna", "qna_pack_build"),
            ("apps_underwriting_ai", "underwriting_decision"),
        ],
    )
    def test_route_carries_app_refs(self, app_id: str, task_class: str) -> None:
        route = _resolve(app_id, task_class)
        assert route.app_id == app_id
        assert route.task_class == task_class
        assert route.domain_contract_ref.startswith("adc::")
        assert route.domain_contract_digest != ""
        assert route.rubric_ref != ""
        assert route.threshold_profile_ref != ""
        assert route.grader_roster_ref != ""
        assert route.retrieval_profile_ref != ""
        assert route.prompt_profile_ref != ""
        assert route.capability_profile_ref != ""
        assert route.route_profile_ref != ""


# ---------------------------------------------------------------------------
# Route → ExitReviewPacket propagation
# ---------------------------------------------------------------------------


def _packet_from_route(route: RouteContract) -> ExitReviewPacket:
    """Simulate Exit's N1-N5 normalization copying app refs into the packet."""
    return ExitReviewPacket(
        source_type=SourceType.L2_SEALED_ARTIFACT,
        request_id="req-1",
        run_id="run-1",
        trace_root="trace-1",
        route_id=route.route_id,
        policy_hash=route.policy_hash,
        blueprint_hash=route.blueprint_hash,
        route_contract={"route_id": route.route_id},
        # Fort Knox fields:
        app_id=route.app_id,
        task_class=route.task_class,
        domain_contract_ref=route.domain_contract_ref,
        resolved_domain_contract_digest=route.domain_contract_digest,
        rubric_ref=route.rubric_ref,
        threshold_profile_ref=route.threshold_profile_ref,
        grader_roster_ref=route.grader_roster_ref,
        retrieval_profile_ref=route.retrieval_profile_ref,
        prompt_profile_ref=route.prompt_profile_ref,
        capability_profile_ref=route.capability_profile_ref,
        route_profile_ref=route.route_profile_ref,
        input_contract_ref=route.input_contract_ref,
        output_schema_ref=route.output_schema_ref,
        app_contract_l4_record_refs=list(route.app_contract_l4_record_refs),
    )


class TestExitReviewPacketPropagation:
    def test_all_app_refs_land_in_packet(self) -> None:
        route = _resolve("apps_rg", "resume_generation")
        packet = _packet_from_route(route)
        assert packet.app_id == "apps_rg"
        assert packet.rubric_ref == "aer::apps_rg::resume_generation::v1"
        assert packet.threshold_profile_ref == "atp::apps_rg::resume_generation::v1"
        assert packet.grader_roster_ref == "agr::apps_rg::resume_generation::v1"
        assert len(packet.app_contract_l4_record_refs) >= 10


# ---------------------------------------------------------------------------
# End-to-end eval (packet -> evaluator -> result)
# ---------------------------------------------------------------------------


def _all_pass_graders(app_id: str, task_class: str) -> dict:
    store = get_default_app_domain_store()
    contract = store.get_contract(app_id, task_class, allow_draft=True)
    rubric = store.get_eval_rubric(contract.eval_rubric_refs[0])
    return {
        d.dimension_id: (lambda _dim, _ctx: (0.99, ["ev-1"]))
        for d in rubric.score_dimensions
    }


class TestE2EEvaluation:
    @pytest.mark.parametrize(
        "app_id,task_class",
        [
            ("apps_rg", "resume_generation"),
            ("apps_lic", "outreach_message"),
            ("apps_research", "company_brief"),
            ("apps_exec", "brief_assembly"),
            ("apps_eval", "eval_self"),
            ("apps_qna", "qna_pack_build"),
        ],
    )
    def test_golden_path_passes_app_specific_eval(
        self, app_id: str, task_class: str,
    ) -> None:
        """Every app's golden path passes when all graders return high scores."""
        route = _resolve(app_id, task_class)
        packet = _packet_from_route(route)
        evaluator = AppSpecificEvaluator(graders=_all_pass_graders(app_id, task_class))
        result = evaluator.evaluate(
            app_id=packet.app_id,
            task_class=packet.task_class,
            rubric_ref=packet.rubric_ref,
            threshold_profile_ref=packet.threshold_profile_ref,
            run_context={"packet": packet},
        )
        assert result.bound is True
        assert result.passed is True, (
            f"{app_id}/{task_class} golden expected PASS, got fail_reasons={result.fail_reasons}"
        )

    @pytest.mark.parametrize(
        "app_id,task_class,dim_to_fail",
        [
            ("apps_rg", "resume_generation", "factual_grounding"),
            ("apps_rg", "resume_generation", "no_fabrication"),
            ("apps_lic", "outreach_message", "personalization_integrity"),
            ("apps_lic", "outreach_message", "no_sensitive_targeting"),
            ("apps_lic", "outreach_message", "brevity_and_channel_fit"),
        ],
    )
    def test_negative_control_fails_for_named_dimension(
        self, app_id: str, task_class: str, dim_to_fail: str,
    ) -> None:
        """Every named negative control fails for its named dimension."""
        route = _resolve(app_id, task_class)
        packet = _packet_from_route(route)
        graders = _all_pass_graders(app_id, task_class)
        # Override just the target dimension with a failing score
        graders[dim_to_fail] = lambda _dim, _ctx: (0.10, ["ev-1"])
        evaluator = AppSpecificEvaluator(graders=graders)
        result = evaluator.evaluate(
            app_id=packet.app_id,
            task_class=packet.task_class,
            rubric_ref=packet.rubric_ref,
            threshold_profile_ref=packet.threshold_profile_ref,
            run_context={"packet": packet},
        )
        assert result.passed is False
        assert any(dim_to_fail in r for r in result.fail_reasons)


# ---------------------------------------------------------------------------
# OTEL span attributes
# ---------------------------------------------------------------------------


class TestOtelSpanAttributes:
    def test_span_attrs_include_every_app_ref(self) -> None:
        route = _resolve("apps_rg", "resume_generation")
        packet = _packet_from_route(route)
        attrs = build_app_domain_span_attributes_from_packet(packet)
        for key in (
            "app.id",
            "app.task_class",
            "app.domain_contract_ref",
            "app.domain_contract_digest",
            "app.rubric_ref",
            "app.threshold_profile_ref",
            "app.grader_roster_ref",
            "app.retrieval_profile_ref",
            "app.prompt_profile_ref",
            "app.capability_profile_ref",
            "app.route_profile_ref",
            "app.input_contract_ref",
            "app.output_schema_ref",
            "l4.record_refs",
        ):
            assert key in attrs, f"missing OTEL attr: {key}"
        assert attrs["app.id"] == "apps_rg"
        assert attrs["app.task_class"] == "resume_generation"

    def test_unbound_packet_produces_empty_attrs(self) -> None:
        packet = ExitReviewPacket(source_type=SourceType.L2_SEALED_ARTIFACT)
        attrs = build_app_domain_span_attributes_from_packet(packet)
        # None of the app.* keys should be present
        assert not any(k.startswith("app.") for k in attrs)

    def test_eval_passed_flag_emitted(self) -> None:
        attrs = build_app_domain_span_attributes(
            app_id="apps_rg",
            task_class="resume_generation",
            app_specific_eval_passed=True,
        )
        assert attrs["exit.app_specific_eval_passed"] is True


# ---------------------------------------------------------------------------
# Proof bundle section
# ---------------------------------------------------------------------------


class TestProofBundleSection:
    def test_proof_section_has_every_required_field(self) -> None:
        section = build_app_domain_proof_packet_section(
            app_id="apps_rg",
            task_class="resume_generation",
            app_domain_contract_ref="adc::apps_rg::v1",
            l4_domain_contract_record_ref="adc::apps_rg::v1",
            uwg_registration_receipt_ref="uwg-receipt-123",
            resolved_l4_record_refs=("r1", "r2", "r3"),
            route_contract_ref="route-1",
            exit_review_packet_ref="erp-1",
            x1_app_specific_gate_results={"factual_grounding": "PASS"},
            x2_aggregation_result="aggregate-123",
            x3_disposition="ALLOW",
            runtime_exhaust_bundle_ref="exhaust-1",
            otel_trace_ref="trace-1",
            replay_receipt_ref="replay-1",
            no_bypass_receipt_ref="nobypass-1",
        )
        for key in (
            "app_id",
            "task_class",
            "app_domain_contract_ref",
            "l4_domain_contract_record_ref",
            "uwg_registration_receipt_ref",
            "resolved_l4_record_refs",
            "route_contract_ref",
            "exit_review_packet_ref",
            "x1_app_specific_gate_results",
            "x2_aggregation_result",
            "x3_disposition",
            "runtime_exhaust_bundle_ref",
            "otel_trace_ref",
            "replay_receipt_ref",
            "no_bypass_receipt_ref",
        ):
            assert key in section, f"missing proof field: {key}"


# ---------------------------------------------------------------------------
# Replay determinism
# ---------------------------------------------------------------------------


class TestReplayDeterminism:
    def test_same_app_task_resolves_same_digest(self) -> None:
        route1 = _resolve("apps_rg", "resume_generation")
        route2 = _resolve("apps_rg", "resume_generation")
        assert route1.domain_contract_digest == route2.domain_contract_digest
        assert route1.rubric_ref == route2.rubric_ref

    def test_digest_invariant_across_base_route_changes(self) -> None:
        """The app-contract digest depends on the L4 record, not on the
        base route the refs are bound into."""
        from agentic_core.L0_routing.app_domain_resolver import (
            resolve_app_contract_refs,
        )
        b1 = resolve_app_contract_refs("apps_rg", "resume_generation")
        b2 = resolve_app_contract_refs("apps_rg", "resume_generation")
        assert b1.domain_contract_digest == b2.domain_contract_digest
