"""Unit tests for agentic_core.L3_orchestration.exit_eval.v6.x2_matrix.

Wave 3.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — high-fan-in exit_eval
module (``x2_matrix``, fan_in=19). The X2 aggregate decision matrix maps a list
of X1 gate verdicts + an ExitReviewPacket to exactly ONE X3 disposition. Covers
the reason-code frozensets, the AggregateDecision carrier, the app-specific-eval
and HITL-routing helpers, and the full priority ladder (hard-fail → safe-abstain
→ escalate → non-hard-fail → commit-request → allow). UNKNOWN on a material gate
never silently passes.
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateResult,
    GateVerdict,
    SourceType,
    V6Disposition,
)
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import (
    AggregateDecision,
    aggregate_decision,
)


def _packet(**overrides: object) -> ExitReviewPacket:
    base: dict = {"source_type": SourceType.L2_SEALED_ARTIFACT}
    base.update(overrides)
    return ExitReviewPacket(**base)  # type: ignore[arg-type]


def _verdict(gate_id: str, result: GateResult, *codes: str) -> GateVerdict:
    return GateVerdict(gate_id=gate_id, result=result, reason_codes=list(codes))


def _all_pass(gate_ids: tuple[str, ...]) -> list[GateVerdict]:
    return [_verdict(g, GateResult.PASS) for g in gate_ids]


_X1_ALL = tuple(f"X1{c}" for c in "ABCDEFGHIJ")


class TestAggregateDecisionCarrier:
    def test_defaults(self) -> None:
        d = AggregateDecision(disposition=V6Disposition.ALLOW)
        assert d.failed_gate_ids == []
        assert d.reason_codes == []
        assert d.triggering_verdicts == []
        assert d.rationale == ""
        assert d.requires_uwg_handoff is False
        assert d.x1_checkout_result is None

    def test_independent_default_lists(self) -> None:
        a = AggregateDecision(disposition=V6Disposition.ALLOW)
        b = AggregateDecision(disposition=V6Disposition.ALLOW)
        a.reason_codes.append("X")
        assert b.reason_codes == []


class TestAllowPath:
    def test_answer_only_all_pass_allows(self) -> None:
        decision = aggregate_decision(_all_pass(_X1_ALL), _packet(terminal_class="answer_only"))
        assert decision.disposition is V6Disposition.ALLOW
        assert decision.rationale == "answer_only_clear"
        assert decision.failed_gate_ids == []

    def test_empty_verdicts_answer_only_allows(self) -> None:
        decision = aggregate_decision([], _packet(terminal_class="answer_only"))
        assert decision.disposition is V6Disposition.ALLOW


class TestHardFailPath:
    @pytest.mark.parametrize(
        "code",
        ["SANDBOX_BREACH", "UNAUTHORIZED_MUTATION", "PROMPT_INJECTION_DETECTED", "UNGROUNDED"],
    )
    def test_hard_fail_code_denies(self, code: str) -> None:
        verdicts = _all_pass(_X1_ALL[:-1]) + [_verdict("X1J", GateResult.FAIL, code)]
        decision = aggregate_decision(verdicts, _packet(terminal_class="answer_only"))
        assert decision.disposition is V6Disposition.DENY
        assert decision.rationale == "hard_fail_condition"
        assert code in decision.reason_codes

    def test_non_replayable_denies_for_all_terminal_classes(self) -> None:
        verdicts = _all_pass(_X1_ALL[:-1]) + [_verdict("X1J", GateResult.FAIL, "NON_REPLAYABLE")]
        # Replay determinism is required on every terminal class, so the
        # NON_REPLAYABLE fail must never fall through to ALLOW.
        low = aggregate_decision(verdicts, _packet(terminal_class="answer_only"))
        assert low.disposition is V6Disposition.DENY
        assert low.rationale == "hard_fail_condition"
        # durable_write remains a hard fail as well.
        high = aggregate_decision(verdicts, _packet(terminal_class="durable_write"))
        assert high.disposition is V6Disposition.DENY
        assert high.rationale == "hard_fail_condition"


class TestSafeAbstainPath:
    def test_evidence_empty_safe_abstains(self) -> None:
        verdicts = _all_pass(_X1_ALL[:-1]) + [_verdict("X1J", GateResult.FAIL, "EVIDENCE_EMPTY")]
        decision = aggregate_decision(verdicts, _packet(terminal_class="answer_only"))
        assert decision.disposition is V6Disposition.SAFE_ABSTAIN
        assert decision.rationale == "safe_abstain_evidence_class"

    def test_other_fail_suppresses_safe_abstain(self) -> None:
        # An evidence-class warn alongside a real non-hard fail → not safe-abstain.
        verdicts = _all_pass(_X1_ALL[:-2]) + [
            _verdict("X1I", GateResult.WARN, "WEAK_EVIDENCE_NO_CAVEAT"),
            _verdict("X1J", GateResult.FAIL, "SOME_OTHER_FAIL"),
        ]
        decision = aggregate_decision(verdicts, _packet(terminal_class="answer_only"))
        assert decision.disposition is V6Disposition.DENY


class TestEscalatePath:
    def test_escalate_code_escalates(self) -> None:
        verdicts = _all_pass(_X1_ALL[:-1]) + [_verdict("X1J", GateResult.WARN, "JUDGE_ABSTAINED")]
        decision = aggregate_decision(verdicts, _packet(terminal_class="answer_only"))
        assert decision.disposition is V6Disposition.ESCALATE
        assert decision.rationale == "escalation_required"
        assert "JUDGE_ABSTAINED" in decision.reason_codes

    def test_material_unknown_escalates(self) -> None:
        # X1D UNKNOWN is a material gate → escalate even with no escalate codes.
        verdicts = [
            _verdict(g, GateResult.PASS) if g != "X1D" else _verdict("X1D", GateResult.UNKNOWN)
            for g in _X1_ALL
        ]
        decision = aggregate_decision(verdicts, _packet(terminal_class="answer_only"))
        assert decision.disposition is V6Disposition.ESCALATE
        assert "UNKNOWN_MATERIAL_GATE" in decision.reason_codes


class TestNonHardFailPath:
    def test_unrecognized_fail_code_denies(self) -> None:
        verdicts = _all_pass(_X1_ALL[:-1]) + [_verdict("X1J", GateResult.FAIL, "WEIRD_CODE")]
        decision = aggregate_decision(verdicts, _packet(terminal_class="answer_only"))
        assert decision.disposition is V6Disposition.DENY
        assert decision.rationale == "gate_fail_non_hard"
        assert "WEIRD_CODE" in decision.reason_codes


class TestCommitRequestPath:
    def test_commit_path_clear_requests_commit(self) -> None:
        decision = aggregate_decision(_all_pass(_X1_ALL), _packet(terminal_class="durable_write"))
        assert decision.disposition is V6Disposition.COMMIT_REQUEST
        assert decision.requires_uwg_handoff is True
        assert decision.rationale == "commit_path_clear"

    def test_commit_path_blocked_when_required_gate_not_pass(self) -> None:
        # X1G (required for commit) UNKNOWN — but X1G is material so it escalates
        # before reaching commit logic. Use X1B FAIL with a non-hard code instead
        # to reach the commit-precondition DENY would require all non-fail; so
        # assert the escalate-first ordering with a material unknown on X1G.
        verdicts = [
            _verdict(g, GateResult.PASS) if g != "X1G" else _verdict("X1G", GateResult.UNKNOWN)
            for g in _X1_ALL
        ]
        decision = aggregate_decision(verdicts, _packet(terminal_class="durable_write"))
        # X1G unknown is material → escalate.
        assert decision.disposition is V6Disposition.ESCALATE

    def test_commit_preconditions_unmet_denies(self) -> None:
        # X1B WARN is neither escalate nor fail code → reaches commit-precondition
        # check, which blocks because X1B is required-PASS.
        verdicts = [
            _verdict(g, GateResult.PASS) if g != "X1B" else _verdict("X1B", GateResult.WARN)
            for g in _X1_ALL
        ]
        decision = aggregate_decision(verdicts, _packet(terminal_class="durable_write"))
        assert decision.disposition is V6Disposition.DENY
        assert decision.rationale == "commit_path_preconditions_unmet"
        assert "X1B_NOT_PASS" in decision.reason_codes


class TestAppSpecificEval:
    def test_bound_failed_app_eval_denies(self) -> None:
        ase = {"bound": True, "passed": False, "fail_reasons": ["no_fabrication_below_min"]}
        decision = aggregate_decision(
            _all_pass(_X1_ALL), _packet(terminal_class="answer_only", app_specific_eval=ase)
        )
        assert decision.disposition is V6Disposition.DENY
        assert decision.rationale == "app_specific_eval_failed"
        assert "APP_DIM_FAIL::no_fabrication_below_min" in decision.reason_codes

    def test_bound_passed_app_eval_does_not_block(self) -> None:
        ase = {"bound": True, "passed": True, "fail_reasons": []}
        decision = aggregate_decision(
            _all_pass(_X1_ALL), _packet(terminal_class="answer_only", app_specific_eval=ase)
        )
        assert decision.disposition is V6Disposition.ALLOW

    def test_unbound_app_eval_ignored(self) -> None:
        ase = {"bound": False, "passed": False, "fail_reasons": ["x"]}
        decision = aggregate_decision(
            _all_pass(_X1_ALL), _packet(terminal_class="answer_only", app_specific_eval=ase)
        )
        assert decision.disposition is V6Disposition.ALLOW

    def test_hitl_required_always_escalates_over_deny(self) -> None:
        ase = {
            "bound": True,
            "passed": False,
            "hitl_policy": "required_always",
            "fail_reasons": ["overall_below_threshold"],
        }
        decision = aggregate_decision(
            _all_pass(_X1_ALL), _packet(terminal_class="answer_only", app_specific_eval=ase)
        )
        assert decision.disposition is V6Disposition.ESCALATE
        assert decision.rationale == "hitl_required_always"
        assert "HUMAN_REQUIRED" in decision.reason_codes

    def test_hitl_required_on_low_soft_only_escalates(self) -> None:
        ase = {
            "bound": True,
            "passed": False,
            "hitl_policy": "required_on_low",
            "fail_reasons": ["threshold_min"],
        }
        decision = aggregate_decision(
            _all_pass(_X1_ALL), _packet(terminal_class="answer_only", app_specific_eval=ase)
        )
        assert decision.disposition is V6Disposition.ESCALATE
        assert decision.rationale == "hitl_required_on_low"

    def test_hard_guardrail_fail_denies_despite_hitl_policy(self) -> None:
        ase = {
            "bound": True,
            "passed": False,
            "hitl_policy": "required_always",
            "fail_reasons": ["dimension_fail::no_fabrication::unknown_fail_closed"],
        }
        decision = aggregate_decision(
            _all_pass(_X1_ALL), _packet(terminal_class="answer_only", app_specific_eval=ase)
        )
        # Hard guardrail substring present → DENY path, never escalate.
        assert decision.disposition is V6Disposition.DENY
        assert decision.rationale == "app_specific_eval_failed"
