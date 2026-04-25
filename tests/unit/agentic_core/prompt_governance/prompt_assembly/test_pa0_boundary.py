"""Unit tests for PA.0 boundary check."""

from __future__ import annotations

import pytest

from agentic_core.prompt_governance.prompt_assembly.pa0_boundary import (
    BoundaryCheckResult,
    BoundaryFailReason,
    BoundaryStatus,
    boundary_check,
)


def _good_plan() -> dict:
    return {"plan_id": "plan-1", "policy_hash": "ph-x", "grounding_required": False}


def _good_route() -> dict:
    return {"route_id": "R3", "execution_form": "SINGLE_STEP", "policy_hash": "ph-x"}


def _exec_meta() -> dict:
    return {"policy_hash": "ph-x", "executable_requested": True, "request_id": "req-1"}


# CHECK 0.1 ------------------------------------------------------------------


def test_missing_plan_contract():
    res = boundary_check(plan_contract=None, route_contract=_good_route(), evidence_contract=None)
    assert res.status is BoundaryStatus.FAIL
    assert res.fail_reason is BoundaryFailReason.MISSING_PLAN_CONTRACT
    assert res.eligible_for_prompt_assembly is False


def test_empty_plan_contract_fails_check_0_1():
    res = boundary_check(plan_contract={}, route_contract=_good_route(), evidence_contract=None)
    assert res.fail_reason is BoundaryFailReason.MISSING_PLAN_CONTRACT


# CHECK 0.2 ------------------------------------------------------------------


def test_missing_route_contract():
    res = boundary_check(plan_contract=_good_plan(), route_contract=None, evidence_contract=None)
    assert res.status is BoundaryStatus.FAIL
    assert res.fail_reason is BoundaryFailReason.MISSING_ROUTE_CONTRACT


def test_route_contract_without_route_id_fails():
    res = boundary_check(
        plan_contract=_good_plan(), route_contract={"execution_form": "SINGLE_STEP"}, evidence_contract=None
    )
    assert res.fail_reason is BoundaryFailReason.MISSING_ROUTE_CONTRACT


# CHECK 0.3 ------------------------------------------------------------------


def test_terminal_route_returns_skip():
    route = _good_route()
    route["execution_form"] = "TERMINAL_SHORTCIRCUIT"
    res = boundary_check(
        plan_contract=_good_plan(),
        route_contract=route,
        evidence_contract=None,
        execution_metadata=_exec_meta(),
    )
    assert res.status is BoundaryStatus.SKIP
    assert res.fail_reason is None
    assert res.eligible_for_prompt_assembly is False  # SKIP ≠ eligible


# CHECK 0.4 ------------------------------------------------------------------


def test_grounding_required_no_evidence_blocks():
    plan = _good_plan()
    plan["grounding_required"] = True
    res = boundary_check(
        plan_contract=plan,
        route_contract=_good_route(),
        evidence_contract=None,
        execution_metadata=_exec_meta(),
    )
    assert res.fail_reason is BoundaryFailReason.GROUNDING_REQUIRED_NO_EVIDENCE


def test_grounding_required_blocked_evidence_status_fails():
    plan = _good_plan()
    plan["grounding_required"] = True
    res = boundary_check(
        plan_contract=plan,
        route_contract=_good_route(),
        evidence_contract={"status": "BLOCKED"},
        execution_metadata=_exec_meta(),
    )
    assert res.fail_reason is BoundaryFailReason.GROUNDING_REQUIRED_NO_EVIDENCE


def test_grounding_required_with_pass_evidence_proceeds():
    plan = _good_plan()
    plan["grounding_required"] = True
    res = boundary_check(
        plan_contract=plan,
        route_contract=_good_route(),
        evidence_contract={"status": "PASS", "policy_hash": "ph-x"},
        execution_metadata=_exec_meta(),
    )
    assert res.status is BoundaryStatus.PASS


# CHECK 0.5 ------------------------------------------------------------------


def test_durable_write_not_permitted_blocks():
    plan = _good_plan()
    plan["write_requested"] = True
    res = boundary_check(
        plan_contract=plan,
        route_contract=_good_route(),
        evidence_contract=None,
        governance={"durable_write_allowed": False},
        execution_metadata=_exec_meta(),
    )
    assert res.fail_reason is BoundaryFailReason.DURABLE_WRITE_NOT_PERMITTED


def test_durable_write_permitted_proceeds():
    plan = _good_plan()
    plan["write_requested"] = True
    res = boundary_check(
        plan_contract=plan,
        route_contract=_good_route(),
        evidence_contract=None,
        governance={"durable_write_allowed": True},
        execution_metadata=_exec_meta(),
    )
    assert res.status is BoundaryStatus.PASS


# CHECK 0.6 ------------------------------------------------------------------


def test_hitl_required_with_executable_request_blocks():
    res = boundary_check(
        plan_contract=_good_plan(),
        route_contract=_good_route(),
        evidence_contract=None,
        governance={"hitl_required": True},
        execution_metadata={"policy_hash": "ph-x", "executable_requested": True},
    )
    assert res.fail_reason is BoundaryFailReason.HITL_REQUIRED_BUT_EXECUTABLE_REQUESTED


def test_hitl_required_review_only_request_passes():
    res = boundary_check(
        plan_contract=_good_plan(),
        route_contract=_good_route(),
        evidence_contract=None,
        governance={"hitl_required": True},
        execution_metadata={"policy_hash": "ph-x", "executable_requested": False},
    )
    assert res.status is BoundaryStatus.PASS


# CHECK 0.7 ------------------------------------------------------------------


def test_policy_hash_mismatch_blocks():
    plan = _good_plan()
    route = _good_route()
    route["policy_hash"] = "ph-y"  # mismatch
    res = boundary_check(
        plan_contract=plan,
        route_contract=route,
        evidence_contract=None,
        execution_metadata={"policy_hash": "ph-x"},
    )
    assert res.fail_reason is BoundaryFailReason.POLICY_HASH_MISMATCH


def test_consistent_policy_hashes_pass():
    res = boundary_check(
        plan_contract=_good_plan(),
        route_contract=_good_route(),
        evidence_contract=None,
        execution_metadata=_exec_meta(),
    )
    assert res.status is BoundaryStatus.PASS
    assert res.eligible_for_prompt_assembly is True
    # All seven check notes recorded
    assert any("check_0_7_pass" in n for n in res.notes)


# Result invariant -----------------------------------------------------------


def test_result_invariant_fail_requires_reason():
    with pytest.raises(ValueError):
        BoundaryCheckResult(status=BoundaryStatus.FAIL, fail_reason=None)


def test_result_pass_forces_eligibility_true():
    r = BoundaryCheckResult(status=BoundaryStatus.PASS, fail_reason=None, eligible_for_prompt_assembly=False)
    assert r.eligible_for_prompt_assembly is True


def test_result_skip_keeps_eligibility_false():
    r = BoundaryCheckResult(status=BoundaryStatus.SKIP, fail_reason=None, eligible_for_prompt_assembly=True)
    assert r.eligible_for_prompt_assembly is False
