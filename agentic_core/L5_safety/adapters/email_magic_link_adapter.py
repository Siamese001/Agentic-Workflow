"""Stateless email magic-link implementation of ``HumanApprovalAdapter``.

Sends a signed approval URL to the resolved approver pool. When the human
clicks, the backend HTTP handler validates the HMAC signature and records
the outcome in ``MagicLinkStore``. The adapter then reads that outcome via
``poll``.

Signatures use HMAC-SHA256 over ``{ledger_id}|{decision}`` with a per-tenant
secret supplied at construction time. Signature binds the decision to the
ledger entry, preventing replay across different escalations.

Two injected collaborators:

- ``EmailTransport``: ``send(to, subject, body) -> message_id``
- ``MagicLinkStore``:
    - ``record_pending(ledger_id)``
    - ``get(ledger_id) -> outcome | None``
    - ``resolve(ledger_id, outcome)``         (test-only helper on the fake)
    - ``cancel(ledger_id)``
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Mapping, Protocol

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


class EmailTransport(Protocol):
    def send(self, to: str, subject: str, body: str) -> str:
        ...


@dataclass(frozen=True)
class StoredOutcome:
    kind: ApprovalOutcomeKind
    approver_id: str | None = None
    reason_code: str | None = None
    rationale: str | None = None


class MagicLinkStore(Protocol):
    def record_pending(self, ledger_id: str) -> None:
        ...

    def get(self, ledger_id: str) -> StoredOutcome | None:
        ...

    def cancel(self, ledger_id: str) -> None:
        ...


class EmailMagicLinkAdapter(HumanApprovalAdapter):
    """Email magic-link approval adapter."""

    kind = "email_magic_link"

    def __init__(
        self,
        *,
        base_url: str,
        signing_secret: bytes,
        email: EmailTransport,
        store: MagicLinkStore,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required")
        if not signing_secret:
            raise ValueError("signing_secret is required")
        self._base_url = base_url.rstrip("/")
        self._secret = signing_secret
        self._email = email
        self._store = store

    # -- contract --------------------------------------------------------

    def enqueue(self, entry: LedgerEntry) -> ApprovalHandle:
        approve_url = self._build_url(entry.ledger_id, "approve")
        deny_url = self._build_url(entry.ledger_id, "deny")
        body = (
            f"HITL approval required ({entry.hitl_class.value}).\n\n"
            f"Run:   {entry.run_id}\n"
            f"Trace: {entry.trace_id}\n"
            f"Timeout: {entry.timeout_s}s\n\n"
            f"Approve: {approve_url}\n"
            f"Deny:    {deny_url}\n"
        )
        try:
            self._store.record_pending(entry.ledger_id)
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: wraps arbitrary transport errors into AdapterError so callers handle a single exception type
            raise AdapterError(f"MagicLinkStore.record_pending failed: {exc}") from exc

        try:
            message_id = self._email.send(
                to=entry.approver_pool,
                subject=f"[HITL {entry.hitl_class.value}] {entry.ledger_id}",
                body=body,
            )
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: wraps arbitrary transport errors into AdapterError so callers handle a single exception type
            raise AdapterError(f"Email send failed: {exc}") from exc

        if not message_id:
            raise AdapterError("Email transport returned no message_id")
        return ApprovalHandle(
            adapter_kind=self.kind,
            external_id=str(message_id),
            ledger_id=entry.ledger_id,
        )

    def poll(self, handle: ApprovalHandle) -> ApprovalOutcome | None:
        self._require_handle(handle)
        try:
            outcome = self._store.get(handle.ledger_id)
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: wraps arbitrary transport errors into AdapterError so callers handle a single exception type
            raise AdapterError(f"MagicLinkStore.get failed: {exc}") from exc
        if outcome is None:
            return None
        return ApprovalOutcome(
            kind=outcome.kind,
            approver_id=outcome.approver_id,
            reason_code=outcome.reason_code,
            rationale=outcome.rationale,
        )

    def cancel(self, handle: ApprovalHandle, reason: str = "CANCELLED") -> None:
        _ = reason
        self._require_handle(handle)
        try:
            self._store.cancel(handle.ledger_id)
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: wraps arbitrary transport errors into AdapterError so callers handle a single exception type
            raise AdapterError(f"MagicLinkStore.cancel failed: {exc}") from exc

    # -- signing ---------------------------------------------------------

    def sign(self, ledger_id: str, decision: str) -> str:
        """Compute the HMAC-SHA256 hex digest for (ledger_id, decision)."""
        msg = f"{ledger_id}|{decision}".encode("utf-8")
        return hmac.new(self._secret, msg, hashlib.sha256).hexdigest()

    def verify(self, ledger_id: str, decision: str, signature: str) -> bool:
        """Constant-time verification of a click-through signature."""
        expected = self.sign(ledger_id, decision)
        return hmac.compare_digest(expected, signature)

    def _build_url(self, ledger_id: str, decision: str) -> str:
        sig = self.sign(ledger_id, decision)
        return (
            f"{self._base_url}/hitl/resolve"
            f"?ledger_id={ledger_id}&decision={decision}&sig={sig}"
        )

    def _require_handle(self, handle: ApprovalHandle) -> None:
        if handle.adapter_kind != self.kind:
            raise ValueError(
                f"handle.adapter_kind {handle.adapter_kind!r} != {self.kind!r}"
            )
        if not handle.external_id:
            raise ValueError("handle.external_id is empty")


__all__ = [
    "EmailMagicLinkAdapter",
    "EmailTransport",
    "MagicLinkStore",
    "StoredOutcome",
]
