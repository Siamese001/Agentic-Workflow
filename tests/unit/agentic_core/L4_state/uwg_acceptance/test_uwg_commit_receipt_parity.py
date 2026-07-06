"""UWG commit receipts carry durable-write provenance directly."""

from __future__ import annotations

from agentic_core.L4_state.uwg.durable_write_gateway import DurableWriteGateway
from tests.unit.agentic_core.L4_state.uwg_acceptance.test_uwg_validation_fail_closed import (
    _bundle,
)


def test_uwg_commit_receipt_carries_request_provenance() -> None:
    request, diffs, rollback, refresh = _bundle()

    commit, blocked, refreshes = DurableWriteGateway().commit(
        commit_request=request,
        state_diffs=diffs,
        rollback_plan=rollback,
        refresh_plan=refresh,
    )

    assert blocked is None
    assert commit is not None
    assert refreshes
    assert commit.l5_certification_ref == request.l5_certification_ref
    assert commit.source_surface == "Exit"
    assert commit.policy_hash == request.policy_hash
    assert commit.blueprint_hash == request.blueprint_hash
    assert commit.replay_key == request.replay_key
    assert commit.gate_verdict_refs == request.gate_verdict_refs
    assert commit.cleared_exit_review_packet_ref == request.cleared_exit_review_packet_ref
    assert commit.registry_digest_set == request.registry_digest_set
    assert commit.clearance_proof_id == request.clearance_proof_id
    assert commit.staged_diff_hash == request.staged_diff_hash
    assert commit.validator_receipt_id
    assert commit.content_hash
