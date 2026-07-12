"""Restart-safe AuditLedger backed by the canonical L4 SQLite database."""

from __future__ import annotations

from typing import Any, Mapping

from agentic_core.L4_state.audit.audit_ledger import AuditAppendReceipt, AuditLedger
from agentic_core.L4_state.contracts.records import AuditLedgerRecord
from agentic_core.L4_state.storage.sqlite_backend import SQLiteL4Backend


_TUPLE_FIELDS = ("receipt_refs", "state_refs", "reason_codes")


def _record_from_payload(payload: Mapping[str, Any]) -> AuditLedgerRecord:
    data = dict(payload)
    for field in _TUPLE_FIELDS:
        if isinstance(data.get(field), list):
            data[field] = tuple(data[field])
    return AuditLedgerRecord(**data)


class SQLiteAuditLedger(AuditLedger):
    """Append-only audit ledger persisted in the shared L4 transaction store."""

    def __init__(self, backend: SQLiteL4Backend) -> None:
        self.backend = backend
        super().__init__()
        self.reload()

    def reload(self) -> None:
        records = [_record_from_payload(row) for row in self.backend.load_audit_records()]
        with self._lock:  # type: ignore[attr-defined]
            self._records = list(records)  # type: ignore[attr-defined]
            self._receipts = {}  # type: ignore[attr-defined]
            self._sequence_counter = records[-1].ledger_sequence if records else 0  # type: ignore[attr-defined]
            self._last_chain_hash = records[-1].chain_hash if records else self.genesis_hash  # type: ignore[attr-defined]

    def _persist(self, record: AuditLedgerRecord) -> None:
        self.backend.persist_audit_record(record)

    def sync_committed_record(
        self,
        record: AuditLedgerRecord,
        receipt: AuditAppendReceipt | None = None,
    ) -> None:
        """Refresh in-memory state after the backend inserted a record atomically."""

        with self._lock:  # type: ignore[attr-defined]
            if not any(
                existing.audit_record_id == record.audit_record_id
                for existing in self._records  # type: ignore[attr-defined]
            ):
                self._records.append(record)  # type: ignore[attr-defined]
                self._records.sort(key=lambda item: item.ledger_sequence)  # type: ignore[attr-defined]
            self._sequence_counter = max(  # type: ignore[attr-defined]
                self._sequence_counter, record.ledger_sequence  # type: ignore[attr-defined]
            )
            self._last_chain_hash = self._records[-1].chain_hash  # type: ignore[attr-defined]
            if receipt is not None:
                self._receipts[receipt.audit_append_receipt_id] = receipt  # type: ignore[attr-defined]


__all__ = ["SQLiteAuditLedger"]
