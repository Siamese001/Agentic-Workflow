"""Audit ledger hash-chain replay evidence."""

from __future__ import annotations

from dataclasses import replace

import pytest

from agentic_core.L4_state.audit.audit_ledger import (
    AuditLedger,
    AuditLedgerChainError,
)


def _append(ledger: AuditLedger, event_type: str):
    return ledger.append(
        event_type=event_type,
        state_surface="l4.test.surface",
        operation_type="commit",
        tenant_id="tenant",
        policy_hash="policy",
        blueprint_hash="blueprint",
        snapshot_before="before",
        actor_surface="UWG",
        mutation_source="UWG",
    )


def test_audit_append_receipt_carries_chain_fields() -> None:
    ledger = AuditLedger()
    record, receipt = _append(ledger, "first")

    assert record.prev_chain_hash
    assert record.chain_hash
    assert receipt.prev_chain_hash == record.prev_chain_hash
    assert receipt.chain_hash == record.chain_hash
    ledger.chain_check()


def test_forged_audit_entry_fails_chain_check() -> None:
    ledger = AuditLedger()
    _append(ledger, "first")
    _append(ledger, "second")
    ledger._records[1] = replace(ledger._records[1], prev_chain_hash="bad")  # type: ignore[attr-defined]

    with pytest.raises(AuditLedgerChainError):
        ledger.chain_check()
