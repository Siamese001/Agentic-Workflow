"""U2 HTTP / API entry adapter.

Normalizes an HTTP request (method + headers + JSON body) into the canonical
raw_envelope shape and delegates to :class:`IngressEnvelopeCheck`. Supports
the full set of rejection codes via :func:`render_http` which returns the
standard ``(status, headers, body)`` triple.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

from agentic_core.L5_safety.enforcement.ingress import (
    ClarificationRequired,
    IngressEnvelopeCheck,
    IngressRejected,
    StampedRequest,
)
from agentic_core.L5_safety.enforcement.rejection_response import (
    RejectionResponse,
    render_clarification_http,
    render_http,
)


class HttpIngressAdapter:
    """Adapter for U2 HTTP / service-to-service entries.

    ``handle`` returns one of:
      * :class:`StampedRequest` — forward to L1,
      * ``(status, headers, body)`` triple for clarification or rejection.
    """

    DEFAULT_SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        gate: IngressEnvelopeCheck,
        *,
        schema_version_header: str = "X-Schema-Version",
        identity_header: str = "X-Caller-Identity",
        request_id_header: str = "X-Request-Id",
        tenant_header: str = "X-Tenant-Id",
        auth_header: str = "Authorization",
    ) -> None:
        self._gate = gate
        self._schema_hdr = schema_version_header
        self._identity_hdr = identity_header
        self._req_hdr = request_id_header
        self._tenant_hdr = tenant_header
        self._auth_hdr = auth_header

    def handle(
        self,
        *,
        headers: dict[str, str],
        body: Any,
    ) -> StampedRequest | tuple[int, dict[str, str], str]:
        envelope = self._to_envelope(headers, body)
        try:
            result = self._gate.check(envelope)
        except IngressRejected as exc:
            return render_http(RejectionResponse.from_exception(exc))

        if isinstance(result, ClarificationRequired):
            return render_clarification_http(result)
        return result

    def _to_envelope(self, headers: dict[str, str], body: Any) -> dict[str, Any]:
        # Case-insensitive header lookup without depending on a specific framework.
        lowered = {k.lower(): v for k, v in headers.items()}
        caller = lowered.get(self._identity_hdr.lower()) or "http-anon"
        schema = lowered.get(self._schema_hdr.lower()) or self.DEFAULT_SCHEMA_VERSION
        request_id = lowered.get(self._req_hdr.lower()) or str(uuid.uuid4())
        tenant = lowered.get(self._tenant_hdr.lower()) or "default"

        envelope: dict[str, Any] = {
            "schema_version": schema,
            "caller_identity": caller,
            "request_id": request_id,
            "tenant_id": tenant,
            "request_payload": body,
            "received_at_utc": time.time(),
            "ingress_source_class": "service",
        }
        modality_hdr = lowered.get("x-modality")
        if modality_hdr:
            envelope["modality"] = modality_hdr
        if isinstance(body, dict) and isinstance(body.get("attachments"), (list, tuple)):
            envelope["attachments"] = body["attachments"]
        auth = lowered.get(self._auth_hdr.lower())
        if auth:
            envelope["authorization"] = auth
            # Support SharedSecretIdentityVerifier bearer convention.
            if isinstance(auth, str) and auth.lower().startswith("bearer "):
                envelope["auth_token"] = auth.split(" ", 1)[1].strip()
                if "auth_timestamp" not in envelope:
                    ts_hdr = lowered.get("x-auth-timestamp")
                    if ts_hdr is not None:
                        try:
                            envelope["auth_timestamp"] = int(ts_hdr)
                        except (TypeError, ValueError):
                            envelope["auth_timestamp"] = 0
        return envelope


__all__ = ["HttpIngressAdapter"]
