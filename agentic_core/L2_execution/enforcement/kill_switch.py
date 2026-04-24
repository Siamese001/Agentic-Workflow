"""
Workflow kill-switch — W4-P4.3 (gap plan b7c4e2: G12).

codebridge.tech 2026 pattern: "kill switches must interrupt an agent
without collapsing the workflow." This module provides a lineage-scoped
kill-switch that:

1. Marks a specific step lineage as **tripped** — subsequent attempts to
   enter E3 (execute) for the same lineage are blocked.
2. Preserves state: the trip record holds a reason + timestamp so
   downstream recovery can distinguish "user cancelled" from "policy
   blocked" without guessing.
3. Is separate from E4's ESCALATED tier — ESCALATED is a *per-step*
   decision by the healing router; the kill-switch is a *workflow-wide*
   shutdown that prevents ANY further step under the same lineage.

Thread-safe and in-memory. Registries are keyed by ``lineage_id`` —
typically the trace_id or a plan-scoped identifier.

Guardian note: narrow exceptions only.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "KillSwitchTripped",
    "KillSwitchRecord",
    "KillSwitchRegistry",
    "default_registry",
    "trip",
    "is_tripped",
    "get_record",
    "untrip",
]


class KillSwitchTripped(Exception):
    """Raised when a caller attempts to enter E3 for a tripped lineage."""

    def __init__(self, record: "KillSwitchRecord") -> None:
        super().__init__(
            f"lineage={record.lineage_id!r} kill-switch tripped "
            f"reason={record.reason!r} at={record.tripped_at}"
        )
        self.record = record


@dataclass(frozen=True, slots=True)
class KillSwitchRecord:
    """Immutable record of a trip event."""

    lineage_id: str
    reason: str
    tripped_at: float
    tripped_by: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "lineage_id": self.lineage_id,
            "reason": self.reason,
            "tripped_at": self.tripped_at,
            "tripped_by": self.tripped_by,
            "metadata": dict(self.metadata),
        }


class KillSwitchRegistry:
    """Thread-safe registry of tripped lineages."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._records: dict[str, KillSwitchRecord] = {}

    def trip(
        self,
        *,
        lineage_id: str,
        reason: str,
        tripped_by: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> KillSwitchRecord:
        """Record a trip for ``lineage_id``. Idempotent — re-tripping is a no-op
        that returns the existing record."""
        if not lineage_id:
            raise ValueError("lineage_id is required")
        if not reason:
            raise ValueError("reason is required")
        with self._lock:
            existing = self._records.get(lineage_id)
            if existing is not None:
                return existing
            record = KillSwitchRecord(
                lineage_id=lineage_id,
                reason=reason,
                tripped_at=time.time(),
                tripped_by=tripped_by,
                metadata=dict(metadata or {}),
            )
            self._records[lineage_id] = record
            return record

    def is_tripped(self, lineage_id: str) -> bool:
        with self._lock:
            return lineage_id in self._records

    def get_record(self, lineage_id: str) -> KillSwitchRecord | None:
        with self._lock:
            return self._records.get(lineage_id)

    def untrip(self, lineage_id: str) -> bool:
        """Clear a trip. Returns True if a record existed."""
        with self._lock:
            return self._records.pop(lineage_id, None) is not None

    def raise_if_tripped(self, lineage_id: str) -> None:
        """Call at E3 entry. Raises ``KillSwitchTripped`` if the lineage is down."""
        rec = self.get_record(lineage_id)
        if rec is not None:
            raise KillSwitchTripped(rec)

    def snapshot(self) -> dict[str, KillSwitchRecord]:
        with self._lock:
            return dict(self._records)

    def clear(self) -> None:
        """Test-only helper."""
        with self._lock:
            self._records.clear()


_default = KillSwitchRegistry()


def default_registry() -> KillSwitchRegistry:
    return _default


def trip(
    *,
    lineage_id: str,
    reason: str,
    tripped_by: str = "",
    metadata: dict[str, Any] | None = None,
) -> KillSwitchRecord:
    """Trip the default registry."""
    return _default.trip(
        lineage_id=lineage_id,
        reason=reason,
        tripped_by=tripped_by,
        metadata=metadata,
    )


def is_tripped(lineage_id: str) -> bool:
    return _default.is_tripped(lineage_id)


def get_record(lineage_id: str) -> KillSwitchRecord | None:
    return _default.get_record(lineage_id)


def untrip(lineage_id: str) -> bool:
    return _default.untrip(lineage_id)
