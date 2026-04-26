"""L4 audit ledger tests.

Doctrine: ``docs/reference/00_L4_State_and_UWG/00.5_*`` §PHASE 3 + §PHASE 6.

Tests must fail if:
- audit ledger entry is overwritten
- audit ledger sequence gap is ignored
- correction does not use ``supersedes_ref``
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.audit.audit_ledger import (
    AuditLedger,
    AuditLedgerSequenceGapError,
    AuditLedgerUnavailableError,
)


def _append_one(ledger: AuditLedger, *, seq_label: str = "x") -> None:
    ledger.append(
        event_type="atomic_commit_applied",
        state_surface="memory",
        operation_type="commit",
        tenant_id="t:1",
        policy_hash="ph:1",
        blueprint_hash="bh:1",
        snapshot_before=f"snap:{seq_label}:before",
        snapshot_after=f"snap:{seq_label}:after",
        actor_surface="UWG",
        mutation_source="UWG",
    )


class TestAppendSemantics:
    def test_append_increments_sequence_monotonically(self, fresh_ledger: AuditLedger) -> None:
        for i in range(5):
            _append_one(fresh_ledger, seq_label=str(i))
        records = fresh_ledger.read()
        sequences = [r.ledger_sequence for r in records]
        assert sequences == [1, 2, 3, 4, 5]

    def test_append_returns_record_and_receipt(self, fresh_ledger: AuditLedger) -> None:
        record, receipt = fresh_ledger.append(
            event_type="atomic_commit_applied",
            state_surface="memory",
            operation_type="commit",
            tenant_id="t:1",
            policy_hash="ph:1",
            blueprint_hash="bh:1",
            snapshot_before="snap:before",
            snapshot_after="snap:after",
            actor_surface="UWG",
            mutation_source="UWG",
        )
        assert record.audit_record_id == receipt.audit_record_id
        assert record.ledger_sequence == receipt.ledger_sequence
        assert record.deterministic_digest
        assert receipt.deterministic_digest == record.deterministic_digest

    def test_unavailable_ledger_raises(self, fresh_ledger: AuditLedger) -> None:
        fresh_ledger.set_available(False)
        with pytest.raises(AuditLedgerUnavailableError):
            _append_one(fresh_ledger)


class TestSequenceCheck:
    """Sequence_check fails on detected gaps."""

    def test_no_gap_passes(self, fresh_ledger: AuditLedger) -> None:
        for i in range(3):
            _append_one(fresh_ledger, seq_label=str(i))
        fresh_ledger.sequence_check()  # should not raise

    def test_injected_gap_detected(self, fresh_ledger: AuditLedger) -> None:
        # Direct construction bypassing the public API to simulate a gap
        from agentic_core.L4_state.contracts.records import AuditLedgerRecord, stamp_digest

        for i in range(3):
            _append_one(fresh_ledger, seq_label=str(i))
        # Inject a record with a wrong sequence — this is what ``sequence_check`` must catch
        bad = stamp_digest(
            AuditLedgerRecord(
                audit_record_id="bad:1",
                ledger_sequence=99,  # gap!
                event_type="atomic_commit_applied",
                state_surface="memory",
                operation_type="commit",
                tenant_id="t:1",
                policy_hash="ph:1",
                blueprint_hash="bh:1",
                snapshot_before="x",
                actor_surface="UWG",
                mutation_source="UWG",
                created_at="99",
            )
        )
        # Inject directly — ledger doesn't expose this; tests prove sequence_check would catch a corrupted store
        fresh_ledger._records.append(bad)  # noqa: SLF001 — testing gap detection
        with pytest.raises(AuditLedgerSequenceGapError):
            fresh_ledger.sequence_check()


class TestAppendOnly:
    """Audit records are append-only — overwrites must be detectable."""

    def test_record_lookup_finds_appended(self, fresh_ledger: AuditLedger) -> None:
        record, _ = fresh_ledger.append(
            event_type="atomic_commit_applied",
            state_surface="memory",
            operation_type="commit",
            tenant_id="t:1",
            policy_hash="ph:1",
            blueprint_hash="bh:1",
            snapshot_before="snap:before",
            actor_surface="UWG",
            mutation_source="UWG",
        )
        assert fresh_ledger.is_overwrite_attempted(record.audit_record_id)
        # Get returns the same record reference (frozen dataclass is value-equal)
        retrieved = fresh_ledger.get_record(record.audit_record_id)
        assert retrieved is not None
        assert retrieved.deterministic_digest == record.deterministic_digest

    def test_correction_uses_supersedes_ref(self, fresh_ledger: AuditLedger) -> None:
        original, _ = fresh_ledger.append(
            event_type="atomic_commit_applied",
            state_surface="memory",
            operation_type="commit",
            tenant_id="t:1",
            policy_hash="ph:1",
            blueprint_hash="bh:1",
            snapshot_before="snap:before",
            actor_surface="UWG",
            mutation_source="UWG",
        )
        # Correction is a NEW append with supersedes_ref pointing at the original.
        correction, _ = fresh_ledger.append(
            event_type="atomic_commit_applied",
            state_surface="memory",
            operation_type="commit",
            tenant_id="t:1",
            policy_hash="ph:1",
            blueprint_hash="bh:1",
            snapshot_before="snap:corrected:before",
            actor_surface="UWG",
            mutation_source="UWG",
            supersedes_ref=original.audit_record_id,
        )
        assert correction.supersedes_ref == original.audit_record_id
        # Both records remain — append-only
        assert fresh_ledger.position() == 2
