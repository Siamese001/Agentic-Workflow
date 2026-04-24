"""W3.P2 tests — plan_abstain_multi_signal aggregation + priority."""

from __future__ import annotations

import pytest

from agentic_core.runtime.contracts.abstain_contract import (
    ACTION_CONTINUE,
    ACTION_EMIT_R5,
    DECISION_ABSTAIN,
    DECISION_PROCEED,
    R5_REASON_BUDGET_EXCEEDED,
    R5_REASON_CIRCUIT_BREAKER_OPEN,
    R5_REASON_CLARIFICATION_NEEDED,
    R5_REASON_CODES,
    R5_REASON_LOW_CONFIDENCE,
    R5_REASON_OOD_DETECTED,
    R5_REASON_TOXICITY_FLAGGED,
    plan_abstain,
    plan_abstain_multi_signal,
)


class TestBackCompatScalarAbstain:
    def test_plan_abstain_still_works(self) -> None:
        # Ensure the original single-signal primitive is untouched.
        decision = plan_abstain(0.40, 0.50)
        assert decision["decision"] == DECISION_ABSTAIN
        assert decision["action"] == "emit_r5_candidate"


class TestEmptySignals:
    def test_none_signals_proceeds(self) -> None:
        decision = plan_abstain_multi_signal(None)
        assert decision["decision"] == DECISION_PROCEED
        assert decision["action"] == ACTION_CONTINUE
        assert decision["triggered_reasons"] == ()
        assert decision["primary_reason"] == "none"

    def test_empty_dict_proceeds(self) -> None:
        decision = plan_abstain_multi_signal({})
        assert decision["decision"] == DECISION_PROCEED


class TestIndividualTriggers:
    def test_low_confidence_fires(self) -> None:
        decision = plan_abstain_multi_signal({"confidence": 0.30})
        assert decision["decision"] == DECISION_ABSTAIN
        assert decision["primary_reason"] == R5_REASON_LOW_CONFIDENCE
        assert decision["triggered_reasons"] == (R5_REASON_LOW_CONFIDENCE,)

    def test_high_confidence_does_not_fire(self) -> None:
        decision = plan_abstain_multi_signal({"confidence": 0.95})
        assert decision["decision"] == DECISION_PROCEED

    def test_ood_fires_at_threshold(self) -> None:
        decision = plan_abstain_multi_signal({"ood_score": 0.72})
        assert decision["primary_reason"] == R5_REASON_OOD_DETECTED

    def test_ood_below_threshold_does_not_fire(self) -> None:
        decision = plan_abstain_multi_signal({"ood_score": 0.20})
        assert decision["decision"] == DECISION_PROCEED

    def test_budget_fires(self) -> None:
        decision = plan_abstain_multi_signal({"budget_exceeded": True})
        assert decision["primary_reason"] == R5_REASON_BUDGET_EXCEEDED

    def test_circuit_breaker_fires(self) -> None:
        decision = plan_abstain_multi_signal({"circuit_breaker_open": True})
        assert decision["primary_reason"] == R5_REASON_CIRCUIT_BREAKER_OPEN

    def test_clarification_fires(self) -> None:
        decision = plan_abstain_multi_signal({"clarification_needed": True})
        assert decision["primary_reason"] == R5_REASON_CLARIFICATION_NEEDED

    def test_toxicity_fires(self) -> None:
        decision = plan_abstain_multi_signal({"toxicity_flagged": True})
        assert decision["primary_reason"] == R5_REASON_TOXICITY_FLAGGED


class TestPriorityOrdering:
    def test_toxicity_beats_low_confidence(self) -> None:
        decision = plan_abstain_multi_signal(
            {"toxicity_flagged": True, "confidence": 0.30},
        )
        assert decision["primary_reason"] == R5_REASON_TOXICITY_FLAGGED
        # But both are recorded.
        assert set(decision["triggered_reasons"]) == {
            R5_REASON_TOXICITY_FLAGGED,
            R5_REASON_LOW_CONFIDENCE,
        }

    def test_circuit_breaker_beats_budget(self) -> None:
        decision = plan_abstain_multi_signal(
            {"circuit_breaker_open": True, "budget_exceeded": True},
        )
        assert decision["primary_reason"] == R5_REASON_CIRCUIT_BREAKER_OPEN

    def test_budget_beats_ood(self) -> None:
        decision = plan_abstain_multi_signal(
            {"budget_exceeded": True, "ood_score": 0.80},
        )
        assert decision["primary_reason"] == R5_REASON_BUDGET_EXCEEDED

    def test_priority_stable_across_order(self) -> None:
        # Dict ordering should not change primary_reason.
        a = plan_abstain_multi_signal(
            {"confidence": 0.30, "toxicity_flagged": True},
        )
        b = plan_abstain_multi_signal(
            {"toxicity_flagged": True, "confidence": 0.30},
        )
        assert a["primary_reason"] == b["primary_reason"]


class TestThresholdOverrides:
    def test_custom_confidence_threshold(self) -> None:
        decision = plan_abstain_multi_signal(
            {"confidence": 0.65, "confidence_threshold": 0.70},
        )
        assert decision["primary_reason"] == R5_REASON_LOW_CONFIDENCE

    def test_custom_ood_threshold(self) -> None:
        decision = plan_abstain_multi_signal(
            {"ood_score": 0.55, "ood_threshold": 0.50},
        )
        assert decision["primary_reason"] == R5_REASON_OOD_DETECTED

    def test_ood_score_out_of_range_rejected(self) -> None:
        with pytest.raises(ValueError, match="ood_score"):
            plan_abstain_multi_signal({"ood_score": 1.5})

    def test_confidence_out_of_range_rejected(self) -> None:
        with pytest.raises(ValueError, match="confidence"):
            plan_abstain_multi_signal({"confidence": 2.0})


class TestReasonCodesContract:
    def test_every_primary_reason_in_closed_set(self) -> None:
        triggers = [
            {"confidence": 0.30},
            {"ood_score": 0.80},
            {"budget_exceeded": True},
            {"circuit_breaker_open": True},
            {"clarification_needed": True},
            {"toxicity_flagged": True},
        ]
        for t in triggers:
            decision = plan_abstain_multi_signal(t)
            assert decision["primary_reason"] in R5_REASON_CODES

    def test_r5_reason_codes_closed_set_has_six(self) -> None:
        assert len(R5_REASON_CODES) == 6


class TestMultipleTriggers:
    def test_reason_list_includes_all_firing_triggers(self) -> None:
        decision = plan_abstain_multi_signal(
            {
                "confidence": 0.30,
                "ood_score": 0.80,
                "budget_exceeded": True,
            },
        )
        assert R5_REASON_LOW_CONFIDENCE in decision["triggered_reasons"]
        assert R5_REASON_OOD_DETECTED in decision["triggered_reasons"]
        assert R5_REASON_BUDGET_EXCEEDED in decision["triggered_reasons"]
        # Priority: budget (3) > ood (4) > low_confidence (6).
        assert decision["primary_reason"] == R5_REASON_BUDGET_EXCEEDED
