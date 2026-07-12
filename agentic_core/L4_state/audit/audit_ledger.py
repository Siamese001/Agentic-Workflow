"""Append-only, hash-chained L4 audit ledger.

Runtime defaults to a restart-safe SQLite implementation backed by the same
canonical database used by transactional UWG commits. ``AuditLedger`` remains
an explicit in-memory implementation for hermetic tests.
"""

from __future__ import annotations

import os
import threading
import uuid
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Tuple

from agentic_core.L4_state.contracts.digests import compute_deterministic_digest
from agentic_core.L4_state.contracts.records import (
    L4_CONTRACT_SCHEMA_VERSION,
    AuditLedgerRecord,
    stamp_digest,
)


class AuditLedgerUnavailableError(RuntimeError):
    """Raised when the ledger cannot accept an append."""


class AuditLedgerSequenceGapError(RuntimeError):
    """Raised when sequence continuity is broken."""


class AuditLedgerChainError(RuntimeError):
    """Raised when hash-chain evidence is invalid."""


@dataclass(frozen=True)
class AuditAppendReceipt:
    """Receipt for a successful audit-ledger append."""

    audit_append_receipt_id: str
    audit_record_id: str
    ledger_sequence: int
    snapshot_position: int
    deterministic_digest: str
    schema_version: str = L4_CONTRACT_SCHEMA_VERSION
    prev_chain_hash: str = ""
    chain_hash: str = ""


class AuditLedger:
    """Thread-safe in-memory audit ledger.

    Runtime callers should normally obtain the default ledger through
    :func:`get_default_ledger`, which uses SQLite unless explicitly configured
    for in-memory operation.
    """

    def __init__(self) -> None:
        self._records: List[AuditLedgerRecord] = []
        self._receipts: Dict[str, AuditAppendReceipt] = {}
        self._sequence_counter = 0
        self._lock = threading.RLock()
        self._available = True
        self._last_chain_hash = self.genesis_hash

    @property
    def genesis_hash(self) -> str:
        return compute_deterministic_digest(
            {"audit_ledger_genesis": L4_CONTRACT_SCHEMA_VERSION}
        )

    def set_available(self, available: bool) -> None:
        with self._lock:
            self._available = available

    def is_available(self) -> bool:
        with self._lock:
            return self._available

    def position(self) -> int:
        with self._lock:
            return len(self._records)

    def next_sequence(self) -> int:
        """Reserve an in-memory sequence number.

        Transactional commit paths do not use this helper; their durable
        backend allocates the sequence inside ``BEGIN IMMEDIATE``.
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
        """Append one immutable record, persisting before publishing in memory."""

        with self._lock:
            if not self._available:
                raise AuditLedgerUnavailableError("audit ledger is marked unavailable")
            seq = self._sequence_counter + 1
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
                created_at=str(seq),
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

            # Persist first. A failed durable write must not advance the visible
            # in-memory ledger position.
            self._persist(record)
            self._sequence_counter = seq
            self._last_chain_hash = chain_hash
            self._records.append(record)
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
        with self._lock:
            return [r for r in self._records if r.ledger_sequence > since_sequence]

    def get_record(self, audit_record_id: str) -> Optional[AuditLedgerRecord]:
        with self._lock:
            return next(
                (row for row in self._records if row.audit_record_id == audit_record_id),
                None,
            )

    def get_append_receipt(self, receipt_id: str) -> Optional[AuditAppendReceipt]:
        with self._lock:
            return self._receipts.get(receipt_id)

    def sequence_check(self) -> None:
        with self._lock:
            for idx, record in enumerate(self._records):
                expected = idx + 1
                if record.ledger_sequence != expected:
                    raise AuditLedgerSequenceGapError(
                        f"ledger gap: position {idx} has sequence "
                        f"{record.ledger_sequence}, expected {expected}"
                    )

    def chain_check(self) -> None:
        with self._lock:
            prev = self.genesis_hash
            for idx, record in enumerate(self._records):
                if record.prev_chain_hash != prev:
                    raise AuditLedgerChainError(
                        f"chain gap: position {idx + 1} prev_chain_hash "
                        f"{record.prev_chain_hash!r}, expected {prev!r}"
                    )
                base = stamp_digest(
                    replace(record, chain_hash="", deterministic_digest="")
                )
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
        return self.get_record(audit_record_id) is not None

    def _persist(self, record: AuditLedgerRecord) -> None:
        """Persistence hook for subclasses; in-memory ledger is intentionally no-op."""

        del record


_DEFAULT_LEDGER: Optional[AuditLedger] = None
_DEFAULT_LOCK = threading.Lock()


def _default_is_memory() -> bool:
    configured = str(os.environ.get("L4_STORAGE_BACKEND", "")).strip().lower()
    if configured:
        return configured == "memory"
    return bool(os.environ.get("PYTEST_CURRENT_TEST"))


def get_default_ledger() -> AuditLedger:
    """Return the process-wide default ledger.

    Runtime default: durable SQLite. Hermetic tests default to memory unless
    ``L4_STORAGE_BACKEND=sqlite`` is explicitly supplied.
    """

    global _DEFAULT_LEDGER  # noqa: PLW0603
    with _DEFAULT_LOCK:
        if _DEFAULT_LEDGER is None:
            if _default_is_memory():
                _DEFAULT_LEDGER = AuditLedger()
            else:
                from agentic_core.L4_state.audit.sqlite_audit_ledger import (
                    SQLiteAuditLedger,
                )
                from agentic_core.L4_state.storage.sqlite_backend import (
                    get_default_backend,
                )

                backend = get_default_backend()
                if backend is None:
                    _DEFAULT_LEDGER = AuditLedger()
                else:
                    _DEFAULT_LEDGER = SQLiteAuditLedger(backend)
        return _DEFAULT_LEDGER


def reset_default_ledger() -> None:
    """Reset the process singleton; durable data is retained by default."""

    global _DEFAULT_LEDGER  # noqa: PLW0603
    with _DEFAULT_LOCK:
        _DEFAULT_LEDGER = None


__all__ = [
    "AuditAppendReceipt",
    "AuditLedger",
    "AuditLedgerChainError",
    "AuditLedgerSequenceGapError",
    "AuditLedgerUnavailableError",
    "get_default_ledger",
    "reset_default_ledger",
]
