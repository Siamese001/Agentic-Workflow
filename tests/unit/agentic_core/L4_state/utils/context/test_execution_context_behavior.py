"""Behavioral tests for ``agentic_core.L4_state.utils.context.execution_context``.

Covers the P0/L2 closure contract:
- ActionClass / GuardrailOutcome enum properties (is_irreversible, may_proceed, ...).
- ExecutionContext validation: required fields must be non-empty.
- Factory ``create`` produces valid instance with deterministic input/target hashes.
- ``with_guardrail_decision`` returns a new frozen copy with decision bound.
- ``to_dict`` redacts capability_token and emits only the documented fields.
- Same input / target produce same hash (determinism).
- Different input / target produce different hash.
"""

from __future__ import annotations

import hashlib

import pytest

from agentic_core.L4_state.utils.context.execution_context import (
    ActionClass,
    ExecutionContext,
    GuardrailOutcome,
)


class TestActionClassProperties:
    @pytest.mark.parametrize(
        ("action", "expected"),
        [
            (ActionClass.READ_ONLY, False),
            (ActionClass.NETWORK, False),
            (ActionClass.MUTATION, True),
            (ActionClass.PRIVILEGED_LOCAL, True),
            (ActionClass.EXTERNAL_SIDE_EFFECT, True),
            (ActionClass.HUMAN_GATED, True),
        ],
    )
    def test_is_irreversible(self, action: ActionClass, expected: bool) -> None:
        assert action.is_irreversible is expected

    @pytest.mark.parametrize(
        ("action", "expected"),
        [
            (ActionClass.MUTATION, True),
            (ActionClass.PRIVILEGED_LOCAL, True),
            (ActionClass.READ_ONLY, False),
            (ActionClass.NETWORK, False),
            (ActionClass.EXTERNAL_SIDE_EFFECT, False),
            (ActionClass.HUMAN_GATED, False),
        ],
    )
    def test_requires_uwg(self, action: ActionClass, expected: bool) -> None:
        assert action.requires_uwg is expected

    def test_requires_human_review_only_human_gated(self) -> None:
        assert ActionClass.HUMAN_GATED.requires_human_review is True
        for other in ActionClass:
            if other is not ActionClass.HUMAN_GATED:
                assert other.requires_human_review is False

    def test_requires_network_policy_only_network(self) -> None:
        assert ActionClass.NETWORK.requires_network_policy is True
        for other in ActionClass:
            if other is not ActionClass.NETWORK:
                assert other.requires_network_policy is False


class TestGuardrailOutcomeProperties:
    def test_may_proceed_only_allow(self) -> None:
        assert GuardrailOutcome.ALLOW.may_proceed is True
        for o in (
            GuardrailOutcome.DENY,
            GuardrailOutcome.ERROR,
            GuardrailOutcome.TIMEOUT,
            GuardrailOutcome.UNKNOWN,
        ):
            assert o.may_proceed is False

    def test_is_abnormal_inverse_of_may_proceed(self) -> None:
        for o in GuardrailOutcome:
            assert o.is_abnormal is not o.may_proceed


def _valid_kwargs(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "execution_request_id": "req-1",
        "run_id": "run-1",
        "capability_token": "token-abc-very-long",
        "policy_hash": "policy-hash-1",
        "guardrail_decision_id": "",
        "guardrail_decision_hash": "",
        "execution_input_hash": "input-hash-1",
        "execution_target_hash": "target-hash-1",
        "trace_id": "trace-1",
    }
    base.update(overrides)
    return base


class TestExecutionContextValidation:
    def test_valid_construction(self) -> None:
        ctx = ExecutionContext(**_valid_kwargs())
        assert ctx.run_id == "run-1"
        assert ctx.action_class is ActionClass.READ_ONLY

    @pytest.mark.parametrize(
        "field",
        [
            "execution_request_id",
            "run_id",
            "capability_token",
            "policy_hash",
            "execution_input_hash",
            "execution_target_hash",
            "trace_id",
        ],
    )
    def test_empty_required_field_raises(self, field: str) -> None:
        kwargs = _valid_kwargs(**{field: ""})
        with pytest.raises(ValueError, match="missing required fields"):
            ExecutionContext(**kwargs)

    def test_guardrail_decision_fields_may_be_empty_on_creation(self) -> None:
        ctx = ExecutionContext(
            **_valid_kwargs(
                guardrail_decision_id="",
                guardrail_decision_hash="",
            )
        )
        assert ctx.guardrail_decision_id == ""

    def test_is_frozen(self) -> None:
        ctx = ExecutionContext(**_valid_kwargs())
        with pytest.raises(AttributeError):
            ctx.run_id = "other"  # type: ignore[misc]


class TestFactoryCreate:
    def test_create_populates_hashes_and_ids(self) -> None:
        ctx = ExecutionContext.create(
            run_id="r",
            capability_token="t",
            policy_hash="p",
            execution_input={"x": 1},
            execution_target="tool:search",
        )
        assert ctx.run_id == "r"
        assert ctx.capability_token == "t"
        assert ctx.policy_hash == "p"
        assert ctx.execution_request_id  # non-empty
        assert ctx.trace_id  # non-empty
        assert ctx.guardrail_decision_id == ""
        assert ctx.guardrail_decision_hash == ""
        assert ctx.action_class is ActionClass.READ_ONLY

    def test_create_input_hash_deterministic(self) -> None:
        payload = {"x": 1, "y": [2, 3]}
        expected = hashlib.sha256(repr(payload).encode()).hexdigest()[:32]
        ctx = ExecutionContext.create(
            run_id="r",
            capability_token="t",
            policy_hash="p",
            execution_input=payload,
            execution_target="tgt",
        )
        assert ctx.execution_input_hash == expected

    def test_create_target_hash_deterministic(self) -> None:
        target = "tool:search"
        expected = hashlib.sha256(target.encode()).hexdigest()[:32]
        ctx = ExecutionContext.create(
            run_id="r",
            capability_token="t",
            policy_hash="p",
            execution_input={},
            execution_target=target,
        )
        assert ctx.execution_target_hash == expected

    def test_create_different_input_differs(self) -> None:
        a = ExecutionContext.create(
            run_id="r",
            capability_token="t",
            policy_hash="p",
            execution_input={"a": 1},
            execution_target="tgt",
        )
        b = ExecutionContext.create(
            run_id="r",
            capability_token="t",
            policy_hash="p",
            execution_input={"a": 2},
            execution_target="tgt",
        )
        assert a.execution_input_hash != b.execution_input_hash

    def test_create_different_target_differs(self) -> None:
        a = ExecutionContext.create(
            run_id="r",
            capability_token="t",
            policy_hash="p",
            execution_input={},
            execution_target="tgt1",
        )
        b = ExecutionContext.create(
            run_id="r",
            capability_token="t",
            policy_hash="p",
            execution_input={},
            execution_target="tgt2",
        )
        assert a.execution_target_hash != b.execution_target_hash

    def test_create_request_ids_unique(self) -> None:
        a = ExecutionContext.create(
            run_id="r",
            capability_token="t",
            policy_hash="p",
            execution_input={},
            execution_target="x",
        )
        b = ExecutionContext.create(
            run_id="r",
            capability_token="t",
            policy_hash="p",
            execution_input={},
            execution_target="x",
        )
        assert a.execution_request_id != b.execution_request_id

    def test_create_trace_id_override(self) -> None:
        ctx = ExecutionContext.create(
            run_id="r",
            capability_token="t",
            policy_hash="p",
            execution_input={},
            execution_target="x",
            trace_id="explicit-trace",
        )
        assert ctx.trace_id == "explicit-trace"

    def test_create_extra_defaults_empty_dict(self) -> None:
        ctx = ExecutionContext.create(
            run_id="r",
            capability_token="t",
            policy_hash="p",
            execution_input={},
            execution_target="x",
        )
        assert ctx.extra == {}

    def test_create_preserves_action_class(self) -> None:
        ctx = ExecutionContext.create(
            run_id="r",
            capability_token="t",
            policy_hash="p",
            execution_input={},
            execution_target="x",
            action_class=ActionClass.MUTATION,
        )
        assert ctx.action_class is ActionClass.MUTATION


class TestWithGuardrailDecision:
    def test_returns_new_instance(self) -> None:
        ctx = ExecutionContext(**_valid_kwargs())
        out = ctx.with_guardrail_decision("dec-1", "dec-hash-1")
        assert out is not ctx
        assert isinstance(out, ExecutionContext)

    def test_binds_decision_fields(self) -> None:
        ctx = ExecutionContext(**_valid_kwargs())
        out = ctx.with_guardrail_decision("dec-1", "dec-hash-1")
        assert out.guardrail_decision_id == "dec-1"
        assert out.guardrail_decision_hash == "dec-hash-1"

    def test_preserves_other_fields(self) -> None:
        ctx = ExecutionContext(**_valid_kwargs(action_class=ActionClass.MUTATION))
        out = ctx.with_guardrail_decision("d", "h")
        assert out.execution_request_id == ctx.execution_request_id
        assert out.run_id == ctx.run_id
        assert out.capability_token == ctx.capability_token
        assert out.policy_hash == ctx.policy_hash
        assert out.execution_input_hash == ctx.execution_input_hash
        assert out.execution_target_hash == ctx.execution_target_hash
        assert out.trace_id == ctx.trace_id
        assert out.action_class is ActionClass.MUTATION

    def test_original_unchanged(self) -> None:
        ctx = ExecutionContext(**_valid_kwargs())
        ctx.with_guardrail_decision("d", "h")
        assert ctx.guardrail_decision_id == ""
        assert ctx.guardrail_decision_hash == ""


class TestToDict:
    def test_redacts_capability_token(self) -> None:
        ctx = ExecutionContext(**_valid_kwargs(capability_token="secret-token-12345"))
        d = ctx.to_dict()
        assert d["capability_token"] == "secret-t..."
        assert "secret-token-12345" not in d["capability_token"]

    def test_emits_expected_keys(self) -> None:
        ctx = ExecutionContext(**_valid_kwargs())
        d = ctx.to_dict()
        assert set(d.keys()) == {
            "execution_request_id",
            "run_id",
            "capability_token",
            "policy_hash",
            "guardrail_decision_id",
            "guardrail_decision_hash",
            "execution_input_hash",
            "execution_target_hash",
            "trace_id",
            "action_class",
        }

    def test_action_class_serializes_as_value(self) -> None:
        ctx = ExecutionContext(**_valid_kwargs(action_class=ActionClass.MUTATION))
        assert ctx.to_dict()["action_class"] == "MUTATION"
