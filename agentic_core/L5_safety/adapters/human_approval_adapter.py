"""Abstract base for runtime HITL human-approval adapters.

Per ADR-023 §3.3, every approval surface (Notion, Slack, Orkes HUMAN task,
email magic link, Jira, PagerDuty) implements this contract. The exit
controller is adapter-agnostic — it calls ``enqueue`` on escalation and
later receives outcomes via ``poll`` or an out-of-band callback that
invokes ``controller.record_approval``/``record_denial``/``record_timeout``.

Adapter contract:

1. ``enqueue(ledger_entry)``      → returns an ``ApprovalHandle`` (opaque).
2. ``poll(handle)``                → returns ``ApprovalOutcome`` or ``None`` if still pending.
3. ``cancel(handle, reason)``      → best-effort; idempotent.

Outcome semantics must match the four lifecycle states recorded by the
runtime HITL ledger (``APPROVED``, ``DENIED``, ``TIMEOUT``, plus the
``PENDING`` state represented by ``poll`` returning ``None``).

Contract tests: every concrete adapter must pass
``tests/agentic_core/L5_safety/adapters/contract.py`` (hermetic — no network).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerEntry,
)


class AdapterError(RuntimeError):
    """Raised when an adapter cannot fulfill a contract call.

    Callers treat this as transient — the caller decides retry vs fail-closed.
    """


class ApprovalOutcomeKind(str, Enum):
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class ApprovalHandle:
    """Opaque handle returned by ``enqueue``.

    ``adapter_kind`` identifies the adapter class (``"notion"``, ``"slack"``, …).
    ``external_id`` is the adapter-assigned record identifier (Notion page id,
    Slack message ts, etc.). ``ledger_id`` is the round-trip back into the
    runtime HITL ledger.
    """

    adapter_kind: str
    external_id: str
    ledger_id: str
    metadata: Mapping[str, Any] = ()  # type: ignore[assignment]


@dataclass(frozen=True)
class ApprovalOutcome:
    """Resolution payload returned by ``poll`` once the human has acted."""

    kind: ApprovalOutcomeKind
    approver_id: str | None = None
    reason_code: str | None = None
    rationale: str | None = None


class HumanApprovalAdapter(ABC):
    """Abstract base class for all human-approval adapters."""

    #: Machine-readable adapter kind (``"notion"``, ``"slack"``, …).
    kind: str = "abstract"

    @abstractmethod
    def enqueue(self, entry: LedgerEntry) -> ApprovalHandle:
        """Create the approval request on the external surface.

        Implementations MUST NOT block on human action. Return as soon as the
        external record is created.

        Raises:
            AdapterError: on transport failure. Controller may retry or
                route to a fallback adapter per policy.
        """

    @abstractmethod
    def poll(self, handle: ApprovalHandle) -> ApprovalOutcome | None:
        """Return the current outcome, or ``None`` if still pending."""

    @abstractmethod
    def cancel(self, handle: ApprovalHandle, reason: str = "CANCELLED") -> None:
        """Best-effort cancellation. Idempotent — double-cancel is a no-op."""


__all__ = [
    "AdapterError",
    "ApprovalHandle",
    "ApprovalOutcome",
    "ApprovalOutcomeKind",
    "HumanApprovalAdapter",
]
