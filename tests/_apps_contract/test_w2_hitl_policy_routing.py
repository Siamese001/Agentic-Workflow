"""W2.P5 verification — hitl_policy routing at X2.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-eval-harness-parity-f8d4a2.md`` W2.P5.

Proves:

- ``hitl_policy: required_always`` on a bound failed run → X2 returns
  ESCALATE (not DENY).
- ``hitl_policy: required_on_low`` with SOFT fail_reasons (threshold /
  overall-below) → ESCALATE.
- ``hitl_policy: required_on_low`` with HARD guardrail fail_reasons
  (unknown_fail_closed, evidence_required_but_empty) → DENY.
- ``hitl_policy: none`` → DENY as before.
- The carried ``AppSpecificEvalResult.hitl_policy`` is populated from the
  resolved threshold profile.
"""

from __future__ import annotations

from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
    AppSpecificEvalResult,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateResult,
    GateVerdict,
    SourceType,
    V6Disposition,
)
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import aggregate_decision


def _pass_verdicts() -> list[GateVerdict]:
    return [
        GateVerdict(gate_id=g, result=GateResult.PASS)
        for g in ("X1A", "X1B", "X1C", "X1D", "X1E", "X1F", "X1G", "X1H", "X1I", "X1J")
    ]


def _packet_with_ase(
    *,
    passed: bool,
    fail_reasons: list[str],
    hitl_policy: str = "none",
) -> ExitReviewPacket:
    ase = AppSpecificEvalResult(
        bound=True,
        app_id="apps_rg",
        task_class="resume_generation",
        rubric_ref="aer::apps_rg::resume_generation::v1",
        threshold_profile_ref="atp::apps_rg::resume_generation::v1",
        overall_score=0.72,
        overall_pass_threshold=0.80,
        passed=passed,
        fail_reasons=list(fail_reasons),
        hitl_policy=hitl_policy,
    )
    packet = ExitReviewPacket(
        source_type=SourceType.L2_SEALED_ARTIFACT,
        request_id="r", run_id="r", trace_root="t",
        policy_hash="p", blueprint_hash="b",
        terminal_class="answer_only",
    )
    packet.app_specific_eval = ase.to_packet_dict()
    return packet


class TestHitlPolicyNone:
    def test_none_routes_to_deny(self) -> None:
        packet = _packet_with_ase(
            passed=False,
            fail_reasons=["overall_below_threshold::score=0.72<threshold=0.80"],
            hitl_policy="none",
        )
        decision = aggregate_decision(_pass_verdicts(), packet)
        assert decision.disposition is V6Disposition.DENY
        assert decision.rationale == "app_specific_eval_failed"


class TestHitlPolicyRequiredOnLow:
    def test_soft_fail_escalates(self) -> None:
        packet = _packet_with_ase(
            passed=False,
            fail_reasons=["overall_below_threshold::score=0.72<threshold=0.80"],
            hitl_policy="required_on_low",
        )
        decision = aggregate_decision(_pass_verdicts(), packet)
        assert decision.disposition is V6Disposition.ESCALATE
        assert decision.rationale == "hitl_required_on_low"
        assert "HUMAN_REQUIRED" in decision.reason_codes
        assert decision.failed_gate_ids == ["APP_DOMAIN"]

    def test_threshold_min_soft_fail_escalates(self) -> None:
        packet = _packet_with_ase(
            passed=False,
            fail_reasons=["threshold_min::executive_positioning::score=0.55<min=0.70"],
            hitl_policy="required_on_low",
        )
        decision = aggregate_decision(_pass_verdicts(), packet)
        assert decision.disposition is V6Disposition.ESCALATE

    def test_dimension_fail_soft_escalates(self) -> None:
        packet = _packet_with_ase(
            passed=False,
            fail_reasons=["dimension_fail::role_alignment::below_rubric_min(0.700)"],
            hitl_policy="required_on_low",
        )
        decision = aggregate_decision(_pass_verdicts(), packet)
        assert decision.disposition is V6Disposition.ESCALATE

    def test_guardrail_unknown_fail_closed_still_denies(self) -> None:
        """hitl_policy=required_on_low must NOT escape a guardrail UNKNOWN
        fail-closed. The human should never be asked to approve a run where
        a hard guardrail (no_fabrication / no_sensitive_targeting) came
        back UNKNOWN."""
        packet = _packet_with_ase(
            passed=False,
            fail_reasons=[
                "dimension_fail::no_fabrication::unknown_fail_closed",
            ],
            hitl_policy="required_on_low",
        )
        decision = aggregate_decision(_pass_verdicts(), packet)
        assert decision.disposition is V6Disposition.DENY
        assert decision.rationale == "app_specific_eval_failed"

    def test_guardrail_evidence_missing_still_denies(self) -> None:
        packet = _packet_with_ase(
            passed=False,
            fail_reasons=[
                "dimension_fail::factual_grounding::evidence_required_but_empty",
            ],
            hitl_policy="required_on_low",
        )
        decision = aggregate_decision(_pass_verdicts(), packet)
        assert decision.disposition is V6Disposition.DENY

    def test_mixed_soft_plus_hard_denies(self) -> None:
        """If EITHER reason is hard, DENY — even if other reasons are soft."""
        packet = _packet_with_ase(
            passed=False,
            fail_reasons=[
                "overall_below_threshold::score=0.72<threshold=0.80",
                "dimension_fail::no_fabrication::unknown_fail_closed",
            ],
            hitl_policy="required_on_low",
        )
        decision = aggregate_decision(_pass_verdicts(), packet)
        assert decision.disposition is V6Disposition.DENY


class TestHitlPolicyRequiredAlways:
    def test_soft_fail_escalates(self) -> None:
        packet = _packet_with_ase(
            passed=False,
            fail_reasons=["overall_below_threshold::score=0.72<threshold=0.80"],
            hitl_policy="required_always",
        )
        decision = aggregate_decision(_pass_verdicts(), packet)
        assert decision.disposition is V6Disposition.ESCALATE
        assert decision.rationale == "hitl_required_always"

    def test_hard_fail_still_denies(self) -> None:
        """required_always does NOT rescue guardrail violations."""
        packet = _packet_with_ase(
            passed=False,
            fail_reasons=["dimension_fail::no_fabrication::unknown_fail_closed"],
            hitl_policy="required_always",
        )
        decision = aggregate_decision(_pass_verdicts(), packet)
        assert decision.disposition is V6Disposition.DENY

    def test_passed_run_does_not_escalate(self) -> None:
        """required_always applies only to failed runs. A passing bound run
        still ALLOWs — HITL is for review of low-quality output, not for
        routine approval of every run."""
        packet = _packet_with_ase(
            passed=True,
            fail_reasons=[],
            hitl_policy="required_always",
        )
        decision = aggregate_decision(_pass_verdicts(), packet)
        assert decision.disposition is V6Disposition.ALLOW


class TestHitlPolicyCarrier:
    def test_to_packet_dict_includes_hitl_policy(self) -> None:
        result = AppSpecificEvalResult(
            bound=True,
            hitl_policy="required_on_low",
        )
        d = result.to_packet_dict()
        assert d["hitl_policy"] == "required_on_low"

    def test_default_hitl_policy_is_none(self) -> None:
        result = AppSpecificEvalResult(bound=True)
        assert result.hitl_policy == "none"
        assert result.to_packet_dict()["hitl_policy"] == "none"
