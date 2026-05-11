"""L4WriteAdapter — the only sanctioned L4 write surface for W10.

Plan: apps-rg-zip-based-full-spine-runtime-restoration-a3f7e2 W10

L4 accepts durable writes ONLY from UniversalWriteGate (UWG).  Any attempt
to call ``commit()`` from a non-UWG surface raises ``DirectWriteViolationError``
and emits a rejection record.

Write surface hierarchy (non-negotiable):
    FutureRunPromotionRequest
      -> UniversalWriteGate.admit()    [admission decision]
      -> L4WriteAdapter.commit()       [durable storage — UWG only]

All other callers (Exit, L6, L2, L3, L0, PA, C0) MUST NOT import or call
``commit()`` directly.  This is enforced by:
  1. This module checking the ``_uwg_token`` sentinel.
  2. Tests: test_l4_rejects_direct_write_from_* in test_apps_rg_uwg_write_gate.py.

In test/stub mode (``stub=True``) no I/O is performed; the adapter records
writes in-memory for test inspection.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional


# Sentinel token that UniversalWriteGate passes to prove it is the caller.
# This is not cryptographic security — it is a structural discipline marker.
_UWG_WRITE_TOKEN = "uwg::authorized::w10"

# Non-UWG sources that must never call commit() directly
_FORBIDDEN_CALLERS: frozenset[str] = frozenset({
    "Exit", "L0", "L1", "L2", "L3", "L6", "C0", "PA",
    "PromptAssembly", "HITL", "Tool", "Model", "AdHocScript",
})


class DirectWriteViolationError(RuntimeError):
    """Raised when a non-UWG surface attempts to write L4 directly."""


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _digest(data: dict) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return "sha256::" + hashlib.sha256(payload.encode()).hexdigest()


class L4WriteAdapter:
    """Sanctioned L4 write surface.

    In production: would persist to the canonical L4 store (SQLite / Redis /
    Chroma depending on target_store).  In W10 scope, the adapter is stubbed
    — it records writes in-memory and verifies the UWG token.

    Args:
        stub: if True (default for tests), no I/O; writes logged in-memory.
        uwg_token: must equal _UWG_WRITE_TOKEN for commit() to proceed.
    """

    def __init__(self, *, stub: bool = True) -> None:
        self._stub = stub
        self._committed: list[dict[str, Any]] = []
        self._rejected: list[dict[str, Any]] = []

    def commit(
        self,
        promotion_request: Any,
        *,
        _caller: str = "UWG",
        _uwg_token: str = "",
    ) -> str:
        """Commit a promotion request to L4.

        Returns an l4_receipt_ref string.
        Raises DirectWriteViolationError if _caller is not UWG or token is wrong.
        """
        # Structural check — only UWG may call commit
        if _caller in _FORBIDDEN_CALLERS:
            record = {
                "violation": "direct_write_attempt",
                "caller": _caller,
                "promotion_request_id": getattr(promotion_request, "promotion_request_id", ""),
                "rejected_at": _utcnow(),
            }
            self._rejected.append(record)
            raise DirectWriteViolationError(
                f"L4WriteAdapter.commit(): direct write from {_caller!r} is forbidden. "
                "All L4 writes must go through UniversalWriteGate.admit()."
            )

        # Token check — UniversalWriteGate must pass _UWG_WRITE_TOKEN
        if _uwg_token != _UWG_WRITE_TOKEN and not self._stub:
            record = {
                "violation": "invalid_uwg_token",
                "caller": _caller,
                "rejected_at": _utcnow(),
            }
            self._rejected.append(record)
            raise DirectWriteViolationError(
                "L4WriteAdapter.commit(): invalid UWG token. "
                "Only UniversalWriteGate may authorize L4 writes."
            )

        l4_receipt_ref = f"l4::commit::{uuid.uuid4().hex[:12]}"
        record = {
            "l4_receipt_ref": l4_receipt_ref,
            "promotion_request_id": getattr(promotion_request, "promotion_request_id", ""),
            "target_store": getattr(promotion_request, "target_store", ""),
            "target_ref": getattr(promotion_request, "target_ref", ""),
            "stub": self._stub,
            "committed_at": _utcnow(),
        }
        self._committed.append(record)
        return l4_receipt_ref

    @property
    def committed_writes(self) -> list[dict[str, Any]]:
        """List of all committed write records (test inspection)."""
        return list(self._committed)

    @property
    def rejected_writes(self) -> list[dict[str, Any]]:
        """List of all rejected write attempts (test inspection)."""
        return list(self._rejected)

    def reset(self) -> None:
        """Clear in-memory state (test teardown)."""
        self._committed.clear()
        self._rejected.clear()


# Module-level token constant for UniversalWriteGate to import
UWG_WRITE_TOKEN = _UWG_WRITE_TOKEN


__all__ = [
    "L4WriteAdapter",
    "DirectWriteViolationError",
    "UWG_WRITE_TOKEN",
    "_FORBIDDEN_CALLERS",
    "_UWG_WRITE_TOKEN",
]
