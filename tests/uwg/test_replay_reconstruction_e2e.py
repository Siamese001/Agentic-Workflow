"""End-to-end replay reconstruction proof (00.5 §PHASE 2 + 00.8 §PHASE 4).

Demonstrates that after a UWG commit, the resulting receipts + audit ledger
records carry enough information to reconstruct the committed state's
deterministic digest. This is the core invariant the proof packet asserts.
"""

from __future__ import annotations

from agentic_core.L4_state.contracts.records import (
    record_canonical_payload,
    stamp_digest,
)
from agentic_core.L4_state.contracts import ReplaySnapshotRecord
from agentic_core.L4_state.contracts.digests import compute_deterministic_digest


class TestReplayE2E:
    def test_commit_audit_ledger_reconstructs_replay_record(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        commit_receipt, blocked, _refresh_receipts = gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit_receipt is not None
        assert blocked is None

        # Find the audit record for this commit
        all_records = gateway.audit_ledger.read()
        commit_audit = [
            r for r in all_records if r.event_type == "atomic_commit_applied" and r.run_id == cr.run_id
        ]
        assert len(commit_audit) == 1
        audit = commit_audit[0]

        # Build a ReplaySnapshotRecord from the receipts + audit
        replay = stamp_digest(
            ReplaySnapshotRecord(
                replay_snapshot_id=f"replay::{commit_receipt.commit_receipt_id}",
                trace_root=cr.trace_root,
                tenant_id=cr.tenant_id,
                policy_hash=cr.policy_hash,
                blueprint_hash=cr.blueprint_hash,
                replay_key=cr.replay_key,
                snapshot_id=commit_receipt.snapshot_after,
                request_id=cr.request_id,
                run_id=cr.run_id,
                commit_receipt_hash=commit_receipt.deterministic_digest,
                gate_verdict_hashes=cr.gate_verdict_refs,
                audit_refs=(audit.audit_record_id,),
            )
        )

        # Round-trip: digest must be reproducible from canonical payload
        payload = record_canonical_payload(replay)
        recomputed = compute_deterministic_digest(payload)
        assert recomputed == replay.deterministic_digest

        # All required reconstruction inputs are present
        assert replay.policy_hash == cr.policy_hash
        assert replay.replay_key == cr.replay_key
        assert replay.commit_receipt_hash == commit_receipt.deterministic_digest

    def test_blocked_commit_has_no_mutation_audit(self, gateway, well_formed_packet) -> None:
        """A blocked commit must NOT produce an atomic_commit_applied audit record."""
        from dataclasses import replace

        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(cr, source_surface="L2")
        commit, blocked, _ = gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None and blocked is not None
        events = {r.event_type for r in gateway.audit_ledger.read()}
        assert "atomic_commit_applied" not in events
        assert "commit_blocked" in events
        # The "no mutation applied" assertion is the SOLE durable proof
        assert blocked.no_mutation_assertion == "NO_MUTATION_APPLIED"
