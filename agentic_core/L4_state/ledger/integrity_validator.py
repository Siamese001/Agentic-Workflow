"""Addendum 2.2: Ledger Integrity Validator.

Before L4 commit, verify hash chain:
    hash(prev_hash + entry_bytes) == stored_hash

Raises LedgerIntegrityViolation on mismatch.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation

logger = logging.getLogger(__name__)

_GENESIS_HASH = "0" * 64


def compute_entry_hash(prev_hash: str, entry: dict[str, Any]) -> str:
    """Compute chained SHA256: hash(prev_hash || entry_bytes)."""
    entry_bytes = json.dumps(entry, sort_keys=True, ensure_ascii=True, default=str).encode()
    payload = (prev_hash + entry_bytes.decode()).encode()
    return hashlib.sha256(payload).hexdigest()


def validate_ledger_chain(entries: list[dict[str, Any]]) -> None:
    """Walk the ledger chain and raise LedgerIntegrityViolation on first broken link.

    Each entry must have a ``_hash`` field computed from the previous hash
    and the entry data (excluding the ``_hash`` field itself).
    """
    prev_hash = _GENESIS_HASH
    for idx, entry in enumerate(entries):
        stored_hash = entry.get("_hash")
        if stored_hash is None:
            raise LedgerIntegrityViolation(
                f"Ledger entry {idx} missing '_hash' field — integrity cannot be verified"
            )
        entry_without_hash = {k: v for k, v in entry.items() if k != "_hash"}
        expected_hash = compute_entry_hash(prev_hash, entry_without_hash)
        if expected_hash != stored_hash:
            raise LedgerIntegrityViolation(
                f"Ledger hash mismatch at entry {idx}: "
                f"expected={expected_hash[:16]}... stored={stored_hash[:16]}..."
            )
        prev_hash = stored_hash


def append_with_hash(
    entries: list[dict[str, Any]],
    new_entry: dict[str, Any],
) -> dict[str, Any]:
    """Append a new entry to the ledger list, computing its chained hash.

    Returns the entry dict with ``_hash`` set.
    """
    prev_hash = entries[-1]["_hash"] if entries else _GENESIS_HASH
    entry_without_hash = {k: v for k, v in new_entry.items() if k != "_hash"}
    new_hash = compute_entry_hash(prev_hash, entry_without_hash)
    hashed_entry = {**entry_without_hash, "_hash": new_hash}
    entries.append(hashed_entry)
    return hashed_entry


def validate_ledger_file(ledger_path: Path) -> None:
    """Load a JSONL ledger file and validate its hash chain."""
    if not ledger_path.exists():
        return
    entries: list[dict[str, Any]] = []
    with open(ledger_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    validate_ledger_chain(entries)
    logger.debug("Ledger integrity OK: %d entries in %s", len(entries), ledger_path)


__all__ = [
    "compute_entry_hash",
    "validate_ledger_chain",
    "append_with_hash",
    "validate_ledger_file",
]
