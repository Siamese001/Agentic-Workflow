"""Slack implementation of ``HumanApprovalAdapter``.

Approval semantics: an approval message is posted to a designated Slack
channel with Block Kit buttons (``APPROVE`` / ``DENY``). The Slack
interactive endpoint is wired separately at runtime composition time; for
this adapter the signal is read out of a ``status`` attribute on the message
record that the transport maintains. Test transports set the attribute
directly; production transports poll the receiving HTTP handler's state.

No ``slack_sdk`` dependency is introduced — the ``SlackTransport`` Protocol
abstracts the three operations we need.
"""

from __future__ import annotations

import json
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


STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_DENIED = "denied"
STATUS_TIMEOUT = "timeout"
STATUS_CANCELLED = "cancelled"


_OUTCOME_BY_STATUS: Mapping[str, ApprovalOutcomeKind] = {
    STATUS_APPROVED: ApprovalOutcomeKind.APPROVED,
    STATUS_DENIED: ApprovalOutcomeKind.DENIED,
    STATUS_TIMEOUT: ApprovalOutcomeKind.TIMEOUT,
}


class SlackTransport(Protocol):
    """Minimal Slack surface this adapter depends on."""

    def post_message(self, channel: str, text: str, blocks: list[Mapping[str, Any]]) -> Mapping[str, Any]:
        ...

    def get_message(self, channel: str, ts: str) -> Mapping[str, Any]:
        ...

    def delete_message(self, channel: str, ts: str) -> Mapping[str, Any]:
        ...


def build_approval_blocks(entry: LedgerEntry) -> list[Mapping[str, Any]]:
    """Render a Block Kit payload for the approval prompt.

    SSOT for the Slack message shape; the interactive endpoint binds on
    the ``action_id`` literals ``hitl_approve`` / ``hitl_deny`` and the
    ``ledger_id`` block value.
    """
    envelope_json = json.dumps(dict(entry.envelope), sort_keys=True, indent=2)
    return [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"HITL Approval: {entry.hitl_class.value}"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Run*\n`{entry.run_id}`"},
                {"type": "mrkdwn", "text": f"*Trace*\n`{entry.trace_id}`"},
                {"type": "mrkdwn", "text": f"*Class*\n{entry.hitl_class.value}"},
                {"type": "mrkdwn", "text": f"*Timeout*\n{entry.timeout_s}s"},
            ],
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"```{envelope_json}```"},
        },
        {
            "type": "actions",
            "block_id": entry.ledger_id,
            "elements": [
                {
                    "type": "button",
                    "action_id": "hitl_approve",
                    "text": {"type": "plain_text", "text": "Approve"},
                    "style": "primary",
                    "value": entry.ledger_id,
                },
                {
                    "type": "button",
                    "action_id": "hitl_deny",
                    "text": {"type": "plain_text", "text": "Deny"},
                    "style": "danger",
                    "value": entry.ledger_id,
                },
            ],
        },
    ]


class SlackApprovalAdapter(HumanApprovalAdapter):
    """Slack-backed approval adapter."""

    kind = "slack"

    def __init__(self, *, channel: str, transport: SlackTransport) -> None:
        if not channel:
            raise ValueError("channel is required")
        self._channel = channel
        self._transport = transport

    def enqueue(self, entry: LedgerEntry) -> ApprovalHandle:
        try:
            resp = self._transport.post_message(
                self._channel,
                text=f"HITL approval required: {entry.hitl_class.value} ({entry.ledger_id})",
                blocks=build_approval_blocks(entry),
            )
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: wraps arbitrary transport errors into AdapterError so callers handle a single exception type
            raise AdapterError(f"Slack post_message failed: {exc}") from exc

        ts = resp.get("ts") if isinstance(resp, Mapping) else None
        if not ts:
            raise AdapterError("Slack post_message returned no ts")
        return ApprovalHandle(
            adapter_kind=self.kind,
            external_id=str(ts),
            ledger_id=entry.ledger_id,
        )

    def poll(self, handle: ApprovalHandle) -> ApprovalOutcome | None:
        self._require_handle(handle)
        try:
            msg = self._transport.get_message(self._channel, handle.external_id)
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: wraps arbitrary transport errors into AdapterError so callers handle a single exception type
            raise AdapterError(f"Slack get_message failed: {exc}") from exc

        status = _read_status(msg)
        if status == STATUS_PENDING:
            return None
        if status == STATUS_CANCELLED:
            return ApprovalOutcome(
                kind=ApprovalOutcomeKind.TIMEOUT, reason_code=STATUS_CANCELLED.upper()
            )
        kind = _OUTCOME_BY_STATUS.get(status)
        if kind is None:
            raise AdapterError(f"Unrecognized Slack status: {status!r}")
        meta = msg.get("metadata") if isinstance(msg, Mapping) else None
        meta = meta if isinstance(meta, Mapping) else {}
        return ApprovalOutcome(
            kind=kind,
            approver_id=_as_str(meta.get("approver_id")),
            reason_code=_as_str(meta.get("reason_code")),
            rationale=_as_str(meta.get("rationale")),
        )

    def cancel(self, handle: ApprovalHandle, reason: str = "CANCELLED") -> None:
        _ = reason
        self._require_handle(handle)
        try:
            self._transport.delete_message(self._channel, handle.external_id)
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: wraps arbitrary transport errors into AdapterError so callers handle a single exception type
            raise AdapterError(f"Slack delete_message failed: {exc}") from exc

    def _require_handle(self, handle: ApprovalHandle) -> None:
        if handle.adapter_kind != self.kind:
            raise ValueError(
                f"handle.adapter_kind {handle.adapter_kind!r} != {self.kind!r}"
            )
        if not handle.external_id:
            raise ValueError("handle.external_id is empty")


def _read_status(msg: Mapping[str, Any]) -> str:
    if not isinstance(msg, Mapping):
        return STATUS_PENDING
    status = msg.get("status")
    return str(status) if isinstance(status, str) else STATUS_PENDING


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


__all__ = [
    "STATUS_APPROVED",
    "STATUS_CANCELLED",
    "STATUS_DENIED",
    "STATUS_PENDING",
    "STATUS_TIMEOUT",
    "SlackApprovalAdapter",
    "SlackTransport",
    "build_approval_blocks",
]
