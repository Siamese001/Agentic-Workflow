"""U1 chat / UI session entry adapter.

Normalizes a chat-style payload into the canonical raw_envelope shape and
delegates to :class:`IngressEnvelopeCheck`. This is the single entry point
for U1 sources; bypassing it is a constitutional violation.
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
    render_chat,
)


class ChatIngressAdapter:
    """Adapter for U1 chat / UI session entries.

    ``handle`` accepts a user's chat-turn dict and returns the stamped request,
    a clarification, or a rendered rejection string.
    """

    SCHEMA_VERSION = "1.0"

    def __init__(self, gate: IngressEnvelopeCheck) -> None:
        self._gate = gate

    def handle(self, turn: dict[str, Any]) -> StampedRequest | ClarificationRequired | str:
        envelope = self._to_envelope(turn)
        try:
            return self._gate.check(envelope)
        except IngressRejected as exc:
            return render_chat(RejectionResponse.from_exception(exc))

    @classmethod
    def _to_envelope(cls, turn: dict[str, Any]) -> dict[str, Any]:
        caller = str(turn.get("caller_identity") or turn.get("user_id") or "chat-anon")
        message = turn.get("message") or turn.get("text") or ""
        payload: dict[str, Any] = {"intent": message}
        if "attachments" in turn:
            payload["attachments"] = turn["attachments"]
        envelope: dict[str, Any] = {
            "schema_version": cls.SCHEMA_VERSION,
            "caller_identity": caller,
            "request_payload": payload,
            "session_id": turn.get("session_id") or str(uuid.uuid4()),
            "request_id": turn.get("request_id") or str(uuid.uuid4()),
            "tenant_id": turn.get("tenant_id") or "default",
            "received_at_utc": time.time(),
            "ingress_source_class": "user",
        }
        if "attachments" in turn:
            envelope["attachments"] = turn["attachments"]
        if "modality" in turn:
            envelope["modality"] = turn["modality"]
        return envelope


__all__ = ["ChatIngressAdapter"]
