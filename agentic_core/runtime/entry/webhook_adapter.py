"""U4 webhook / callback entry adapter.

Verifies a signed HMAC over the raw body before delegating to the ingress
gate. HMAC verification is a transport-level check distinct from E3 identity
verification; callers may still configure a separate
:class:`IdentityVerifier` for the caller-identity claim.
"""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from typing import Any

from agentic_core.L5_safety.enforcement.ingress_envelope_check import (
    ClarificationRequired,
    IngressEnvelopeCheck,
    IngressRejected,
    StampedRequest,
)
from agentic_core.L5_safety.enforcement.rejection_response import (
    RejectionResponse,
    render_webhook,
)


class WebhookSignatureError(Exception):
    """Raised when the webhook HMAC signature does not verify."""


class WebhookIngressAdapter:
    """Adapter for U4 webhook / async callback entries.

    The HMAC signature MUST be computed as::

        HMAC_SHA256(shared_secret, f"{timestamp}.{body_bytes}")

    and supplied in the ``X-Webhook-Signature`` header along with
    ``X-Webhook-Timestamp`` (epoch seconds).
    """

    SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        gate: IngressEnvelopeCheck,
        shared_secret: bytes | None = None,
        *,
        clock_skew_seconds: int = 300,
    ) -> None:
        self._gate = gate
        self._secret = bytes(shared_secret) if shared_secret else None
        self._clock_skew = int(clock_skew_seconds)

    def handle(
        self,
        *,
        headers: dict[str, str],
        body_bytes: bytes,
        parsed_body: dict[str, Any],
    ) -> StampedRequest | ClarificationRequired | dict[str, Any]:
        if self._secret is not None:
            self._verify_signature(headers, body_bytes)

        envelope = self._to_envelope(headers, parsed_body)
        try:
            return self._gate.check(envelope)
        except IngressRejected as exc:
            return render_webhook(RejectionResponse.from_exception(exc))

    def _verify_signature(self, headers: dict[str, str], body_bytes: bytes) -> None:
        lowered = {k.lower(): v for k, v in headers.items()}
        sig = lowered.get("x-webhook-signature", "")
        ts = lowered.get("x-webhook-timestamp", "")
        if not sig or not ts:
            raise WebhookSignatureError("Missing webhook signature or timestamp header.")
        try:
            ts_int = int(ts)
        except ValueError as exc:
            raise WebhookSignatureError("Malformed webhook timestamp.") from exc
        if abs(time.time() - ts_int) > self._clock_skew:
            raise WebhookSignatureError("Webhook timestamp outside clock-skew window.")

        assert self._secret is not None  # for type checker
        expected = hmac.new(
            self._secret,
            f"{ts_int}.".encode("utf-8") + body_bytes,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, sig):
            raise WebhookSignatureError("Webhook HMAC signature mismatch.")

    @classmethod
    def _to_envelope(cls, headers: dict[str, str], body: dict[str, Any]) -> dict[str, Any]:
        lowered = {k.lower(): v for k, v in headers.items()}
        caller = str(
            body.get("caller_identity")
            or lowered.get("x-caller-identity")
            or "webhook-anon"
        )
        return {
            "schema_version": body.get("schema_version") or cls.SCHEMA_VERSION,
            "caller_identity": caller,
            "request_id": body.get("request_id") or lowered.get("x-request-id") or str(uuid.uuid4()),
            "session_id": body.get("session_id") or str(uuid.uuid4()),
            "tenant_id": body.get("tenant_id") or "default",
            "request_payload": body.get("request_payload") or body.get("event") or body,
            "received_at_utc": time.time(),
        }


__all__ = ["WebhookIngressAdapter", "WebhookSignatureError"]
