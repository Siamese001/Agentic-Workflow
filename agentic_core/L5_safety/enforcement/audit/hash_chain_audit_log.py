"""
H2: Hash-chained immutable audit log with genesis rule.

Replaces mutable in-memory ``audit_log: List[...]`` with an
append-only, hash-chained log.  Each entry carries a
``previous_hash`` pointer (sha-256 of prior entry's canonical
bytes).  Chain integrity is verifiable from the deterministic
genesis anchor.

Genesis rule:
  entry_index = 0
  previous_hash = "GENESIS"

Hash computation rules:
  - Computed on canonical serialized bytes (sorted keys, no
    whitespace variance).
  - Timestamp frozen before hash — no mutation after.

Lives in L2 per gravity rules (durable writes are L2-only).
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
)
from agentic_core.utils.canonical_serializer_util import (
    canonical_bytes,
)

Logger = logging.getLogger(__name__)

GENESIS_HASH = "GENESIS"


def _canonical_entry_bytes(
    entry_index: int,
    previous_hash: str,
    timestamp: str,
    tier: str,
    action: str,
    payload: dict[str, Any],
) -> bytes:
    """Deterministic canonical bytes for hash computation.

    Delegates to the shared canonical serializer.
    """
    obj = {
        "action": action,
        "entry_index": entry_index,
        "payload": payload,
        "previous_hash": previous_hash,
        "tier": tier,
        "timestamp": timestamp,
    }
    return canonical_bytes(obj)


@dataclass(frozen=True)
class AuditEntry:
    """Single immutable entry in the hash-chained audit log."""

    entry_index: int
    previous_hash: str
    entry_hash: str
    timestamp: str
    tier: str
    action: str
    payload: dict[str, Any]

    def verify_hash(self) -> bool:
        """Re-derive hash and compare."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "AuditEntry.verify_hash")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AuditEntry.verify_hash".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        canonical = _canonical_entry_bytes(
            entry_index=self.entry_index,
            previous_hash=self.previous_hash,
            timestamp=self.timestamp,
            tier=self.tier,
            action=self.action,
            payload=self.payload,
        )
        return hashlib.sha256(canonical).hexdigest() == self.entry_hash


class HashChainAuditLog:
    """Append-only hash-chained audit log.

    Usage::

        log = HashChainAuditLog()
        log.append(tier="L2", action="persist",
                   payload={"key": "value"})
        assert log.verify_chain_integrity()
    """

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []
        self._sealed: bool = False

    @property
    def length(self) -> int:
        return len(self._entries)

    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        return tuple(self._entries)

    @property
    def chain_root(self) -> str | None:
        """Hash of the last entry, or None if empty."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "HashChainAuditLog.chain_root")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HashChainAuditLog.chain_root".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not self._entries:
            return None
        return self._entries[-1].entry_hash

    def append(
        self,
        *,
        tier: str,
        action: str,
        payload: dict[str, Any] | None = None,
    ) -> AuditEntry:
        """Append a new entry to the chain.

        Timestamp is frozen at call time before hash.
        """
        if self._sealed:
            raise RuntimeError("Audit log is sealed — no further appends.")

        entry_index = len(self._entries)
        previous_hash = GENESIS_HASH if entry_index == 0 else self._entries[-1].entry_hash
        timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        safe_payload = payload if payload is not None else {}

        canonical = _canonical_entry_bytes(
            entry_index=entry_index,
            previous_hash=previous_hash,
            timestamp=timestamp,
            tier=tier,
            action=action,
            payload=safe_payload,
        )
        entry_hash = hashlib.sha256(canonical).hexdigest()

        entry = AuditEntry(
            entry_index=entry_index,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
            timestamp=timestamp,
            tier=tier,
            action=action,
            payload=safe_payload,
        )
        self._entries.append(entry)
        Logger.debug(f"[audit] appended entry {entry_index} hash={entry_hash[:12]}...")
        return entry

    def seal(self) -> str:
        """Seal the log — no further appends allowed.

        Returns the chain root hash.
        """
        if not self._entries:
            raise RuntimeError("Cannot seal empty audit log.")
        self._sealed = True
        root = self._entries[-1].entry_hash
        Logger.debug(f"[audit] sealed at entry {len(self._entries) - 1}, root={root[:12]}...")
        return root

    def verify_chain_integrity(self) -> bool:
        """Replay hash chain from genesis and verify."""
        if not self._entries:
            return True

        for i, entry in enumerate(self._entries):
            if not entry.verify_hash():
                Logger.error(f"[audit] hash mismatch at entry {i}")
                return False

            expected_prev = GENESIS_HASH if i == 0 else self._entries[i - 1].entry_hash
            if entry.previous_hash != expected_prev:
                Logger.error(
                    f"[audit] chain break at entry {i}: "
                    f"expected prev={expected_prev[:12]}... "
                    f"got={entry.previous_hash[:12]}...",
                )
                return False

        return True
