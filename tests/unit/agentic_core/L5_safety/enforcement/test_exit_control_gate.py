import pytest

_exit_control_gate = pytest.importorskip(
    "agentic_core.L5_safety.enforcement.exit_control_gate",
    reason="Requires ExitControlGate implementation from the monorepo checkout.",
)
ExitControlGate = _exit_control_gate.ExitControlGate

_exit_disposition_types = pytest.importorskip(
    "agentic_core.L5_safety.types.exit_disposition_types",
    reason="Requires exit disposition types from the monorepo checkout.",
)
ExitDisposition = _exit_disposition_types.ExitDisposition
ExitGateResult = _exit_disposition_types.ExitGateResult


def _gate(threshold: float = 0.70) -> ExitControlGate:
    return ExitControlGate(
        policy_hash="sha256:test-policy",
        compliance_hash="sha256:test-compliance",
        confidence_threshold=threshold,
    )


def _good_artifact(**overrides) -> dict:
    base = {
        "rules_compliant": True,
        "answer_fit": True,
        "safety_clear": True,
        "grounded_replayable": True,
        "confidence_score": 0.95,
        "has_commit_payload": False,
        "escalation_reason": None,
    }
    base.update(overrides)
    return base


class TestExitDispositionEnum:
    def test_exactly_four_values(self):
        assert len(ExitDisposition) == 4

    def test_values_are_correct_strings(self):
        assert ExitDisposition.ALLOW_RESPONSE.value == "ALLOW_RESPONSE"
        assert ExitDisposition.DENY_RETURN.value == "DENY_RETURN"
        assert ExitDisposition.ESCALATE_TO_HITL.value == "ESCALATE_TO_HITL"
        assert ExitDisposition.COMMIT_TO_UWG.value == "COMMIT_TO_UWG"


class TestAllowResponse:
    def test_all_four_pass_returns_allow_response(self):
        result = _gate().evaluate(_good_artifact())
        assert result.disposition == ExitDisposition.ALLOW_RESPONSE

    def test_allow_response_has_non_null_trace_id(self):
        result = _gate().evaluate(_good_artifact())
        assert result.trace_id and len(result.trace_id) > 0

    def test_allow_response_has_reason(self):
        result = _gate().evaluate(_good_artifact())
        assert result.reason

    def test_allow_response_dimensions_all_true(self):
        result = _gate().evaluate(_good_artifact())
        assert result.dimensions.rules_compliant is True
        assert result.dimensions.answer_fit is True
        assert result.dimensions.safety_clear is True
        assert result.dimensions.grounded_replayable is True


class TestCommitToUWG:
    def test_all_pass_with_commit_payload_returns_commit_to_uwg(self):
        result = _gate().evaluate(_good_artifact(has_commit_payload=True))
        assert result.disposition == ExitDisposition.COMMIT_TO_UWG

    def test_commit_reason_mentions_uwg(self):
        result = _gate().evaluate(_good_artifact(has_commit_payload=True))
        assert "UWG" in result.reason or "uwg" in result.reason.lower()


class TestDenyReturn:
    def test_safety_clear_false_returns_deny(self):
        result = _gate().evaluate(_good_artifact(safety_clear=False))
        assert result.disposition == ExitDisposition.DENY_RETURN

    def test_rules_compliant_false_returns_deny(self):
        result = _gate().evaluate(_good_artifact(rules_compliant=False))
        assert result.disposition == ExitDisposition.DENY_RETURN

    def test_answer_fit_false_returns_deny(self):
        result = _gate().evaluate(_good_artifact(answer_fit=False))
        assert result.disposition == ExitDisposition.DENY_RETURN

    def test_grounded_replayable_false_returns_deny(self):
        result = _gate().evaluate(_good_artifact(grounded_replayable=False))
        assert result.disposition == ExitDisposition.DENY_RETURN

    def test_deny_has_reason_mentioning_failed_dimension(self):
        result = _gate().evaluate(_good_artifact(safety_clear=False))
        assert "X1C" in result.reason or "safety" in result.reason.lower()

    def test_rules_compliant_false_deny_mentions_x1a(self):
        result = _gate().evaluate(_good_artifact(rules_compliant=False))
        assert "X1A" in result.reason or "rules" in result.reason.lower()

    def test_answer_fit_false_deny_mentions_x1b(self):
        result = _gate().evaluate(_good_artifact(answer_fit=False))
        assert "X1B" in result.reason or "answer" in result.reason.lower()

    def test_grounded_false_deny_mentions_x1d(self):
        result = _gate().evaluate(_good_artifact(grounded_replayable=False))
        assert "X1D" in result.reason or "ground" in result.reason.lower()

    def test_commit_payload_with_safety_fail_returns_deny_not_commit(self):
        result = _gate().evaluate(_good_artifact(safety_clear=False, has_commit_payload=True))
        assert result.disposition == ExitDisposition.DENY_RETURN


class TestEscalateToHITL:
    def test_low_confidence_returns_escalate(self):
        result = _gate(threshold=0.70).evaluate(_good_artifact(confidence_score=0.65))
        assert result.disposition == ExitDisposition.ESCALATE_TO_HITL

    def test_exactly_at_threshold_does_not_escalate(self):
        result = _gate(threshold=0.70).evaluate(_good_artifact(confidence_score=0.70))
        assert result.disposition == ExitDisposition.ALLOW_RESPONSE

    def test_above_threshold_does_not_escalate(self):
        result = _gate(threshold=0.70).evaluate(_good_artifact(confidence_score=0.95))
        assert result.disposition == ExitDisposition.ALLOW_RESPONSE

    def test_explicit_escalation_reason_returns_escalate(self):
        result = _gate().evaluate(_good_artifact(escalation_reason="policy ambiguity detected"))
        assert result.disposition == ExitDisposition.ESCALATE_TO_HITL

    def test_escalate_reason_includes_escalation_reason_text(self):
        result = _gate().evaluate(_good_artifact(escalation_reason="ambiguous jurisdiction"))
        assert "ambiguous jurisdiction" in result.reason

    def test_escalation_reason_with_high_confidence_still_escalates(self):
        result = _gate().evaluate(
            _good_artifact(confidence_score=0.99, escalation_reason="human review required by policy")
        )
        assert result.disposition == ExitDisposition.ESCALATE_TO_HITL

    def test_escalation_takes_precedence_over_commit_payload(self):
        result = _gate().evaluate(
            _good_artifact(
                escalation_reason="requires human approval",
                has_commit_payload=True,
            )
        )
        assert result.disposition == ExitDisposition.ESCALATE_TO_HITL


class TestPriorityOrdering:
    def test_safety_fail_overrides_rules_fail(self):
        result = _gate().evaluate(_good_artifact(safety_clear=False, rules_compliant=False))
        assert result.disposition == ExitDisposition.DENY_RETURN
        assert "X1C" in result.reason or "safety" in result.reason.lower()

    def test_safety_fail_overrides_low_confidence(self):
        result = _gate().evaluate(_good_artifact(safety_clear=False, confidence_score=0.10))
        assert result.disposition == ExitDisposition.DENY_RETURN

    def test_rules_fail_checked_after_safety(self):
        result = _gate().evaluate(
            _good_artifact(safety_clear=True, rules_compliant=False, confidence_score=0.10)
        )
        assert result.disposition == ExitDisposition.DENY_RETURN
        assert "X1A" in result.reason or "rules" in result.reason.lower()


class TestFailClosed:
    def test_missing_required_key_returns_deny_not_exception(self):
        bad = {"rules_compliant": True}
        result = _gate().evaluate(bad)
        assert result.disposition == ExitDisposition.DENY_RETURN

    def test_empty_dict_returns_deny_not_exception(self):
        result = _gate().evaluate({})
        assert result.disposition == ExitDisposition.DENY_RETURN

    def test_none_artifact_returns_deny_not_exception(self):
        result = _gate().evaluate(None)
        assert result.disposition == ExitDisposition.DENY_RETURN

    def test_non_numeric_confidence_returns_deny_not_exception(self):
        result = _gate().evaluate(_good_artifact(confidence_score="not-a-float"))
        assert result.disposition == ExitDisposition.DENY_RETURN

    def test_disposition_never_none(self):
        for artifact in [{}, None, {"bad": "data"}, _good_artifact()]:
            result = _gate().evaluate(artifact)
            assert result.disposition is not None

    def test_missing_key_deny_reason_contains_malformed_text(self):
        result = _gate().evaluate({"rules_compliant": True})
        assert result.disposition == ExitDisposition.DENY_RETURN
        assert (
            "malformed" in result.reason.lower()
            or "extraction" in result.reason.lower()
            or "failed" in result.reason.lower()
        )

    def test_none_artifact_deny_reason_is_non_empty(self):
        result = _gate().evaluate(None)
        assert result.disposition == ExitDisposition.DENY_RETURN
        assert result.reason and len(result.reason) > 0


class TestExitGateResultContract:
    def test_to_dict_contains_disposition(self):
        result = _gate().evaluate(_good_artifact())
        d = result.to_dict()
        assert d["disposition"] == "ALLOW_RESPONSE"

    def test_to_dict_contains_trace_id(self):
        result = _gate().evaluate(_good_artifact())
        d = result.to_dict()
        assert "trace_id" in d and d["trace_id"]

    def test_to_dict_contains_reason(self):
        result = _gate().evaluate(_good_artifact())
        d = result.to_dict()
        assert "reason" in d

    def test_to_dict_contains_dimensions(self):
        result = _gate().evaluate(_good_artifact())
        d = result.to_dict()
        assert "dimensions" in d
        assert "rules_compliant" in d["dimensions"]
        assert "confidence_score" in d["dimensions"]

    def test_to_dict_contains_policy_hash(self):
        result = _gate().evaluate(_good_artifact())
        d = result.to_dict()
        assert d["policy_hash"] == "sha256:test-policy"

    def test_two_evaluations_produce_different_trace_ids(self):
        gate = _gate()
        r1 = gate.evaluate(_good_artifact())
        r2 = gate.evaluate(_good_artifact())
        assert r1.trace_id != r2.trace_id


class TestLayerSovereignty:
    def test_gate_does_not_mutate_input_artifact(self):
        artifact = _good_artifact()
        original_keys = set(artifact.keys())
        original_values = dict(artifact)
        _gate().evaluate(artifact)
        assert set(artifact.keys()) == original_keys
        assert artifact == original_values

    def test_gate_does_not_raise_on_any_input(self):
        adversarial_inputs = [
            None,
            {},
            [],
            "string",
            42,
            {"confidence_score": "nan"},
            {"safety_clear": None},
            _good_artifact(confidence_score=-999),
        ]
        gate = _gate()
        for inp in adversarial_inputs:
            result = gate.evaluate(inp)
            assert isinstance(result, ExitGateResult)
