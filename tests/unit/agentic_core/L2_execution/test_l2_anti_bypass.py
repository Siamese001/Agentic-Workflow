"""Tests for L2 anti-bypass guards (doc 04.8 §PHASE 3).

Each forbidden behavior gets at least one negative test (must reject) and
one positive test (must accept the well-formed case). The aggregator
:func:`assert_l2_bounded` is exercised end-to-end at the bottom.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.enforcement.anti_bypass_guards import (
    BypassReason,
    L2BypassViolation,
    assert_capability_token_present,
    assert_human_input_is_data_only,
    assert_l2_bounded,
    assert_no_direct_human_call,
    assert_no_direct_l4_write,
    assert_no_direct_uwg_call,
    assert_no_forbidden_l2_output,
    assert_no_prompt_envelope_construction,
    assert_no_provider_or_tool_switch,
    assert_no_route_change,
    assert_no_unapproved_c0_retrieval,
    assert_no_workflow_expansion,
    assert_repair_under_same_snapshot,
    assert_sandbox_envelope_present,
    assert_seals_rejection_or_failure,
    raise_if_any,
)


# ---------------------------------------------------------------------------
# 1. Forbidden L2 final-disposition strings
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "forbidden",
    [
        "ALLOW_FINISH",
        "DENY",
        "REROUTE",
        "ESCALATE_HITL",
        "COMMIT_REQUEST_TO_UWG",
        "SAFE_FALLBACK",
        "durable_write_committed",
        "policy_certified",
        "route_changed",
        "workflow_expanded",
        "evidence_contract_issued",
        "prompt_envelope_constructed",
        "learning_promoted",
    ],
)
def test_forbidden_l2_outputs_rejected(forbidden: str) -> None:
    res = assert_no_forbidden_l2_output(forbidden)
    assert not res.ok
    assert res.reason is BypassReason.EMITS_FINAL_EXIT_DISPOSITION


def test_l2_terminal_class_strings_accepted() -> None:
    # Terminal classes that L2 *may* emit (E5 §TERMINAL CLASS).
    for ok in ("SUCCESS", "DEGRADED_SUCCESS", "FAILURE", "NEEDS_HELP", "REJECTED"):
        assert assert_no_forbidden_l2_output(ok).ok


# ---------------------------------------------------------------------------
# 2. Route mutation
# ---------------------------------------------------------------------------


def test_route_id_change_rejected() -> None:
    res = assert_no_route_change(
        original_route_id="r1",
        original_route_digest="d1",
        new_route_id="r2",
        new_route_digest="d1",
    )
    assert not res.ok
    assert res.reason is BypassReason.CHANGES_ROUTE_ID_OR_DIGEST


def test_route_digest_change_rejected() -> None:
    res = assert_no_route_change(
        original_route_id="r1",
        original_route_digest="d1",
        new_route_id="r1",
        new_route_digest="d2",
    )
    assert not res.ok
    assert res.reason is BypassReason.CHANGES_ROUTE_ID_OR_DIGEST


def test_route_unchanged_passes() -> None:
    res = assert_no_route_change(
        original_route_id="r1",
        original_route_digest="d1",
        new_route_id="r1",
        new_route_digest="d1",
    )
    assert res.ok


# ---------------------------------------------------------------------------
# 3. Workflow expansion
# ---------------------------------------------------------------------------


def test_workflow_expansion_rejected() -> None:
    res = assert_no_workflow_expansion(original_step_count=4, new_step_count=5)
    assert not res.ok
    assert res.reason is BypassReason.EXPANDS_WORKFLOW


def test_workflow_unchanged_passes() -> None:
    assert assert_no_workflow_expansion(original_step_count=4, new_step_count=4).ok


# ---------------------------------------------------------------------------
# 4. Capability token + sandbox envelope
# ---------------------------------------------------------------------------


def test_missing_capability_token_rejected() -> None:
    res = assert_capability_token_present("")
    assert not res.ok
    assert res.reason is BypassReason.MISSING_CAPABILITY_TOKEN


def test_missing_sandbox_envelope_rejected() -> None:
    res = assert_sandbox_envelope_present(None)
    assert not res.ok
    assert res.reason is BypassReason.MISSING_SANDBOX_ENVELOPE


def test_present_capability_and_sandbox_pass() -> None:
    assert assert_capability_token_present("cap-1").ok
    assert assert_sandbox_envelope_present("sbx-1").ok


# ---------------------------------------------------------------------------
# 5. Provider / model / tool silent-switch
# ---------------------------------------------------------------------------


def test_provider_switch_rejected() -> None:
    res = assert_no_provider_or_tool_switch(
        declared_provider="anthropic",
        actual_provider="openai",
    )
    assert not res.ok
    assert res.reason is BypassReason.SILENT_PROVIDER_OR_TOOL_SWITCH


def test_model_switch_rejected() -> None:
    res = assert_no_provider_or_tool_switch(
        declared_provider="anthropic",
        actual_provider="anthropic",
        declared_model="claude-haiku",
        actual_model="claude-opus",
    )
    assert not res.ok
    assert res.reason is BypassReason.SILENT_PROVIDER_OR_TOOL_SWITCH


def test_tool_switch_rejected() -> None:
    res = assert_no_provider_or_tool_switch(
        declared_provider="x",
        actual_provider="x",
        declared_tool="grep",
        actual_tool="ripgrep",
    )
    assert not res.ok


def test_provider_match_passes() -> None:
    res = assert_no_provider_or_tool_switch(
        declared_provider="anthropic",
        actual_provider="anthropic",
        declared_model="claude-haiku",
        actual_model="claude-haiku",
    )
    assert res.ok


# ---------------------------------------------------------------------------
# 6. Repair under changed snapshot
# ---------------------------------------------------------------------------


def test_repair_under_changed_blueprint_rejected() -> None:
    res = assert_repair_under_same_snapshot(
        original_blueprint_hash="bp1",
        original_policy_hash="pol1",
        repair_blueprint_hash="bp2",
        repair_policy_hash="pol1",
    )
    assert not res.ok
    assert res.reason is BypassReason.REPAIR_UNDER_CHANGED_SNAPSHOT


def test_repair_under_changed_policy_rejected() -> None:
    res = assert_repair_under_same_snapshot(
        original_blueprint_hash="bp1",
        original_policy_hash="pol1",
        repair_blueprint_hash="bp1",
        repair_policy_hash="pol2",
    )
    assert not res.ok


def test_repair_same_snapshot_passes() -> None:
    res = assert_repair_under_same_snapshot(
        original_blueprint_hash="bp1",
        original_policy_hash="pol1",
        repair_blueprint_hash="bp1",
        repair_policy_hash="pol1",
    )
    assert res.ok


# ---------------------------------------------------------------------------
# 7. Unsealed rejection / failure
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cls", ["FAILURE", "REJECTED", "NEEDS_HELP", "FAIL_TERMINAL"])
def test_unsealed_failure_rejected(cls: str) -> None:
    res = assert_seals_rejection_or_failure(terminal_class=cls, sealed_artifact_ref="")
    assert not res.ok
    assert res.reason is BypassReason.UNSEALED_REJECTION_OR_FAILURE


def test_sealed_failure_passes() -> None:
    res = assert_seals_rejection_or_failure(terminal_class="REJECTED", sealed_artifact_ref="art-1")
    assert res.ok


def test_success_does_not_require_seal_check() -> None:
    res = assert_seals_rejection_or_failure(terminal_class="SUCCESS", sealed_artifact_ref="")
    assert res.ok


# ---------------------------------------------------------------------------
# 8. Direct L4 / UWG / human bypass
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "target",
    [
        "agentic_core.L4_state.canonical_store",
        "uwg.commit",
        "uwg_commit_log",
        "system_of_record.write",
        "durable_write_path",
    ],
)
def test_direct_l4_or_uwg_target_rejected(target: str) -> None:
    res = assert_no_direct_l4_write(target=target)
    assert not res.ok
    assert res.reason is BypassReason.DIRECT_L4_WRITE


def test_proposed_state_diff_target_passes() -> None:
    res = assert_no_direct_l4_write(target="proposed_state_diff_buffer")
    assert res.ok


def test_direct_human_channel_rejected() -> None:
    res = assert_no_direct_human_call(channel="hitl_chat_inline")
    assert not res.ok
    assert res.reason is BypassReason.ASKS_HUMAN_DIRECTLY


def test_packetized_human_channel_passes() -> None:
    res = assert_no_direct_human_call(channel="exit_hitl_packetization")
    assert res.ok


def test_uwg_call_without_exit_clearance_rejected() -> None:
    res = assert_no_direct_uwg_call(target_layer="UWG", exit_cleared=False)
    assert not res.ok
    assert res.reason is BypassReason.DIRECT_UWG_CALL


def test_uwg_call_with_exit_clearance_passes() -> None:
    res = assert_no_direct_uwg_call(target_layer="UWG", exit_cleared=True)
    assert res.ok


# ---------------------------------------------------------------------------
# 9. Human input cannot become authority
# ---------------------------------------------------------------------------


def test_human_input_with_authority_rejected() -> None:
    res = assert_human_input_is_data_only(human_input_scope="AUTHORITATIVE")
    assert not res.ok
    assert res.reason is BypassReason.TREATS_HUMAN_INPUT_AS_AUTHORITY


def test_human_input_data_only_passes() -> None:
    res = assert_human_input_is_data_only(human_input_scope="DATA_ONLY")
    assert res.ok


# ---------------------------------------------------------------------------
# 10. Prompt envelope construction by L2
# ---------------------------------------------------------------------------


def test_l2_constructs_prompt_envelope_rejected() -> None:
    res = assert_no_prompt_envelope_construction(builder_layer="L2")
    assert not res.ok
    assert res.reason is BypassReason.BUILDS_PROMPT_ENVELOPE


def test_prompt_assembly_layer_passes() -> None:
    res = assert_no_prompt_envelope_construction(builder_layer="PROMPT_ASSEMBLY")
    assert res.ok


# ---------------------------------------------------------------------------
# 11. C0 retrieval gate
# ---------------------------------------------------------------------------


def test_unapproved_c0_retrieval_rejected() -> None:
    res = assert_no_unapproved_c0_retrieval(retrieval_authority="OPPORTUNISTIC")
    assert not res.ok
    assert res.reason is BypassReason.UNAPPROVED_C0_RETRIEVAL


def test_bounded_read_authority_passes() -> None:
    assert assert_no_unapproved_c0_retrieval(retrieval_authority="BOUNDED_READ").ok
    assert assert_no_unapproved_c0_retrieval(retrieval_authority="BOUNDED_TOOL_ACTION").ok


# ---------------------------------------------------------------------------
# 12. Aggregator: assert_l2_bounded()
# ---------------------------------------------------------------------------


def test_aggregator_clean_facts_yields_all_ok() -> None:
    facts = {
        "capability_token_ref": "cap-1",
        "sandbox_envelope_ref": "sbx-1",
        "original_route_id": "r1",
        "new_route_id": "r1",
        "original_route_digest": "d1",
        "new_route_digest": "d1",
        "original_step_count": 5,
        "new_step_count": 5,
        "declared_provider": "anthropic",
        "actual_provider": "anthropic",
        "original_blueprint_hash": "bp",
        "original_policy_hash": "pol",
        "repair_blueprint_hash": "bp",
        "repair_policy_hash": "pol",
        "terminal_class": "SUCCESS",
        "sealed_artifact_ref": "art-1",
        "write_target": "proposed_state_diff_buffer",
        "human_call_channel": "exit_hitl_packetization",
        "human_input_scope": "DATA_ONLY",
        "prompt_envelope_builder_layer": "PROMPT_ASSEMBLY",
        "c0_retrieval_authority": "BOUNDED_READ",
        "uwg_target_layer": "L4",  # not UWG
        "exit_cleared": False,
        "final_disposition": "SUCCESS",
    }
    results = assert_l2_bounded(facts)
    failures = [r for r in results if not r.ok]
    assert failures == [], failures


def test_aggregator_dirty_facts_collects_violations() -> None:
    facts = {
        "capability_token_ref": "",  # missing — should fail
        "sandbox_envelope_ref": "sbx-1",
        "original_route_id": "r1",
        "new_route_id": "r2",  # changed — should fail
        "declared_provider": "anthropic",
        "actual_provider": "openai",  # switched — should fail
        "final_disposition": "ALLOW_FINISH",  # forbidden output — should fail
    }
    results = assert_l2_bounded(facts)
    fails = [r for r in results if not r.ok]
    reasons = {r.reason for r in fails}
    assert BypassReason.MISSING_CAPABILITY_TOKEN in reasons
    assert BypassReason.CHANGES_ROUTE_ID_OR_DIGEST in reasons
    assert BypassReason.SILENT_PROVIDER_OR_TOOL_SWITCH in reasons
    assert BypassReason.EMITS_FINAL_EXIT_DISPOSITION in reasons


def test_raise_if_any_clean_passes() -> None:
    raise_if_any(assert_l2_bounded({"capability_token_ref": "cap-1"}))


def test_raise_if_any_dirty_raises() -> None:
    facts = {"capability_token_ref": ""}
    results = assert_l2_bounded(facts)
    with pytest.raises(L2BypassViolation, match="missing_capability_token"):
        raise_if_any(results)
