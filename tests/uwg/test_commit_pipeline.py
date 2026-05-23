"""UWG commit pipeline happy-path and blocked-commit tests.

Doctrine: ``docs/reference/00_L4_State_and_UWG/00.6_*`` §PHASE 2 + §PHASE 4.
"""

from __future__ import annotations

from dataclasses import replace

from agentic_core.L4_state.otel.spans import get_emitted_spans


class TestHappyPath:
    """Well-formed packet -> commit_receipt + refresh receipts; blocked is None."""

    def test_full_commit_pipeline_emits_commit_receipt(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        commit_receipt, blocked, refresh_receipts = gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit_receipt is not None
        assert blocked is None
        assert commit_receipt.snapshot_after
        assert commit_receipt.audit_append_receipt_ref
        assert commit_receipt.read_surface_refresh_plan_ref == refresh.refresh_plan_id
        assert commit_receipt.deterministic_digest
        assert commit_receipt.l5_certification_ref == cr.l5_certification_ref

    def test_commit_returns_refresh_receipts(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        commit_receipt, _blocked, refresh_receipts = gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit_receipt is not None
        assert len(refresh_receipts) == len(refresh.required_refreshes)
        for r in refresh_receipts:
            assert r.source_commit_receipt_ref == commit_receipt.commit_receipt_id
            assert r.status == "SUCCESS"

    def test_commit_emits_required_spans(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        names = {s.name for s in get_emitted_spans()}
        # Per 00.8 §PHASE 1
        assert "uwg.commit.request_received" in names
        assert "uwg.commit.validate" in names
        assert "uwg.write_lock.acquire" in names
        assert "uwg.commit.apply" in names
        assert "uwg.commit.receipt_emit" in names
        assert "uwg.read_surface.refresh" in names

    def test_audit_ledger_appended_on_commit(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        gateway.commit(
            commit_request=cr,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        records = gateway.audit_ledger.read()
        events = {r.event_type for r in records}
        assert "atomic_commit_applied" in events
        assert "read_surface_refresh_completed" in events


class TestBlockedCommit:
    """Per 00.6 §PHASE 4 — blocked commits emit BlockedCommitReceipt."""

    def test_non_exit_source_blocks(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(cr, source_surface="L2")
        commit, blocked, _ = gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert blocked.no_mutation_assertion == "NO_MUTATION_APPLIED"
        assert any(
            "non_exit_source" in code or "non_authorized" in code for code in blocked.blocked_reason_codes
        )

    def test_missing_policy_hash_blocks(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(cr, policy_hash="")
        commit, blocked, _ = gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert "missing::policy_hash" in blocked.blocked_reason_codes

    def test_missing_replay_key_blocks(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(cr, replay_key="")
        commit, blocked, _ = gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert "missing::replay_key" in blocked.blocked_reason_codes

    def test_missing_gate_verdicts_blocks(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(cr, gate_verdict_refs=())
        commit, blocked, _ = gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        assert commit is None
        assert blocked is not None
        assert "missing::gate_verdict_refs" in blocked.blocked_reason_codes

    def test_blocked_emits_blocked_span(self, gateway, well_formed_packet) -> None:
        cr, diffs, rollback, refresh = well_formed_packet
        bad = replace(cr, source_surface="L6")
        gateway.commit(
            commit_request=bad,
            state_diffs=diffs,
            rollback_plan=rollback,
            refresh_plan=refresh,
        )
        names = {s.name for s in get_emitted_spans()}
        assert "uwg.commit.blocked" in names
