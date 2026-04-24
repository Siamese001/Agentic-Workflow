"""Rejection response contract + per-source renderers.

Closes gap G-15: the ingress gate raised :class:`IngressRejected`, but each
entry adapter had to translate it ad-hoc to its transport. This module
provides a :class:`RejectionResponse` dataclass and four shipped renderers —
HTTP, webhook, chat, batch — so every U0 source speaks the same rejection
shape.

Layer authority: L5 (policy plane) — pure transform, no durable writes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L5_safety.enforcement.ingress_envelope_check import (
    ClarificationRequired,
    IngressRejected,
    RejectionSlip,
)


@dataclass(frozen=True)
class RejectionResponse:
    """Transport-agnostic rejection response.

    Fields are the minimum set every source renderer must carry back to the
    caller. ``http_status`` maps each reason code to an appropriate HTTP
    status for the HTTP renderer; other renderers ignore it.
    """

    reason_code: str
    message: str
    request_id: str
    trace_root: str
    http_status: int = 400
    retryable: bool = False
    matched_fragments: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_slip(cls, slip: RejectionSlip) -> "RejectionResponse":
        status, retryable = _status_for(slip.reason_code.value)
        return cls(
            reason_code=slip.reason_code.value,
            message=slip.message,
            request_id=slip.request_id,
            trace_root=slip.trace_root,
            http_status=status,
            retryable=retryable,
            matched_fragments=tuple(slip.matched_fragments),
        )

    @classmethod
    def from_exception(cls, exc: IngressRejected) -> "RejectionResponse":
        return cls.from_slip(exc.slip)

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": "REJECTED",
            "reason_code": self.reason_code,
            "message": self.message,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "retryable": self.retryable,
            "matched_fragments": list(self.matched_fragments),
        }


_STATUS_TABLE: dict[str, tuple[int, bool]] = {
    "E1_MALFORMED_ENVELOPE": (400, False),
    "E2_SCHEMA_INVALID": (400, False),
    "E2_PAYLOAD_OVERSIZED": (413, False),
    "E2_PAYLOAD_TOO_DEEP": (400, False),
    "E3_IDENTITY_MISSING": (401, False),
    "E3_IDENTITY_UNTRUSTED": (401, False),
    "E4_QUOTA_EXCEEDED": (429, True),
    "E4_RATE_LIMITED": (429, True),
    "E6_INJECTION_DETECTED": (400, False),
    "E6_JAILBREAK_DETECTED": (400, False),
    "E6_PII_DETECTED": (400, False),
    "E7_REPLAY_DUPLICATE": (409, False),
}


def _status_for(code: str) -> tuple[int, bool]:
    return _STATUS_TABLE.get(code, (400, False))


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------


def render_http(resp: RejectionResponse) -> tuple[int, dict[str, str], str]:
    """Return ``(status_code, headers, body)`` for an HTTP adapter."""

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Request-Id": resp.request_id,
        "X-Trace-Root": resp.trace_root,
    }
    if resp.retryable:
        headers["Retry-After"] = "1"
    body = json.dumps(resp.to_dict(), ensure_ascii=False)
    return resp.http_status, headers, body


def render_webhook(resp: RejectionResponse) -> dict[str, Any]:
    """Return a dict body suitable for webhook responders (202 ACK + deadletter)."""

    return {
        "ack": True,
        "deadletter": True,
        "rejection": resp.to_dict(),
    }


def render_chat(resp: RejectionResponse) -> str:
    """Render a compact chat-bubble string for U1 chat adapters."""

    return (
        f"[request rejected: {resp.reason_code}] {resp.message} "
        f"(request_id={resp.request_id})"
    )


def render_batch(resp: RejectionResponse) -> dict[str, Any]:
    """Render a per-row failure record for U3 batch adapters."""

    return {
        "status": "rejected",
        "request_id": resp.request_id,
        "trace_root": resp.trace_root,
        "reason_code": resp.reason_code,
        "message": resp.message,
    }


def render_clarification_http(
    clarify: ClarificationRequired,
) -> tuple[int, dict[str, str], str]:
    """Render a :class:`ClarificationRequired` as HTTP 422."""

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Request-Id": clarify.request_id,
        "X-Trace-Root": clarify.trace_root,
    }
    body = json.dumps(clarify.to_dict(), ensure_ascii=False)
    return 422, headers, body


__all__ = [
    "RejectionResponse",
    "render_batch",
    "render_chat",
    "render_clarification_http",
    "render_http",
    "render_webhook",
]
