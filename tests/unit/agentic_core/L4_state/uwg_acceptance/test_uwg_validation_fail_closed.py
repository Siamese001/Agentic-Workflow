"""UWG validation fails closed on incomplete durable-write evidence."""

from __future__ import annotations

from dataclasses import replace

from agentic_core.L4_state.contracts.records import (
    CommitRequest,
    ReadSurfaceRefreshPlan,
    RollbackPlan,
    StateDiff,
    stamp_digest,
)
from agentic_core.L4_state.uwg.durable_write_gateway import (
    DurableWriteGateway,
    compute_state_diffs_digest,
)

TARGET = "l4.test.surface"


def _bundle():
    rollback = stamp_digest(
        RollbackPlan(
            rollback_plan_id="rb:test",
            blast_radius="single_surface",
            target_surfaces=(TARGET,),
            before_snapshot_refs=("snapshot:before",),
            rollback_operation_types=("tombstone",),
        )
    )
    diff = stamp_digest(
        StateDiff(
            state_diff_id="sd:test",
            target_surface=TARGET,
            operation_type="memory_promotion",
            after_candidate="payload:test",
            schema_ref="schema:test",
            blast_radius="single_surface",
            rollback_plan_ref=rollback.rollback_plan_id,
            proposed_by_surface="Exit",
            created_at="1",
        )
    )
    staged = compute_state_diffs_digest([diff])
    request = stamp_digest(
        CommitRequest(
            commit_request_id="cr:test",
            cleared_exit_review_packet_ref="exit:test",
            request_id="request:test",
            run_id="run:test",
            trace_root="trace:test",
            tenant_id="tenant:test",
            policy_hash="policy:test",
            blueprint_hash="blueprint:test",
            route_contract_ref="route:test",
            replay_key="replay:test",
            rollback_plan_ref=rollback.rollback_plan_id,
            blast_radius="single_surface",
            state_diff_refs=(diff.state_diff_id,),
            gate_verdict_refs=("gate:test",),
            l5_certification_ref="l5:test",
            affected_state_surfaces=(TARGET,),
            expected_read_surface_refreshes=("test_projection",),
            registry_digest_set=("registry:test",),
            capability_token_ref="capability:test",
            clearance_proof_id="clearance:test",
            validator_receipt_id="validator:test",
            staged_diff_hash=staged,
            commit_request_signature="signature:test",
        )
    )
    refresh = stamp_digest(
        ReadSurfaceRefreshPlan(
            refresh_plan_id="refresh:test",
            source_commit_receipt_ref="<pending>",
            before_snapshot="snapshot:before",
            expected_after_snapshot="snapshot:after",
            stale_projection_policy="fail_closed",
            retry_policy="none",
            policy_hash=request.policy_hash,
            blueprint_hash=request.blueprint_hash,
            affected_surfaces=(TARGET,),
            required_refreshes=("test_projection",),
            refresh_order=("test_projection",),
        )
    )
    return request, [diff], rollback, refresh


def _commit(request: CommitRequest, diffs: list[StateDiff]):
    _base, _diffs, rollback, refresh = _bundle()
    return DurableWriteGateway().commit(
        commit_request=request,
        state_diffs=diffs,
        rollback_plan=rollback,
        refresh_plan=refresh,
    )


def test_missing_clearance_proof_blocks_commit() -> None:
    request, diffs, _rollback, _refresh = _bundle()
    request = stamp_digest(replace(request, clearance_proof_id="", deterministic_digest=""))

    commit, blocked, refreshes = _commit(request, diffs)

    assert commit is None
    assert refreshes == []
    assert blocked is not None
    assert "missing_clearance_proof_id" in blocked.blocked_reason_codes
    assert blocked.no_mutation_assertion == "NO_MUTATION_APPLIED"


def test_missing_registry_digest_set_blocks_refresh_bound_commit() -> None:
    request, diffs, _rollback, _refresh = _bundle()
    request = stamp_digest(replace(request, registry_digest_set=(), deterministic_digest=""))

    commit, blocked, _refreshes = _commit(request, diffs)

    assert commit is None
    assert blocked is not None
    assert "missing_registry_digest_set" in blocked.blocked_reason_codes


def test_state_diff_hash_mismatch_blocks_commit() -> None:
    request, diffs, _rollback, _refresh = _bundle()
    request = stamp_digest(replace(request, staged_diff_hash="bad", deterministic_digest=""))

    commit, blocked, _refreshes = _commit(request, diffs)

    assert commit is None
    assert blocked is not None
    assert "state_diff_hash_mismatch" in blocked.blocked_reason_codes


def test_target_surface_not_allowlisted_blocks_commit() -> None:
    request, diffs, _rollback, _refresh = _bundle()
    bad_diff = stamp_digest(replace(diffs[0], target_surface="l4.other.surface", deterministic_digest=""))
    request = stamp_digest(
        replace(
            request,
            state_diff_refs=(bad_diff.state_diff_id,),
            staged_diff_hash=compute_state_diffs_digest([bad_diff]),
            deterministic_digest="",
        )
    )

    commit, blocked, _refreshes = _commit(request, [bad_diff])

    assert commit is None
    assert blocked is not None
    assert "target_surface_not_allowlisted" in blocked.blocked_reason_codes
