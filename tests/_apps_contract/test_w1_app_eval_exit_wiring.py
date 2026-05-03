"""W1 verification — App-specific eval is wired into X2 aggregate + X3 disposition.

Plan: ``.windsurf/plans/apps-eval-harness-parity-f8d4a2.md`` W1.P5.

This module proves the NEW wiring introduced in W1.P1-P4:

- W1.P1 — pipeline.py invokes AppSpecificEvaluator.evaluate_from_packet and
  serializes the result into ExitReviewPacket.app_specific_eval.
- W1.P2 — app_grader_registry.read_dim_score_from_output is used as the
  default grader, reading from run_context["output"]["dim_scores"].
- W1.P3 — x2_matrix.aggregate_decision returns DENY with rationale
  "app_specific_eval_failed" when the packet carries a bound-and-failed
  app_specific_eval.
- W1.P4 — x3_dispositions._build_x3_packet_impl overrides ALLOW / COMMIT to
  DENY when app_specific_eval is bound and did not pass (belt-and-braces).

The existing isolated-evaluator tests in test_app_domain_exit_evaluation.py
cover evaluator correctness. This module specifically proves Exit-level
consumption of the result.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import pytest

from agentic_core.L0_routing.app_domain_resolver import resolve_and_bind
from agentic_core.L0_routing.c0_retrieval.route_contract import RouteContract
from agentic_core.L0_routing.c0_retrieval.verdicts import FreshnessClass, SupportTarget
from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    build_default_app_evaluator,
    read_dim_score_from_output,
)
from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
    AppSpecificEvalResult,
    AppSpecificEvaluator,
    evaluate_from_packet,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateResult,
    GateVerdict,
    SourceType,
    V6Disposition,
    X3AllowPacket,
    X3DenyPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import (
    AggregateDecision,
    aggregate_decision,
)
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import build_x3_packet
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


APPS_UNDER_TEST = [
    ("apps_rg", "resume_generation"),
    ("apps_lic", "outreach_message"),
    ("apps_rfp", "rfp_response"),
    ("apps_qna", "qna_pack_build"),
    ("apps_research", "company_brief"),
    ("apps_exec", "brief_assembly"),
    ("apps_eval", "eval_self"),
    ("apps_underwriting_ai", "underwriting_decision"),
]


@pytest.fixture(autouse=True)
def _reset_stores():
    reset_default_gateway()
    reset_default_app_domain_store()
    dirs = discover_app_contract_dirs(REPO_ROOT)
    for app_id in sorted(dirs):
        register_bundle(load_bundle_from_dir(dirs[app_id]))
    yield
    reset_default_gateway()
    reset_default_app_domain_store()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _base_route(app_id: str, task_class: str) -> RouteContract:
    base = RouteContract(
        route_id=f"w1.{app_id}.{task_class}",
        grounding_required=True,
        execution_form="SINGLE_STEP",
        freshness_class=FreshnessClass.CURRENT,
        support_target=SupportTarget.SOURCE_SUMMARY,
        tenant_scope="w1-tenant",
    )
    return resolve_and_bind(base, app_id, task_class, allow_draft=True)


def _packet_from_route(
    route: RouteContract,
    *,
    output: dict | None = None,
    terminal_class: str = "answer_only",
) -> ExitReviewPacket:
    return ExitReviewPacket(
        source_type=SourceType.L2_SEALED_ARTIFACT,
        request_id="req-w1",
        run_id="run-w1",
        trace_root="trace-w1",
        route_id=route.route_id,
        policy_hash=route.policy_hash,
        blueprint_hash=route.blueprint_hash,
        route_contract={"route_id": route.route_id},
        terminal_class=terminal_class,
        output=output or {},
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


def _build_output(app_id: str, task_class: str, scores: Mapping[str, float]) -> dict:
    """Construct an output dict shape consumed by read_dim_score_from_output.

    Caller passes scores per dim. Each dim also gets a one-element evidence
    list so evidence_required dims pass.
    """
    return {
        "dim_scores": dict(scores),
        "dim_evidence": {dim_id: [f"ev-{dim_id}"] for dim_id in scores},
    }


def _all_pass_output(app_id: str, task_class: str) -> dict:
    store = get_default_app_domain_store()
    contract = store.get_contract(app_id, task_class, allow_draft=True)
    rubric = store.get_eval_rubric(contract.eval_rubric_refs[0])
    return _build_output(
        app_id,
        task_class,
        {d.dimension_id: 0.99 for d in rubric.score_dimensions},
    )


def _run_app_eval(packet: ExitReviewPacket) -> AppSpecificEvalResult:
    evaluator = build_default_app_evaluator()
    return evaluate_from_packet(
        evaluator=evaluator,
        app_id=packet.app_id,
        task_class=packet.task_class,
        rubric_ref=packet.rubric_ref,
        threshold_profile_ref=packet.threshold_profile_ref,
        run_context={"output": packet.output or {}},
    )


def _attach_app_eval(packet: ExitReviewPacket) -> AppSpecificEvalResult:
    """Populate packet.app_specific_eval from the current output — simulates
    the pipeline.run() step added in W1.P1."""
    result = _run_app_eval(packet)
    if result.bound:
        packet.app_specific_eval = result.to_packet_dict()
    return result


def _pass_verdicts() -> list[GateVerdict]:
    """10 X1 verdicts all PASS — so the X2 matrix would normally ALLOW if
    app_specific_eval didn't exist."""
    return [
        GateVerdict(gate_id=g, result=GateResult.PASS)
        for g in ("X1A", "X1B", "X1C", "X1D", "X1E", "X1F", "X1G", "X1H", "X1I", "X1J")
    ]


# ---------------------------------------------------------------------------
# W1.P2 — read_dim_score_from_output contract
# ---------------------------------------------------------------------------


class TestReadDimScoreFromOutput:
    def test_reads_score_and_evidence(self) -> None:
        from agentic_core.L4_state.contracts.app_domain import ScoreDimension

        dim = ScoreDimension(
            dimension_id="factual_grounding",
            description="",
            weight=0.25,
            grader_type="deterministic",
            min_required_score=0.95,
            evidence_required=True,
            fail_closed_if_unknown=True,
        )
        ctx = {
            "output": {
                "dim_scores": {"factual_grounding": 0.97},
                "dim_evidence": {"factual_grounding": ["profile:abc"]},
            }
        }
        score, evidence = read_dim_score_from_output(dim, ctx)
        assert score == pytest.approx(0.97)
        assert evidence == ["profile:abc"]

    def test_missing_score_returns_unknown(self) -> None:
        from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
            GRADER_UNKNOWN_SENTINEL,
        )
        from agentic_core.L4_state.contracts.app_domain import ScoreDimension

        dim = ScoreDimension(
            dimension_id="factual_grounding",
            description="",
            weight=0.25,
            grader_type="deterministic",
            min_required_score=0.95,
            evidence_required=True,
            fail_closed_if_unknown=True,
        )
        score, evidence = read_dim_score_from_output(dim, {"output": {}})
        assert score == GRADER_UNKNOWN_SENTINEL
        assert evidence == []


# ---------------------------------------------------------------------------
# W1.P1 integration — packet.app_specific_eval populates when bound
# ---------------------------------------------------------------------------


class TestPacketAppSpecificEvalPopulation:
    @pytest.mark.parametrize("app_id,task_class", APPS_UNDER_TEST)
    def test_bound_pass_path_populates_and_passes(
        self, app_id: str, task_class: str,
    ) -> None:
        route = _base_route(app_id, task_class)
        packet = _packet_from_route(route, output=_all_pass_output(app_id, task_class))
        result = _attach_app_eval(packet)
        assert result.bound is True
        assert result.passed is True, f"{app_id}/{task_class}: fail_reasons={result.fail_reasons}"
        assert packet.app_specific_eval["bound"] is True
        assert packet.app_specific_eval["passed"] is True
        assert packet.app_specific_eval["app_id"] == app_id
        assert packet.app_specific_eval["task_class"] == task_class

    @pytest.mark.parametrize("app_id,task_class", APPS_UNDER_TEST)
    def test_bound_missing_dim_scores_fails_closed(
        self, app_id: str, task_class: str,
    ) -> None:
        """No dim_scores in output -> every dim UNKNOWN -> fail_closed_if_unknown
        dims FAIL. All 8 apps have at least one such guardrail dim."""
        route = _base_route(app_id, task_class)
        packet = _packet_from_route(route, output={})  # empty output
        result = _attach_app_eval(packet)
        assert result.bound is True
        assert result.passed is False, (
            f"{app_id}/{task_class} should fail-closed when no dim_scores provided"
        )
        assert packet.app_specific_eval["passed"] is False

    def test_unbound_packet_leaves_app_specific_eval_empty(self) -> None:
        """Packet with no rubric_ref -> evaluator returns bound=False -> we
        do NOT overwrite packet.app_specific_eval."""
        packet = ExitReviewPacket(
            source_type=SourceType.L2_SEALED_ARTIFACT,
            request_id="req-unbound",
            run_id="run-unbound",
            trace_root="trace-unbound",
            policy_hash="p",
            blueprint_hash="b",
        )
        result = _run_app_eval(packet)
        assert result.bound is False
        # unchanged default
        assert packet.app_specific_eval == {}


# ---------------------------------------------------------------------------
# W1.P3 — X2 aggregator DENIES on bound-and-failed app_specific_eval
# ---------------------------------------------------------------------------


class TestX2AppSpecificEvalFailureBlocks:
    def test_all_x1_pass_but_app_failed_denies(self) -> None:
        """10 X1 verdicts PASS + output missing a hard dim -> X2 returns DENY
        with rationale 'app_specific_eval_failed'. This is the headline audit
        BLOCKER fix: without W1.P3, this case ALLOWed."""
        route = _base_route("apps_rg", "resume_generation")
        packet = _packet_from_route(route, output={})  # forces fail-closed
        _attach_app_eval(packet)
        assert packet.app_specific_eval["passed"] is False
        decision = aggregate_decision(_pass_verdicts(), packet)
        assert decision.disposition is V6Disposition.DENY
        assert decision.rationale == "app_specific_eval_failed"
        assert decision.failed_gate_ids == ["APP_DOMAIN"]
        assert any(c.startswith("APP_DIM_FAIL") for c in decision.reason_codes)

    def test_all_x1_pass_and_app_passed_allows(self) -> None:
        """Control: all X1 PASS + all dims PASS -> ALLOW (X3D)."""
        route = _base_route("apps_rg", "resume_generation")
        packet = _packet_from_route(
            route, output=_all_pass_output("apps_rg", "resume_generation"),
        )
        _attach_app_eval(packet)
        assert packet.app_specific_eval["passed"] is True
        decision = aggregate_decision(_pass_verdicts(), packet)
        assert decision.disposition is V6Disposition.ALLOW

    def test_unbound_packet_x2_uses_generic_path(self) -> None:
        """Unbound app_specific_eval must not affect X2 at all."""
        packet = ExitReviewPacket(
            source_type=SourceType.L2_SEALED_ARTIFACT,
            request_id="r", run_id="r", trace_root="t",
            policy_hash="p", blueprint_hash="b",
            terminal_class="answer_only",
        )
        # packet.app_specific_eval is default {}
        decision = aggregate_decision(_pass_verdicts(), packet)
        # Generic path -> ALLOW
        assert decision.disposition is V6Disposition.ALLOW


# ---------------------------------------------------------------------------
# W1.P4 — X3 belt-and-braces: cannot emit ALLOW when app eval failed
# ---------------------------------------------------------------------------


class TestX3BeltAndBracesBlockAllow:
    def test_allow_decision_with_failed_app_eval_becomes_deny(self) -> None:
        """Even if upstream X2 somehow hands us an ALLOW decision, X3 must
        refuse to emit an X3AllowPacket when the bound app eval failed."""
        route = _base_route("apps_rg", "resume_generation")
        packet = _packet_from_route(route, output={})
        _attach_app_eval(packet)
        assert packet.app_specific_eval["passed"] is False

        # Forge an ALLOW decision directly (simulating upstream defect)
        fake_allow = AggregateDecision(
            disposition=V6Disposition.ALLOW,
            rationale="forged_allow_for_test",
        )
        x3 = build_x3_packet(packet, fake_allow)
        assert isinstance(x3, X3DenyPacket), (
            "X3 must reject ALLOW emission when app eval failed; "
            f"got {type(x3).__name__} instead"
        )
        assert "APP_DOMAIN" in x3.failed_gate_ids
        assert any(c.startswith("APP_DIM_FAIL") for c in x3.reason_codes)

    def test_commit_decision_with_failed_app_eval_becomes_deny(self) -> None:
        """Same check for COMMIT_REQUEST."""
        route = _base_route("apps_rg", "resume_generation")
        packet = _packet_from_route(route, output={})
        _attach_app_eval(packet)

        fake_commit = AggregateDecision(
            disposition=V6Disposition.COMMIT_REQUEST,
            rationale="forged_commit_for_test",
        )
        x3 = build_x3_packet(packet, fake_commit)
        assert isinstance(x3, X3DenyPacket)
        assert "APP_DOMAIN" in x3.failed_gate_ids

    def test_allow_decision_with_passed_app_eval_emits_allow(self) -> None:
        """Control: ALLOW decision + passed app eval -> X3AllowPacket."""
        route = _base_route("apps_rg", "resume_generation")
        packet = _packet_from_route(
            route, output=_all_pass_output("apps_rg", "resume_generation"),
        )
        _attach_app_eval(packet)
        assert packet.app_specific_eval["passed"] is True

        allow_decision = AggregateDecision(
            disposition=V6Disposition.ALLOW,
            rationale="answer_only_clear",
        )
        x3 = build_x3_packet(packet, allow_decision)
        assert isinstance(x3, X3AllowPacket)

    def test_allow_decision_unbound_packet_emits_allow(self) -> None:
        """Control: no app binding -> X3 behavior unchanged."""
        packet = ExitReviewPacket(
            source_type=SourceType.L2_SEALED_ARTIFACT,
            request_id="r", run_id="r", trace_root="t",
            policy_hash="p", blueprint_hash="b",
            terminal_class="answer_only",
        )
        allow_decision = AggregateDecision(
            disposition=V6Disposition.ALLOW,
            rationale="answer_only_clear",
        )
        x3 = build_x3_packet(packet, allow_decision)
        assert isinstance(x3, X3AllowPacket)
