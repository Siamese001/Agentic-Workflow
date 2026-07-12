"""Idempotent projection-outbox runner.

A projector may mutate only a derived read surface.  Canonical state already
exists before a handler is invoked, and every attempt is recorded in the
SQLite outbox so a process restart can safely resume incomplete work.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from agentic_core.L4_state.storage.sqlite_backend import (
    ProjectionOutboxItem,
    SQLiteL4Backend,
)

ProjectionHandler = Callable[[ProjectionOutboxItem], Mapping[str, Any] | None]


@dataclass(frozen=True)
class ProjectionRunResult:
    projection_id: str
    projection_type: str
    status: str
    receipt: dict[str, Any]


class ProjectionRunner:
    """Run pending projection rows using explicitly registered handlers."""

    def __init__(
        self,
        backend: SQLiteL4Backend,
        *,
        handlers: Mapping[str, ProjectionHandler] | None = None,
    ) -> None:
        self.backend = backend
        self.handlers: dict[str, ProjectionHandler] = dict(handlers or {})

    def register(self, projection_type: str, handler: ProjectionHandler) -> None:
        if not projection_type:
            raise ValueError("projection_type is required")
        self.handlers[projection_type] = handler

    def run_pending(
        self,
        *,
        commit_receipt_id: str | None = None,
        retry_failed: bool = True,
        raise_on_failure: bool = False,
        limit: int = 100,
    ) -> list[ProjectionRunResult]:
        statuses = ("PENDING", "FAILED") if retry_failed else ("PENDING",)
        rows = self.backend.list_projection_outbox(
            commit_receipt_id=commit_receipt_id,
            statuses=statuses,
            limit=limit,
        )
        results: list[ProjectionRunResult] = []
        for row in rows:
            handler = self.handlers.get(row.projection_type)
            if handler is None:
                receipt = self.backend.fail_projection(
                    item=row,
                    error=f"projection_handler_missing::{row.projection_type}",
                )
                results.append(
                    ProjectionRunResult(
                        projection_id=row.projection_id,
                        projection_type=row.projection_type,
                        status="FAILED",
                        receipt=receipt,
                    )
                )
                if raise_on_failure:
                    raise RuntimeError(receipt["reason"])
                continue

            running = self.backend.mark_projection_running(row.projection_id)
            try:
                outcome = dict(handler(running) or {})
                requested_status = str(outcome.pop("status", "COMPLETE") or "COMPLETE").upper()
                if requested_status not in {"COMPLETE", "SKIPPED"}:
                    raise RuntimeError(
                        f"invalid projector terminal status={requested_status!r}"
                    )
                receipt = self.backend.complete_projection(
                    item=running,
                    result=outcome,
                    status=requested_status,
                )
                results.append(
                    ProjectionRunResult(
                        projection_id=running.projection_id,
                        projection_type=running.projection_type,
                        status=requested_status,
                        receipt=receipt,
                    )
                )
            except Exception as exc:
                receipt = self.backend.fail_projection(item=running, error=exc)
                results.append(
                    ProjectionRunResult(
                        projection_id=running.projection_id,
                        projection_type=running.projection_type,
                        status="FAILED",
                        receipt=receipt,
                    )
                )
                if raise_on_failure:
                    raise
        return results


__all__ = ["ProjectionHandler", "ProjectionRunResult", "ProjectionRunner"]
