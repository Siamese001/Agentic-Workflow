"""Tests for L1PlanContract and validate_plan_contract (B04 — GAP-002, REQ-003).

Contract invariant tests:
- L1PlanContract is a frozen dataclass (immutable)
- All 7 fields required; any missing raises PlanContractViolation
- grounding_required=False → validate() passes
- grounding_required=True → validate() passes (C0 flag is structural, not a validator concern)
- confidence_score outside [0,1] → PlanContractViolation
- empty steps → PlanContractViolation
- empty plan_id / request_id / policy_hash → PlanContractViolation
- invalid reasoning_mode type → PlanContractViolation

validate_plan_contract() chokepoint tests:
- None input → PlanContractViolation
- Non-L1PlanContract input (dict, str, int) → PlanContractViolation
- Valid L1PlanContract → no exception

ReasoningMode enum:
- Exactly four values: CHAIN_OF_THOUGHT, REACT, DIRECT, DECOMPOSED

to_dict() contract:
- Contains all 7 keys
- reasoning_mode serialized as string value
- steps serialized as list

Layer sovereignty:
- L1PlanContract is frozen — mutation raises FrozenInstanceError
"""

import pytest
from dataclasses import FrozenInstanceError

from agentic_core.L1_cognition.types.plan_contract_types import (
    L1PlanContract,
    PlanContractViolation,
    ReasoningMode,
)
from agentic_core.L1_cognition.enforcement.reasoning_chokepoint import (
    validate_plan_contract,
)


def _valid_contract(**overrides) -> L1PlanContract:
    defaults = dict(
        plan_id="plan-001",
        request_id="req-001",
        policy_hash="sha256:abc123",
        reasoning_mode=ReasoningMode.CHAIN_OF_THOUGHT,
        grounding_required=True,
        confidence_score=0.90,
        steps=({"action": "retrieve"}, {"action": "synthesize"}),
    )
    defaults.update(overrides)
    return L1PlanContract(**defaults)


class TestReasoningModeEnum:
    def test_exactly_four_values(self):
        assert len(ReasoningMode) == 4

    def test_all_expected_values_present(self):
        assert ReasoningMode.CHAIN_OF_THOUGHT
        assert ReasoningMode.REACT
        assert ReasoningMode.DIRECT
        assert ReasoningMode.DECOMPOSED


class TestL1PlanContractValid:
    def test_valid_contract_does_not_raise(self):
        _valid_contract().validate()

    def test_grounding_required_true_passes(self):
        _valid_contract(grounding_required=True).validate()

    def test_grounding_required_false_passes(self):
        _valid_contract(grounding_required=False).validate()

    def test_confidence_score_zero_passes(self):
        _valid_contract(confidence_score=0.0).validate()

    def test_confidence_score_one_passes(self):
        _valid_contract(confidence_score=1.0).validate()

    def test_single_step_passes(self):
        _valid_contract(steps=({"action": "single"},)).validate()

    def test_all_reasoning_modes_accepted(self):
        for mode in ReasoningMode:
            _valid_contract(reasoning_mode=mode).validate()


class TestL1PlanContractViolations:
    def test_confidence_below_zero_raises(self):
        with pytest.raises(PlanContractViolation):
            _valid_contract(confidence_score=-0.01).validate()

    def test_confidence_above_one_raises(self):
        with pytest.raises(PlanContractViolation):
            _valid_contract(confidence_score=1.01).validate()

    def test_empty_steps_tuple_raises(self):
        with pytest.raises(PlanContractViolation):
            _valid_contract(steps=()).validate()

    def test_empty_plan_id_raises(self):
        with pytest.raises(PlanContractViolation):
            _valid_contract(plan_id="").validate()

    def test_whitespace_plan_id_raises(self):
        with pytest.raises(PlanContractViolation):
            _valid_contract(plan_id="   ").validate()

    def test_empty_request_id_raises(self):
        with pytest.raises(PlanContractViolation):
            _valid_contract(request_id="").validate()

    def test_empty_policy_hash_raises(self):
        with pytest.raises(PlanContractViolation):
            _valid_contract(policy_hash="").validate()

    def test_invalid_reasoning_mode_type_raises(self):
        with pytest.raises(PlanContractViolation):
            _valid_contract(reasoning_mode="CHAIN_OF_THOUGHT").validate()

    def test_plan_contract_violation_is_value_error_subclass(self):
        exc = PlanContractViolation("test")
        assert isinstance(exc, ValueError)

    def test_steps_as_string_raises_even_if_non_empty(self):
        with pytest.raises(PlanContractViolation):
            _valid_contract(steps="retrieve-then-synthesize").validate()


class TestValidatePlanContractChokepoint:
    def test_none_raises_plan_contract_violation(self):
        with pytest.raises(PlanContractViolation):
            validate_plan_contract(None)

    def test_dict_raises_plan_contract_violation(self):
        with pytest.raises(PlanContractViolation):
            validate_plan_contract({"plan_id": "x"})

    def test_string_raises_plan_contract_violation(self):
        with pytest.raises(PlanContractViolation):
            validate_plan_contract("not a contract")

    def test_int_raises_plan_contract_violation(self):
        with pytest.raises(PlanContractViolation):
            validate_plan_contract(42)

    def test_valid_contract_passes_chokepoint(self):
        validate_plan_contract(_valid_contract())

    def test_invalid_contract_raises_at_chokepoint(self):
        bad = _valid_contract(confidence_score=2.0)
        with pytest.raises(PlanContractViolation):
            validate_plan_contract(bad)


class TestToDictContract:
    def test_to_dict_contains_all_seven_keys(self):
        d = _valid_contract().to_dict()
        assert "plan_id" in d
        assert "request_id" in d
        assert "policy_hash" in d
        assert "reasoning_mode" in d
        assert "grounding_required" in d
        assert "confidence_score" in d
        assert "steps" in d

    def test_reasoning_mode_serialized_as_string(self):
        d = _valid_contract(reasoning_mode=ReasoningMode.REACT).to_dict()
        assert d["reasoning_mode"] == "REACT"

    def test_steps_serialized_as_list(self):
        d = _valid_contract(steps=({"a": 1}, {"b": 2})).to_dict()
        assert isinstance(d["steps"], list)
        assert len(d["steps"]) == 2

    def test_grounding_required_preserved(self):
        d = _valid_contract(grounding_required=True).to_dict()
        assert d["grounding_required"] is True

    def test_confidence_score_preserved(self):
        d = _valid_contract(confidence_score=0.77).to_dict()
        assert d["confidence_score"] == pytest.approx(0.77)


class TestLayerSovereignty:
    def test_frozen_contract_raises_on_mutation(self):
        contract = _valid_contract()
        with pytest.raises(FrozenInstanceError):
            contract.plan_id = "new-id"  # type: ignore[misc]

    def test_frozen_contract_steps_is_tuple(self):
        contract = _valid_contract()
        assert isinstance(contract.steps, tuple)
