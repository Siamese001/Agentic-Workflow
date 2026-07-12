"""Strict R1B UWG evidence verification and shared-authority tests."""

from __future__ import annotations

from dataclasses import replace

from agentic_core.L4_state.contracts.records import stamp_digest
from apps_rg.cache.r1b_commit_authority import compute_r1b_commit_request_signature
from apps_rg.cache.r1b_strict_gateway import (
    R1BStrictUWGGateway,
    get_r1b_strict_gateway,
    reset_r1b_strict_gateway,
)
from tests.unit.agentic_core.L4_state.uwg_acceptance.test_uwg_validation_fail_closed import (
    _bundle,
)


def _signed_bundle():
    request, diffs, rollback, refresh = _bundle()
    signature = compute_r1b_commit_request_signature(
        commit_request_id=request.commit_request_id,
        staged_diff_hash=request.staged_diff_hash,
        clearance_proof_id=request.clearance_proof_id,
    )
    request = stamp_digest(
        replace(
            request,
            commit_request_signature=signature,
            deterministic_digest="",
        )
    )
    return request, diffs, rollback, refresh


def test_r1b_gateway_reuses_validation_receipt_for_same_commit_inputs() -> None:
    request, diffs, rollback, refresh = _signed_bundle()
    gateway = R1BStrictUWGGateway()

    first = gateway._validate(request, diffs, rollback, refresh)
    second = gateway._validate(request, diffs, rollback, refresh)

    assert first.uwg_validation_receipt_id == second.uwg_validation_receipt_id
    assert first.deterministic_digest == second.deterministic_digest


def test_forged_commit_request_signature_blocks_before_commit() -> None:
    request, diffs, rollback, refresh = _signed_bundle()
    request = stamp_digest(
        replace(request, commit_request_signature="forged", deterministic_digest="")
    )

    commit, blocked, refreshes = R1BStrictUWGGateway().commit(
        commit_request=request,
        state_diffs=diffs,
        rollback_plan=rollback,
        refresh_plan=refresh,
    )

    assert commit is None
    assert refreshes == []
    assert blocked is not None
    assert "commit_request_signature_invalid" in blocked.blocked_reason_codes
    assert blocked.no_mutation_assertion == "NO_MUTATION_APPLIED"


def test_missing_capability_token_blocks_before_commit() -> None:
    request, diffs, rollback, refresh = _signed_bundle()
    request = stamp_digest(
        replace(request, capability_token_ref="", deterministic_digest="")
    )

    commit, blocked, _refreshes = R1BStrictUWGGateway().commit(
        commit_request=request,
        state_diffs=diffs,
        rollback_plan=rollback,
        refresh_plan=refresh,
    )

    assert commit is None
    assert blocked is not None
    assert "missing_or_placeholder_capability_token_ref" in blocked.blocked_reason_codes


def test_shared_r1b_gateway_is_process_singleton() -> None:
    reset_r1b_strict_gateway()
    first = get_r1b_strict_gateway()
    second = get_r1b_strict_gateway()
    assert first is second
