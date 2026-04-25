"""
Ingress reason codes (REJECTION / REFILL REASONS table from spec).

Codes are machine-readable. Every reject/throttle/duplicate verdict MUST
attach at least one IngressReasonCode so downstream callers can react
deterministically and so observability can bucket reject_rate by reason.
"""

from __future__ import annotations

from enum import Enum


class IngressReasonCode(str, Enum):
    """All 18 reason codes defined in the Request Intake spec."""

    # E1 transport / shell
    UNSUPPORTED_TRANSPORT = "UNSUPPORTED_TRANSPORT"
    EMPTY_PAYLOAD = "EMPTY_PAYLOAD"
    MALFORMED_ENVELOPE = "MALFORMED_ENVELOPE"

    # E2 identity
    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_EXPIRED = "AUTH_EXPIRED"
    TENANT_MISMATCH = "TENANT_MISMATCH"
    PRINCIPAL_BLOCKED = "PRINCIPAL_BLOCKED"

    # E3 quota / dedupe / abuse
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    BURST_LIMIT = "BURST_LIMIT"
    DUPLICATE_REQUEST = "DUPLICATE_REQUEST"
    WEBHOOK_REPLAY = "WEBHOOK_REPLAY"

    # E4 schema
    UNSUPPORTED_MODALITY = "UNSUPPORTED_MODALITY"
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
    FIELD_TYPE_MISMATCH = "FIELD_TYPE_MISMATCH"

    # E5 normalization
    NORMALIZATION_UNSAFE = "NORMALIZATION_UNSAFE"
    ATTACHMENT_MANIFEST_BAD = "ATTACHMENT_MANIFEST_BAD"

    # E6 stamping / generic
    TRACE_BINDING_FAILED = "TRACE_BINDING_FAILED"
    INTERNAL_INGRESS_ERROR = "INTERNAL_INGRESS_ERROR"


# Reason codes that should be retried by the caller (vs. permanent reject).
RETRIABLE_REASON_CODES = frozenset(
    {
        IngressReasonCode.QUOTA_EXCEEDED,
        IngressReasonCode.BURST_LIMIT,
        IngressReasonCode.INTERNAL_INGRESS_ERROR,
    }
)


__all__ = ["IngressReasonCode", "RETRIABLE_REASON_CODES"]
