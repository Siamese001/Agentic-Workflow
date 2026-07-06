"""Append-only L4 audit ledger (00.5 §PHASE 3).

Doctrinal requirements (00.5):
- ledger is append-only (no overwrites, no deletes)
- monotonically-increasing ``ledger_sequence``
- correction uses ``append_record`` with ``supersedes_ref``, not mutation
- ``sequence_check`` detects gaps
- ledger unavailable -> commit fails closed

This implementation is in-memory (a list + lock) by default. Real
deployments wire a durable backing store (SQLite/Postgres/cloud) by
subclassing :class:`AuditLedger` and overriding ``_persist`` /
``_load_position``.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional, Tuple

from agentic_core.L4_state.contracts.digests import compute_deterministic_digest
from agentic_core.L4_state.contracts.records import (
    AuditLedgerRecord,
    L4_CONTRACT_SCHEMA_VERSION,
    record_canonical_payload,
    stamp_digest,
)


class AuditLedgerUnavailableError(RuntimeError):
    """Raised when the ledger cannot be reached for an append.

    Per 00.5 §PHASE 3 "Ledger unavailable means commit fails closed".
    """


class AuditLedgerSequenceGapError(RuntimeError):
    """Raised when ``sequence_check()`` detects a gap.

    Per 00.5 §PHASE 6 "audit ledger sequence gap is ignored" must fail tests.
    """


class AuditLedgerChainError(RuntimeError):
    """Raised when ``chain_check()`` detects broken hash-chain evidence."""


@dataclass(frozen=True)
class AuditAppendReceipt:
    """Receipt for a successful audit ledger append."""

    audit_append_receipt_id: str
    audit_record_id: str
    ledger_sequence: int
    snapshot_position: int
    deterministic_digest: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    prev_chain_hash: str = ""
    chain_hash: str = ""


class AuditLedger:
    """In-memory append-only ledger with monotonic sequencing.

    Thread-safe. Subclass to back with durable storage.
    """

    def __init__(self) -> None:
        self._records: List[AuditLedgerRecord] = []
        self._receipts: Dict[str, AuditAppendReceipt] = {}
        self._sequence_counter: int = 0
        self._lock = threading.RLock()
        self._available: bool = True
        self._last_chain_hash: str = compute_deterministic_digest(
            {"audit_ledger_genesis": L4_CONTRACT_SCHEMA_VERSION}
        )

    def set_available(self, available: bool) -> None:
        """Toggle ledger availability (test/maintenance hook)."""
        with self._lock:
            self._available = available

    def is_available(self) -> bool:
        with self._lock:
            return self._available

    def position(self) -> int:
        """Return the current ledger position (number of records written)."""
        with self._lock:
            return len(self._records)

    def next_sequence(self) -> int:
        """Allocate the next sequence number without writing a record.

        Used by callers that need to compute a record's digest before append.
        Holds the lock briefly.
        """
        with self._lock:
            self._sequence_counter += 1
            return self._sequence_counter

    def append(
        self,
        *,
        event_type: str,
        state_surface: str,
        operation_type: str,
        tenant_id: str,
        policy_hash: str,
        blueprint_hash: str,
        snapshot_before: str,
        actor_surface: str,
        mutation_source: str,
        snapshot_after: Optional[str] = None,
        request_id: Optional[str] = None,
        run_id: Optional[str] = None,
        trace_root: Optional[str] = None,
        receipt_refs: Tuple[str, ...] = (),
        state_refs: Tuple[str, ...] = (),
        reason_codes: Tuple[str, ...] = (),
        supersedes_ref: Optional[str] = None,
    ) -> Tuple[AuditLedgerRecord, AuditAppendReceipt]:
        """Append a record to the ledger.

        Raises :class:`AuditLedgerUnavailableError` if the ledger is
        marked unavailable.
        """
        with self._lock:
            if not self._available:
                raise AuditLedgerUnavailableError("audit ledger is marked unavailable")
            self._sequence_counter += 1
            seq = self._sequence_counter
            record = AuditLedgerRecord(
                audit_record_id=str(uuid.uuid4()),
                ledger_sequence=seq,
                event_type=event_type,
                state_surface=state_surface,
                operation_type=operation_type,
                tenant_id=tenant_id,
                policy_hash=policy_hash,
                blueprint_hash=blueprint_hash,
                snapshot_before=snapshot_before,
                actor_surface=actor_surface,
                mutation_source=mutation_source,
                created_at=str(seq),  # ledger-relative (not wall clock — clock policy)
                snapshot_after=snapshot_after,
                request_id=request_id,
                run_id=run_id,
                trace_root=trace_root,
                receipt_refs=receipt_refs,
                state_refs=state_refs,
                reason_codes=reason_codes,
                supersedes_ref=supersedes_ref,
                prev_chain_hash=self._last_chain_hash,
            )
            record = stamp_digest(record)
            chain_hash = compute_deterministic_digest(
                {
                    "prev_chain_hash": self._last_chain_hash,
                    "record_digest": record.deterministic_digest,
                }
            )
            record = stamp_digest(
                replace(record, chain_hash=chain_hash, deterministic_digest="")
            )
            self._last_chain_hash = chain_hash
            self._records.append(record)
            self._persist(record)
            receipt = AuditAppendReceipt(
                audit_append_receipt_id=str(uuid.uuid4()),
                audit_record_id=record.audit_record_id,
                ledger_sequence=seq,
                snapshot_position=len(self._records),
                deterministic_digest=record.deterministic_digest,
                prev_chain_hash=record.prev_chain_hash,
                chain_hash=record.chain_hash,
            )
            self._receipts[receipt.audit_append_receipt_id] = receipt
            return record, receipt

    def read(self, *, since_sequence: int = 0) -> List[AuditLedgerRecord]:
        """Read records with ``ledger_sequence > since_sequence``."""
        with self._lock:
            return [r for r in self._records if r.ledger_sequence > since_sequence]

    def get_record(self, audit_record_id: str) -> Optional[AuditLedgerRecord]:
        with self._lock:
            for record in self._records:
                if record.audit_record_id == audit_record_id:
                    return record
            return None

    def sequence_check(self) -> None:
        """Verify the ledger has no sequence gaps. Raises on detection."""
        with self._lock:
            for idx, record in enumerate(self._records):
                expected = idx + 1
                if record.ledger_sequence != expected:
                    raise AuditLedgerSequenceGapError(
                        f"ledger gap: position {idx} has sequence "
                        f"{record.ledger_sequence}, expected {expected}"
                    )

    def chain_check(self) -> None:
        """Verify every record links to the previous hash and recomputes."""
        with self._lock:
            prev = compute_deterministic_digest(
                {"audit_ledger_genesis": L4_CONTRACT_SCHEMA_VERSION}
            )
            for idx, record in enumerate(self._records):
                if record.prev_chain_hash != prev:
                    raise AuditLedgerChainError(
                        f"chain gap: position {idx + 1} prev_chain_hash "
                        f"{record.prev_chain_hash!r}, expected {prev!r}"
                    )
                base = replace(record, chain_hash="", deterministic_digest="")
                base = stamp_digest(base)
                expected = compute_deterministic_digest(
                    {
                        "prev_chain_hash": prev,
                        "record_digest": base.deterministic_digest,
                    }
                )
                if record.chain_hash != expected:
                    raise AuditLedgerChainError(
                        f"chain hash mismatch: position {idx + 1} has "
                        f"{record.chain_hash!r}, expected {expected!r}"
                    )
                prev = record.chain_hash

    def is_overwrite_attempted(self, audit_record_id: str) -> bool:
        """Return True if ``audit_record_id`` already exists.

        UWG callers MUST check before issuing a correction; corrections use
        ``append_record`` + ``supersedes_ref`` (00.5 §PHASE 3).
        """
        return self.get_record(audit_record_id) is not None

    # Subclass hooks ------------------------------------------------------

    def _persist(self, record: AuditLedgerRecord) -> None:
        """Override in subclass for durable persistence."""
        # In-memory implementation: nothing to do; record already in self._records.
        del record


# Default singleton ----------------------------------------------------------

_DEFAULT_LEDGER: Optional[AuditLedger] = None
_DEFAULT_LOCK = threading.Lock()


def get_default_ledger() -> AuditLedger:
    """Return the process-wide default ledger (lazy-initialized)."""
    global _DEFAULT_LEDGER  # noqa: PLW0603
    with _DEFAULT_LOCK:
        if _DEFAULT_LEDGER is None:
            _DEFAULT_LEDGER = AuditLedger()
        return _DEFAULT_LEDGER


def reset_default_ledger() -> None:
    """Reset the default ledger (test hook)."""
    global _DEFAULT_LEDGER  # noqa: PLW0603
    with _DEFAULT_LOCK:
        _DEFAULT_LEDGER = AuditLedger()


__all__ = [
    "AuditAppendReceipt",
    "AuditLedgerChainError",
    "AuditLedger",
    "AuditLedgerSequenceGapError",
    "AuditLedgerUnavailableError",
    "get_default_ledger",
    "reset_default_ledger",
]
