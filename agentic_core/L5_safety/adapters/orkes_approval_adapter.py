"""Orkes Conductor implementation of ``HumanApprovalAdapter``.

Uses Orkes HUMAN task semantics. The adapter creates a HUMAN task bound to
the provided ``task_def_name`` and tracks its lifecycle via ``TASK_STATUS``.

Orkes task status → approval outcome mapping:

    IN_PROGRESS / SCHEDULED → PENDING
    COMPLETED               → APPROVED | DENIED (from task output ``decision``)
    FAILED                  → DENIED (reason_code = ORKES_FAILED)
    TIMED_OUT               → TIMEOUT
    TERMINATED / CANCELED   → TIMEOUT (reason_code = CANCELLED)
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerEntry,
)
from agentic_core.L5_safety.adapters.human_approval_adapter import (
    AdapterError,
    ApprovalHandle,
    ApprovalOutcome,
    ApprovalOutcomeKind,
    HumanApprovalAdapter,
)


TASK_IN_PROGRESS = "IN_PROGRESS"
TASK_SCHEDULED = "SCHEDULED"
TASK_COMPLETED = "COMPLETED"
TASK_FAILED = "FAILED"
TASK_TIMED_OUT = "TIMED_OUT"
TASK_TERMINATED = "TERMINATED"
TASK_CANCELED = "CANCELED"

DECISION_APPROVE = "approve"
DECISION_DENY = "deny"


class OrkesTransport(Protocol):
    """Minimal Orkes Conductor surface this adapter depends on."""

    def create_human_task(
        self,
        task_def_name: str,
        input_data: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        ...

    def get_human_task(self, task_id: str) -> Mapping[str, Any]:
        ...

    def terminate_human_task(self, task_id: str, reason: str) -> Mapping[str, Any]:
        ...


class OrkesApprovalAdapter(HumanApprovalAdapter):
    """Orkes HUMAN-task approval adapter."""

    kind = "orkes"

    def __init__(self, *, task_def_name: str, transport: OrkesTransport) -> None:
        if not task_def_name:
            raise ValueError("task_def_name is required")
        self._task_def = task_def_name
        self._transport = transport

    def enqueue(self, entry: LedgerEntry) -> ApprovalHandle:
        input_data = {
            "ledger_id": entry.ledger_id,
            "run_id": entry.run_id,
            "trace_id": entry.trace_id,
            "hitl_class": entry.hitl_class.value,
            "approver_pool": entry.approver_pool,
            "timeout_s": entry.timeout_s,
            "policy_snapshot": entry.policy_snapshot,
            "envelope": dict(entry.envelope),
        }
        try:
            task = self._transport.create_human_task(self._task_def, input_data)
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: wraps arbitrary transport errors into AdapterError so callers handle a single exception type
            raise AdapterError(f"Orkes create_human_task failed: {exc}") from exc

        task_id = task.get("task_id") if isinstance(task, Mapping) else None
        if not task_id:
            raise AdapterError("Orkes create_human_task returned no task_id")
        return ApprovalHandle(
            adapter_kind=self.kind,
            external_id=str(task_id),
            ledger_id=entry.ledger_id,
        )

    def poll(self, handle: ApprovalHandle) -> ApprovalOutcome | None:
        self._require_handle(handle)
        try:
            task = self._transport.get_human_task(handle.external_id)
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: wraps arbitrary transport errors into AdapterError so callers handle a single exception type
            raise AdapterError(f"Orkes get_human_task failed: {exc}") from exc

        status = _read(task, "status") or TASK_IN_PROGRESS

        if status in (TASK_IN_PROGRESS, TASK_SCHEDULED):
            return None
        if status == TASK_COMPLETED:
            output = task.get("output") if isinstance(task, Mapping) else None
            output = output if isinstance(output, Mapping) else {}
            decision = _read(output, "decision") or ""
            if decision == DECISION_APPROVE:
                return ApprovalOutcome(
                    kind=ApprovalOutcomeKind.APPROVED,
                    approver_id=_read(output, "approver_id"),
                    rationale=_read(output, "rationale"),
                )
            if decision == DECISION_DENY:
                return ApprovalOutcome(
                    kind=ApprovalOutcomeKind.DENIED,
                    approver_id=_read(output, "approver_id"),
                    reason_code=_read(output, "reason_code") or "ORKES_DENIED",
                    rationale=_read(output, "rationale"),
                )
            raise AdapterError(f"Unrecognized Orkes decision: {decision!r}")
        if status == TASK_FAILED:
            return ApprovalOutcome(
                kind=ApprovalOutcomeKind.DENIED, reason_code="ORKES_FAILED"
            )
        if status == TASK_TIMED_OUT:
            return ApprovalOutcome(kind=ApprovalOutcomeKind.TIMEOUT)
        if status in (TASK_TERMINATED, TASK_CANCELED):
            return ApprovalOutcome(
                kind=ApprovalOutcomeKind.TIMEOUT, reason_code="CANCELLED"
            )
        raise AdapterError(f"Unrecognized Orkes task status: {status!r}")

    def cancel(self, handle: ApprovalHandle, reason: str = "CANCELLED") -> None:
        self._require_handle(handle)
        try:
            self._transport.terminate_human_task(handle.external_id, reason=reason)
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: wraps arbitrary transport errors into AdapterError so callers handle a single exception type
            raise AdapterError(f"Orkes terminate_human_task failed: {exc}") from exc

    def _require_handle(self, handle: ApprovalHandle) -> None:
        if handle.adapter_kind != self.kind:
            raise ValueError(
                f"handle.adapter_kind {handle.adapter_kind!r} != {self.kind!r}"
            )
        if not handle.external_id:
            raise ValueError("handle.external_id is empty")


def _read(obj: Any, key: str) -> str | None:
    if not isinstance(obj, Mapping):
        return None
    val = obj.get(key)
    return str(val) if val is not None else None


__all__ = [
    "DECISION_APPROVE",
    "DECISION_DENY",
    "OrkesApprovalAdapter",
    "OrkesTransport",
    "TASK_CANCELED",
    "TASK_COMPLETED",
    "TASK_FAILED",
    "TASK_IN_PROGRESS",
    "TASK_SCHEDULED",
    "TASK_TERMINATED",
    "TASK_TIMED_OUT",
]
