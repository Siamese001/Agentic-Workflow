"""Shared base for the three meta-learning buses.

Defines the BaseBus contract: append-only, future-run-only, no
current-run mutation. Each concrete bus enforces its own publish
contract on top of this base.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar


class BusPublishError(RuntimeError):
    """Raised when a publish attempt violates a bus invariant."""


# Records are duck-typed: we read .run_id and .sealed_at_unix via getattr
# so any dataclass with those two fields is accepted. Using a plain TypeVar
# rather than a Protocol bound avoids spurious Mypy structural-mismatch
# errors on frozen dataclasses.
T = TypeVar("T")


@dataclass
class BaseBus(Generic[T]):
    """Append-only future-run-only bus."""

    name: str
    current_run_id: str = ""
    records: list[T] = field(default_factory=list)
    rejected: list[dict[str, Any]] = field(default_factory=list)

    def set_current_run(self, run_id: str) -> None:
        """Mark a run as 'in progress'. publish() will reject records
        whose ``run_id`` matches this value, enforcing the future-run-only
        invariant from the v34 mapping."""
        self.current_run_id = run_id

    def end_current_run(self) -> None:
        """Clear the current-run guard (after Exit Eval seals the run)."""
        self.current_run_id = ""

    def _reject(self, record: T, reason: str) -> None:
        self.rejected.append({
            "reason": reason,
            "record_run_id": getattr(record, "run_id", None),
            "bus": self.name,
        })

    def _gate_future_run_only(self, record: T) -> None:
        run_id = getattr(record, "run_id", "")
        if not run_id:
            self._reject(record, "missing_run_id")
            raise BusPublishError(f"{self.name}: record.run_id is empty")
        if self.current_run_id and run_id == self.current_run_id:
            self._reject(record, "current_run_feedback_blocked")
            raise BusPublishError(
                f"{self.name}: record.run_id={run_id!r} matches "
                f"current_run_id — current-run feedback is forbidden "
                "(v34 §future-run-only invariant)."
            )
        if not getattr(record, "sealed_at_unix", 0):
            self._reject(record, "record_not_sealed")
            raise BusPublishError(
                f"{self.name}: record.sealed_at_unix is 0 — only sealed "
                "completed-run records may be published."
            )

    def count(self) -> int:
        return len(self.records)


__all__ = ["BaseBus", "BusPublishError"]
