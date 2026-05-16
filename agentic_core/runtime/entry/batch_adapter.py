"""U3 scheduled / batch entry adapter.

Processes a batch (list) of per-row envelopes and returns a paired list of
outcomes — one per row — so a single malformed row does not stop the run.
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
    render_batch,
)


class BatchIngressAdapter:
    """Adapter for U3 scheduled / batch drops.

    Each ``row`` in the input list is normalized independently and gated.
    Output is a list of the same length. Per-row outcome is one of:
      * :class:`StampedRequest`
      * :class:`ClarificationRequired`
      * a dict produced by :func:`render_batch` (rejection)
    """

    SCHEMA_VERSION = "1.0"

    def __init__(self, gate: IngressEnvelopeCheck) -> None:
        self._gate = gate

    def handle_rows(
        self,
        rows: list[dict[str, Any]],
        *,
        batch_id: str | None = None,
    ) -> list[StampedRequest | ClarificationRequired | dict[str, Any]]:
        batch_id = batch_id or str(uuid.uuid4())
        out: list[StampedRequest | ClarificationRequired | dict[str, Any]] = []
        for idx, row in enumerate(rows):
            envelope = self._to_envelope(row, batch_id, idx)
            try:
                out.append(self._gate.check(envelope))
            except IngressRejected as exc:
                out.append(render_batch(RejectionResponse.from_exception(exc)))
        return out

    @classmethod
    def _to_envelope(cls, row: dict[str, Any], batch_id: str, idx: int) -> dict[str, Any]:
        caller = str(row.get("caller_identity") or row.get("submitter") or f"batch:{batch_id}")
        envelope: dict[str, Any] = {
            "schema_version": row.get("schema_version") or cls.SCHEMA_VERSION,
            "caller_identity": caller,
            "request_id": row.get("request_id") or f"{batch_id}:{idx}",
            "session_id": row.get("session_id") or batch_id,
            "tenant_id": row.get("tenant_id") or "default",
            "request_payload": row.get("request_payload") or row.get("payload"),
            "received_at_utc": time.time(),
            "batch_index": idx,
            "batch_id": batch_id,
            "ingress_source_class": "batch",
        }
        if "attachments" in row:
            envelope["attachments"] = row["attachments"]
        if "modality" in row:
            envelope["modality"] = row["modality"]
        return envelope


__all__ = ["BatchIngressAdapter"]
