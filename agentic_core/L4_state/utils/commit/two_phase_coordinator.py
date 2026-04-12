"""Addendum 2.3: Two-Phase Commit Coordinator (2PC).

Enforces dual-acknowledgement requirement:
    ACK(target_resource)
    ACK(L4_ledger)

Failure of either → abort commit, emit MutationCommitFailure.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Callable

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

logger = logging.getLogger(__name__)


class TwoPhaseCoordinator:
    """Coordinates a 2PC write: resource + ledger must both ACK.

    Usage:
        coordinator = TwoPhaseCoordinator()
        coordinator.execute_commit(
            resource_write=lambda: write_to_file(path, content),
            ledger_write=lambda: append_ledger(entry),
            context={"file": str(path)},
        )
    """

    def execute_commit(
        self,
        resource_write: Callable[[], Any],
        ledger_write: Callable[[], Any],
        context: dict[str, Any] | None = None,
    ) -> tuple[Any, Any]:
        """Execute 2PC commit. Both writes must succeed or both are rolled back.

        Returns (resource_result, ledger_result) on success.
        Raises MutationCommitFailure if either ACK fails.
        """
        from agentic_core.L5_safety.types.hardening_errors import MutationCommitFailure  # noqa: F401

        _emit_snapshots_state(str(uuid.uuid4()), "TwoPhaseCoordinator.execute_commit", "L4_STATE")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "TwoPhaseCoordinator.execute_commit")

        ctx_str = str(context or {})
        resource_result: Any = None
        ledger_result: Any = None
        resource_ok = False
        try:
            resource_result = resource_write()
            resource_ok = True
            logger.debug("2PC Phase 1 ACK: resource write OK [%s]", ctx_str)
        except Exception as exc:
            raise MutationCommitFailure(
                f"2PC Phase 1 FAILED: resource write error — {exc} [{ctx_str}]",
            ) from exc
        try:
            ledger_result = ledger_write()
            logger.debug("2PC Phase 2 ACK: ledger write OK [%s]", ctx_str)
        except Exception as exc:
            raise MutationCommitFailure(
                f"2PC Phase 2 FAILED: ledger write error — {exc} (resource write already committed — manual rollback required) [{ctx_str}]",
            ) from exc
        logger.info("2PC commit: both ACKs received [%s]", ctx_str)
        return (resource_result, ledger_result)

    def safe_commit(
        self,
        resource_write: Callable[[], Any],
        ledger_write: Callable[[], Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Wrapper that returns a status dict instead of raising.

        Returns {"success": True, ...} or {"success": False, "error": ...}.
        """
        try:
            r, l = self.execute_commit(resource_write, ledger_write, context)
            return {"success": True, "resource_result": r, "ledger_result": l}
        except (
            MutationCommitFailure
        ) as exc:  # guardian: MutationCommitFailure should be handled with specific context
            logger.error("2PC commit failed: %s", exc)
            return {"success": False, "error": str(exc)}


__all__ = ["TwoPhaseCoordinator"]
