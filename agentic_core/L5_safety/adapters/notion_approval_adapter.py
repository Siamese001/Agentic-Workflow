"""Notion implementation of ``HumanApprovalAdapter``.

Per ADR-023 G2, runtime HITL uses a **separate** Notion DB (not the
developer-loop HITL Decision Ledger). The DB ID is resolved from
``config/notion_databases.yaml`` via the ``runtime_hitl_decisions`` key.

Boundary design: this adapter depends only on a ``NotionTransport`` protocol
(a callable with ``create_page``, ``retrieve_page``, ``archive_page`` methods).
Callers inject either:

- A thin wrapper around the ``mcp6_notion`` MCP tools (runtime composition), or
- A fake transport for tests (see ``tests/.../adapters/test_notion_adapter.py``).

No direct HTTP library or Notion SDK dependency is introduced here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
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


# Notion page property status values — SSOT for the runtime HITL DB.
STATUS_PENDING = "PENDING"
STATUS_APPROVED = "APPROVED"
STATUS_DENIED = "DENIED"
STATUS_TIMEOUT = "TIMEOUT"
STATUS_CANCELLED = "CANCELLED"

_OUTCOME_BY_STATUS: Mapping[str, ApprovalOutcomeKind] = {
    STATUS_APPROVED: ApprovalOutcomeKind.APPROVED,
    STATUS_DENIED: ApprovalOutcomeKind.DENIED,
    STATUS_TIMEOUT: ApprovalOutcomeKind.TIMEOUT,
}


class NotionTransport(Protocol):
    """Minimal Notion surface the adapter depends on.

    Implementations must be side-effect-honest: ``create_page`` must either
    return a page record with ``id`` or raise.
    """

    def create_page(self, database_id: str, properties: Mapping[str, Any]) -> Mapping[str, Any]:
        ...

    def retrieve_page(self, page_id: str) -> Mapping[str, Any]:
        ...

    def archive_page(self, page_id: str) -> Mapping[str, Any]:
        ...


@dataclass(frozen=True)
class NotionProperties:
    """Shape of the Notion page properties this adapter writes."""

    ledger_id: str
    run_id: str
    trace_id: str
    hitl_class: str
    approver_pool: str
    timeout_s: int
    status: str
    envelope_json: str
    policy_snapshot: str

    def to_notion_payload(self) -> dict[str, Any]:
        """Render as Notion page-property payload.

        Uses simple rich_text / number / select shapes — the Notion DB schema
        deployed in the workspace MUST match these names and types.
        """
        return {
            "Ledger ID": {"title": [{"text": {"content": self.ledger_id}}]},
            "Run ID": {"rich_text": [{"text": {"content": self.run_id}}]},
            "Trace ID": {"rich_text": [{"text": {"content": self.trace_id}}]},
            "Class": {"select": {"name": self.hitl_class}},
            "Approver Pool": {"select": {"name": self.approver_pool}},
            "Timeout (s)": {"number": self.timeout_s},
            "Status": {"select": {"name": self.status}},
            "Policy Snapshot": {
                "rich_text": [{"text": {"content": self.policy_snapshot}}]
            },
            "Envelope": {"rich_text": [{"text": {"content": self.envelope_json}}]},
        }


class NotionApprovalAdapter(HumanApprovalAdapter):
    """Notion-backed approval adapter.

    Approval semantics: a human edits the ``Status`` select to one of
    ``APPROVED`` / ``DENIED`` / ``TIMEOUT``. ``Approver`` / ``Reason`` /
    ``Rationale`` are optional rich_text columns the human may fill.
    """

    kind = "notion"

    def __init__(self, *, database_id: str, transport: NotionTransport) -> None:
        if not database_id:
            raise ValueError("database_id is required")
        self._database_id = database_id
        self._transport = transport

    # -- contract --------------------------------------------------------

    def enqueue(self, entry: LedgerEntry) -> ApprovalHandle:
        props = NotionProperties(
            ledger_id=entry.ledger_id,
            run_id=entry.run_id,
            trace_id=entry.trace_id,
            hitl_class=entry.hitl_class.value,
            approver_pool=entry.approver_pool,
            timeout_s=entry.timeout_s,
            status=STATUS_PENDING,
            envelope_json=json.dumps(dict(entry.envelope), sort_keys=True),
            policy_snapshot=entry.policy_snapshot,
        )
        try:
            page = self._transport.create_page(self._database_id, props.to_notion_payload())
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: wraps arbitrary transport errors into AdapterError so callers handle a single exception type
            raise AdapterError(f"Notion create_page failed: {exc}") from exc

        page_id = page.get("id") if isinstance(page, Mapping) else None
        if not page_id:
            raise AdapterError("Notion create_page returned no page id")
        return ApprovalHandle(
            adapter_kind=self.kind,
            external_id=str(page_id),
            ledger_id=entry.ledger_id,
        )

    def poll(self, handle: ApprovalHandle) -> ApprovalOutcome | None:
        self._require_handle(handle)
        try:
            page = self._transport.retrieve_page(handle.external_id)
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: wraps arbitrary transport errors into AdapterError so callers handle a single exception type
            raise AdapterError(f"Notion retrieve_page failed: {exc}") from exc

        status = _read_status(page)
        if status == STATUS_PENDING:
            return None
        if status == STATUS_CANCELLED:
            # Cancelled without explicit outcome — treat as TIMEOUT fallback.
            return ApprovalOutcome(
                kind=ApprovalOutcomeKind.TIMEOUT, reason_code=STATUS_CANCELLED
            )
        kind = _OUTCOME_BY_STATUS.get(status)
        if kind is None:
            raise AdapterError(f"Unrecognized Notion Status value: {status!r}")

        return ApprovalOutcome(
            kind=kind,
            approver_id=_read_text(page, "Approver"),
            reason_code=_read_select(page, "Reason"),
            rationale=_read_text(page, "Rationale"),
        )

    def cancel(self, handle: ApprovalHandle, reason: str = "CANCELLED") -> None:
        _ = reason  # adapter archives the page; reason is informational
        self._require_handle(handle)
        try:
            self._transport.archive_page(handle.external_id)
        except AdapterError:
            raise
        except Exception as exc:  # guardian: allow-broad-exception -- adapter boundary: archive errors re-raised as AdapterError; callers treat archive failures as non-fatal
            raise AdapterError(f"Notion archive_page failed: {exc}") from exc

    # -- helpers ---------------------------------------------------------

    def _require_handle(self, handle: ApprovalHandle) -> None:
        if handle.adapter_kind != self.kind:
            raise ValueError(
                f"handle.adapter_kind {handle.adapter_kind!r} != {self.kind!r}"
            )
        if not handle.external_id:
            raise ValueError("handle.external_id is empty")


def _read_status(page: Mapping[str, Any]) -> str:
    return _read_select(page, "Status") or STATUS_PENDING


def _read_select(page: Mapping[str, Any], prop: str) -> str | None:
    props = page.get("properties") if isinstance(page, Mapping) else None
    if not isinstance(props, Mapping):
        return None
    entry = props.get(prop)
    if not isinstance(entry, Mapping):
        return None
    sel = entry.get("select")
    if isinstance(sel, Mapping):
        name = sel.get("name")
        return str(name) if name else None
    return None


def _read_text(page: Mapping[str, Any], prop: str) -> str | None:
    props = page.get("properties") if isinstance(page, Mapping) else None
    if not isinstance(props, Mapping):
        return None
    entry = props.get(prop)
    if not isinstance(entry, Mapping):
        return None
    rich = entry.get("rich_text") or entry.get("title")
    if not isinstance(rich, list) or not rich:
        return None
    first = rich[0]
    if isinstance(first, Mapping):
        text = first.get("text") or {}
        content = text.get("content") if isinstance(text, Mapping) else None
        if content:
            return str(content)
        plain = first.get("plain_text")
        if plain:
            return str(plain)
    return None


__all__ = [
    "NotionApprovalAdapter",
    "NotionProperties",
    "NotionTransport",
    "STATUS_APPROVED",
    "STATUS_CANCELLED",
    "STATUS_DENIED",
    "STATUS_PENDING",
    "STATUS_TIMEOUT",
]
