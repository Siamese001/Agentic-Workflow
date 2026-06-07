"""Terminal U0 rejection for apps_rg — sealed RejectedRequestNotice (REQ-U0-REJECTION-TERMINAL-001)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


class AppsRgIngressReasonCode(str, Enum):
    """apps_rg-local U0 rejection reason codes.

    Migration-only protocol until a canonical spine rejection contract exists.
    """

    UNSUPPORTED_TRANSPORT = "UNSUPPORTED_TRANSPORT"
    EMPTY_PAYLOAD = "EMPTY_PAYLOAD"
    MALFORMED_ENVELOPE = "MALFORMED_ENVELOPE"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    TENANT_MISMATCH = "TENANT_MISMATCH"
    PRINCIPAL_BLOCKED = "PRINCIPAL_BLOCKED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    BURST_LIMIT = "BURST_LIMIT"
    DUPLICATE_REQUEST = "DUPLICATE_REQUEST"
    WEBHOOK_REPLAY = "WEBHOOK_REPLAY"
    UNSUPPORTED_MODALITY = "UNSUPPORTED_MODALITY"
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
    FIELD_TYPE_MISMATCH = "FIELD_TYPE_MISMATCH"
    NORMALIZATION_UNSAFE = "NORMALIZATION_UNSAFE"
    ATTACHMENT_MANIFEST_BAD = "ATTACHMENT_MANIFEST_BAD"
    TRACE_BINDING_FAILED = "TRACE_BINDING_FAILED"
    INTERNAL_INGRESS_ERROR = "INTERNAL_INGRESS_ERROR"


class AppsRgSourceClass(str, Enum):
    """apps_rg-local U0 source class for terminal rejection notices."""

    USER = "user"
    SERVICE = "service"
    BATCH = "batch"
    WEBHOOK = "webhook"
    ALERT = "alert"


@dataclass(frozen=True)
class AppsRgRejectedRequestNotice:
    """apps_rg-local terminal rejection notice.

    Non-canonical migration protocol; do not promote to spine truth by alias.
    """

    request_id: str
    trace_root: str
    source_class: AppsRgSourceClass | None
    received_at_iso: str
    rejection_stage: str
    rejection_reason: AppsRgIngressReasonCode
    reason_codes: tuple[AppsRgIngressReasonCode, ...]
    retry_after_seconds: int | None = None
    machine_readable_detail: Mapping[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class AppsRgU0RejectedError(Exception):
    """Raised when apps_rg U0 validation fails; carries a terminal rejection notice."""

    notice: AppsRgRejectedRequestNotice
    message: str = ""

    def __str__(self) -> str:
        return self.message or self.notice.rejection_reason.value


def build_u0_rejected_notice(
    *,
    request_id: str,
    trace_root: str,
    rejection_reason: AppsRgIngressReasonCode,
    rejection_stage: str = "E4",
    machine_readable_detail: Mapping[str, Any] | None = None,
) -> AppsRgRejectedRequestNotice:
    """Build a sealed RejectedRequestNotice for apps_rg U0 failures."""

    return AppsRgRejectedRequestNotice(
        request_id=request_id or "unknown",
        trace_root=trace_root or request_id or "unknown",
        source_class=AppsRgSourceClass.BATCH,
        received_at_iso=datetime.now(timezone.utc).isoformat(),
        rejection_stage=rejection_stage,
        rejection_reason=rejection_reason,
        reason_codes=(rejection_reason,),
        retry_after_seconds=None,
        machine_readable_detail=dict(machine_readable_detail or {}),
    )


__all__ = [
    "AppsRgIngressReasonCode",
    "AppsRgRejectedRequestNotice",
    "AppsRgSourceClass",
    "AppsRgU0RejectedError",
    "build_u0_rejected_notice",
]
