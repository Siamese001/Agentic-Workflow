"""Unit tests for agentic_core.runtime.contracts.abstain_contract.

Targets Wave-4 / Phase P10. Source: 456 lines, fan_in=45 (L_RUNTIME, impact 78.8).
Pure, stateless module — exhaustive behavioral coverage.
"""

from __future__ import annotations

import pytest

from hypothesis import given, strategies as st

from agentic_core.runtime.contracts.abstain_contract import (
    ACTION_CONTINUE,
    ACTION_EMIT_R5,
    ACTION_REQUEST_CLARIFICATION,
    DECISION_ABSTAIN,
    DECISION_CLARIFY,
    DECISION_PROCEED,
    DEFAULT_ABSTAIN_THRESHOLD,
    DEFAULT_AMBIGUITY_THRESHOLD,
    R5_REASON_BUDGET_EXCEEDED,
    R5_REASON_CIRCUIT_BREAKER_OPEN,
    R5_REASON_CLARIFICATION_NEEDED,
    R5_REASON_CODES,
    R5_REASON_LOW_CONFIDENCE,
    R5_REASON_OOD_DETECTED,
    R5_REASON_TOXICITY_FLAGGED,
    plan_abstain,
    plan_abstain_multi_signal,
    plan_clarify,
)


class TestConstants:
    def test_default_abstain_threshold(self) -> None:
        assert DEFAULT_ABSTAIN_THRESHOLD == 0.50

    def test_default_ambiguity_threshold(self) -> None:
        assert DEFAULT_AMBIGUITY_THRESHOLD == 0.60

    def test_action_strings(self) -> None:
        assert ACTION_EMIT_R5 == "emit_r5_candidate"
        assert ACTION_CONTINUE == "continue"
        assert ACTION_REQUEST_CLARIFICATION == "request_clarification"

    def test_decision_strings(self) -> None:
        assert DECISION_ABSTAIN == "abstain"
        assert DECISION_PROCEED == "proceed"
        assert DECISION_CLARIFY == "clarify"

    def test_r5_reason_codes_complete(self) -> None:
        assert R5_REASON_CODES == frozenset(
            {
                R5_REASON_LOW_CONFIDENCE,
                R5_REASON_OOD_DETECTED,
                R5_REASON_BUDGET_EXCEEDED,
                R5_REASON_CIRCUIT_BREAKER_OPEN,
                R5_REASON_CLARIFICATION_NEEDED,
                R5_REASON_TOXICITY_FLAGGED,
            }
        )


class TestPlanAbstain:
    def test_below_threshold_abstains(self) -> None:
        d = plan_abstain(0.3, 0.5)
        assert d["decision"] == "abstain"
        assert d["action"] == "emit_r5_candidate"
        assert d["confidence"] == 0.3
        assert d["threshold"] == 0.5
        assert "below" in d["reason"]

    def test_at_threshold_proceeds(self) -> None:
        # confidence == threshold → proceed (strictly-below triggers abstain)
        d = plan_abstain(0.5, 0.5)
        assert d["decision"] == "proceed"
        assert d["action"] == "continue"

    def test_above_threshold_proceeds(self) -> None:
        d = plan_abstain(0.9, 0.5)
        assert d["decision"] == "proceed"
        assert d["action"] == "continue"
        assert "at or above" in d["reason"]

    def test_default_threshold_used(self) -> None:
        d = plan_abstain(0.4)
        assert d["threshold"] == DEFAULT_ABSTAIN_THRESHOLD
        assert d["decision"] == "abstain"

    def test_reason_hint_overrides_default(self) -> None:
        d = plan_abstain(0.3, 0.5, reason_hint="custom explanation")
        assert d["reason"] == "custom explanation"

    @pytest.mark.parametrize("bad", [-0.1, 1.1, 2.0, -5.0])
    def test_invalid_confidence_raises(self, bad: float) -> None:
        with pytest.raises(ValueError, match="confidence must be"):
            plan_abstain(bad, 0.5)

    @pytest.mark.parametrize("bad", [-0.1, 1.1])
    def test_invalid_threshold_raises(self, bad: float) -> None:
        with pytest.raises(ValueError, match="threshold must be"):
            plan_abstain(0.5, bad)

    def test_boundary_values_accepted(self) -> None:
        d1 = plan_abstain(0.0, 0.0)
        assert d1["decision"] == "proceed"
        d2 = plan_abstain(1.0, 1.0)
        assert d2["decision"] == "proceed"
        d3 = plan_abstain(0.0, 1.0)
        assert d3["decision"] == "abstain"


class TestPlanClarify:
    def test_high_ambiguity_triggers_clarify(self) -> None:
        d = plan_clarify(confidence=0.8, ambiguity_score=0.9)
        assert d["decision"] == "clarify"
        assert d["action"] == "request_clarification"
        assert d["ambiguity_score"] == 0.9

    def test_low_ambiguity_proceeds(self) -> None:
        d = plan_clarify(confidence=0.8, ambiguity_score=0.2)
        assert d["decision"] == "proceed"
        assert d["action"] == "continue"

    def test_at_threshold_triggers_clarify(self) -> None:
        # >= threshold triggers clarify
        d = plan_clarify(confidence=0.9, ambiguity_score=0.60)
        assert d["decision"] == "clarify"

    def test_default_ambiguity_threshold(self) -> None:
        d = plan_clarify(0.5, 0.3)
        assert d["ambiguity_threshold"] == DEFAULT_AMBIGUITY_THRESHOLD

    def test_reason_hint_overrides(self) -> None:
        d = plan_clarify(0.5, 0.9, reason_hint="user utterance ambiguous")
        assert d["reason"] == "user utterance ambiguous"

    @pytest.mark.parametrize(
        "field,bad",
        [
            ("confidence", -0.1),
            ("confidence", 1.5),
            ("ambiguity_score", -0.1),
            ("ambiguity_score", 1.1),
        ],
    )
    def test_invalid_numeric_raises(self, field: str, bad: float) -> None:
        kwargs = {"confidence": 0.5, "ambiguity_score": 0.5}
        kwargs[field] = bad
        with pytest.raises(ValueError, match=f"{field} must be"):
            plan_clarify(**kwargs)  # type: ignore[arg-type]

    def test_invalid_threshold_raises(self) -> None:
        with pytest.raises(ValueError, match="threshold must be"):
            plan_clarify(0.5, 0.5, threshold=1.5)


class TestPlanAbstainMultiSignal:
    def test_none_signals_proceeds(self) -> None:
        d = plan_abstain_multi_signal(None)
        assert d["decision"] == "proceed"
        assert d["triggered_reasons"] == ()
        assert d["primary_reason"] == "none"
        assert d["action"] == "continue"

    def test_empty_signals_proceeds(self) -> None:
        d = plan_abstain_multi_signal({})
        assert d["decision"] == "proceed"
        assert d["primary_reason"] == "none"

    def test_toxicity_wins_primary(self) -> None:
        d = plan_abstain_multi_signal(
            {
                "toxicity_flagged": True,
                "budget_exceeded": True,
                "confidence": 0.3,
            }
        )
        assert d["decision"] == "abstain"
        assert d["primary_reason"] == R5_REASON_TOXICITY_FLAGGED
        # All three triggers recorded
        assert R5_REASON_TOXICITY_FLAGGED in d["triggered_reasons"]
        assert R5_REASON_BUDGET_EXCEEDED in d["triggered_reasons"]
        assert R5_REASON_LOW_CONFIDENCE in d["triggered_reasons"]

    def test_circuit_breaker_beats_budget(self) -> None:
        d = plan_abstain_multi_signal(
            {
                "circuit_breaker_open": True,
                "budget_exceeded": True,
            }
        )
        assert d["primary_reason"] == R5_REASON_CIRCUIT_BREAKER_OPEN

    def test_ood_score_trigger(self) -> None:
        d = plan_abstain_multi_signal({"ood_score": 0.8})
        assert d["decision"] == "abstain"
        assert d["primary_reason"] == R5_REASON_OOD_DETECTED

    def test_ood_score_below_threshold(self) -> None:
        d = plan_abstain_multi_signal({"ood_score": 0.1, "ood_threshold": 0.7})
        assert d["decision"] == "proceed"

    def test_custom_ood_threshold(self) -> None:
        d = plan_abstain_multi_signal({"ood_score": 0.5, "ood_threshold": 0.4})
        assert d["decision"] == "abstain"
        assert d["primary_reason"] == R5_REASON_OOD_DETECTED

    def test_clarification_trigger(self) -> None:
        d = plan_abstain_multi_signal({"clarification_needed": True})
        assert d["primary_reason"] == R5_REASON_CLARIFICATION_NEEDED

    def test_low_confidence_only(self) -> None:
        d = plan_abstain_multi_signal({"confidence": 0.2, "confidence_threshold": 0.5})
        assert d["decision"] == "abstain"
        assert d["primary_reason"] == R5_REASON_LOW_CONFIDENCE

    def test_priority_order_is_stable(self) -> None:
        # All 6 triggers firing — should be sorted by priority
        d = plan_abstain_multi_signal(
            {
                "confidence": 0.1,
                "ood_score": 0.9,
                "budget_exceeded": True,
                "circuit_breaker_open": True,
                "clarification_needed": True,
                "toxicity_flagged": True,
            }
        )
        priority = (
            R5_REASON_TOXICITY_FLAGGED,
            R5_REASON_CIRCUIT_BREAKER_OPEN,
            R5_REASON_BUDGET_EXCEEDED,
            R5_REASON_OOD_DETECTED,
            R5_REASON_CLARIFICATION_NEEDED,
            R5_REASON_LOW_CONFIDENCE,
        )
        assert tuple(d["triggered_reasons"]) == priority

    @pytest.mark.parametrize(
        "key,bad",
        [
            ("confidence", -0.1),
            ("confidence", 1.5),
            ("confidence_threshold", -0.1),
            ("confidence_threshold", 1.1),
            ("ood_score", -0.1),
            ("ood_score", 1.1),
        ],
    )
    def test_invalid_numeric_raises(self, key: str, bad: float) -> None:
        signals: dict = {key: bad}
        with pytest.raises(ValueError, match=f"{key} must be"):
            plan_abstain_multi_signal(signals)  # type: ignore[arg-type]

    @pytest.mark.parametrize("bad", [-0.1, 1.1])
    def test_invalid_ood_threshold_raises_when_ood_score_provided(self, bad: float) -> None:
        # ood_threshold is only validated when ood_score is also provided
        signals: dict = {"ood_score": 0.5, "ood_threshold": bad}
        with pytest.raises(ValueError, match="ood_threshold must be"):
            plan_abstain_multi_signal(signals)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Property-based tests (hypothesis) — pure-function invariants
# ---------------------------------------------------------------------------

_unit_interval = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)


class TestPlanAbstainProperties:
    @given(confidence=_unit_interval, threshold=_unit_interval)
    def test_decision_matches_comparison(self, confidence: float, threshold: float) -> None:
        # Contract: confidence < threshold → abstain; otherwise proceed.
        d = plan_abstain(confidence, threshold)
        if confidence < threshold:
            assert d["decision"] == DECISION_ABSTAIN
            assert d["action"] == ACTION_EMIT_R5
        else:
            assert d["decision"] == DECISION_PROCEED
            assert d["action"] == ACTION_CONTINUE

    @given(confidence=_unit_interval, threshold=_unit_interval)
    def test_echo_fields_are_floats_in_range(self, confidence: float, threshold: float) -> None:
        d = plan_abstain(confidence, threshold)
        assert isinstance(d["confidence"], float)
        assert isinstance(d["threshold"], float)
        assert 0.0 <= d["confidence"] <= 1.0
        assert 0.0 <= d["threshold"] <= 1.0

    @given(confidence=_unit_interval, threshold=_unit_interval)
    def test_decision_deterministic(self, confidence: float, threshold: float) -> None:
        # Pure function — same inputs always produce same output.
        d1 = plan_abstain(confidence, threshold)
        d2 = plan_abstain(confidence, threshold)
        assert d1 == d2


class TestPlanClarifyProperties:
    @given(
        confidence=_unit_interval,
        ambiguity=_unit_interval,
        threshold=_unit_interval,
    )
    def test_clarify_iff_ambiguity_at_or_above_threshold(
        self, confidence: float, ambiguity: float, threshold: float
    ) -> None:
        d = plan_clarify(confidence, ambiguity, threshold)
        if ambiguity >= threshold:
            assert d["decision"] == DECISION_CLARIFY
            assert d["action"] == ACTION_REQUEST_CLARIFICATION
        else:
            assert d["decision"] == DECISION_PROCEED
            assert d["action"] == ACTION_CONTINUE


class TestPlanAbstainMultiSignalProperties:
    @given(conf=_unit_interval, conf_threshold=_unit_interval)
    def test_low_confidence_only_matches_plan_abstain(self, conf: float, conf_threshold: float) -> None:
        # With only confidence/threshold set, multi-signal must agree with
        # scalar plan_abstain on the abstain/proceed verdict.
        scalar = plan_abstain(conf, conf_threshold)
        multi = plan_abstain_multi_signal({"confidence": conf, "confidence_threshold": conf_threshold})
        assert scalar["decision"] == multi["decision"]

    @given(toxic=st.booleans(), circuit=st.booleans(), budget=st.booleans())
    def test_any_critical_boolean_trigger_causes_abstain(
        self, toxic: bool, circuit: bool, budget: bool
    ) -> None:
        # If any of the three hard booleans is True, decision MUST be abstain.
        d = plan_abstain_multi_signal(
            {
                "toxicity_flagged": toxic,
                "circuit_breaker_open": circuit,
                "budget_exceeded": budget,
            }
        )
        if toxic or circuit or budget:
            assert d["decision"] == DECISION_ABSTAIN
            assert d["primary_reason"] in R5_REASON_CODES
        else:
            assert d["decision"] == DECISION_PROCEED
            assert d["primary_reason"] == "none"

    @given(toxic=st.booleans(), circuit=st.booleans())
    def test_toxicity_wins_over_circuit(self, toxic: bool, circuit: bool) -> None:
        d = plan_abstain_multi_signal(
            {
                "toxicity_flagged": toxic,
                "circuit_breaker_open": circuit,
            }
        )
        if toxic:
            assert d["primary_reason"] == R5_REASON_TOXICITY_FLAGGED
        elif circuit:
            assert d["primary_reason"] == R5_REASON_CIRCUIT_BREAKER_OPEN
