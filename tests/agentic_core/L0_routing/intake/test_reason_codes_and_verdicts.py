"""Coverage of reason codes + verdict enums against spec tables."""

from __future__ import annotations

from agentic_core.L0_routing.intake.reason_codes import (
    RETRIABLE_REASON_CODES,
    IngressReasonCode,
)
from agentic_core.L0_routing.intake.verdicts import (
    AuthVerdict,
    NormalizationVerdict,
    PrincipalType,
    QuotaVerdict,
    SchemaVerdict,
    SourceClass,
)


# Spec line 591-612: REJECTION / REFILL REASONS table — 18 codes.
SPEC_REASON_CODES = {
    "UNSUPPORTED_TRANSPORT",
    "EMPTY_PAYLOAD",
    "MALFORMED_ENVELOPE",
    "AUTH_REQUIRED",
    "AUTH_EXPIRED",
    "TENANT_MISMATCH",
    "PRINCIPAL_BLOCKED",
    "QUOTA_EXCEEDED",
    "BURST_LIMIT",
    "DUPLICATE_REQUEST",
    "WEBHOOK_REPLAY",
    "UNSUPPORTED_MODALITY",
    "PAYLOAD_TOO_LARGE",
    "FIELD_TYPE_MISMATCH",
    "NORMALIZATION_UNSAFE",
    "ATTACHMENT_MANIFEST_BAD",
    "TRACE_BINDING_FAILED",
    "INTERNAL_INGRESS_ERROR",
}


def test_all_18_reason_codes_present() -> None:
    """Every reason code in spec lines 591-612 must be implemented."""
    impl = {code.value for code in IngressReasonCode}
    assert impl == SPEC_REASON_CODES


def test_reason_codes_are_strings() -> None:
    """Codes are str-valued enums for JSON-stable serialization."""
    for code in IngressReasonCode:
        assert isinstance(code.value, str)
        assert code.value == code.value.upper()


def test_retriable_codes_are_subset() -> None:
    assert RETRIABLE_REASON_CODES.issubset(set(IngressReasonCode))
    # Permanent reject codes must NOT be retriable
    assert IngressReasonCode.AUTH_EXPIRED not in RETRIABLE_REASON_CODES
    assert IngressReasonCode.PRINCIPAL_BLOCKED not in RETRIABLE_REASON_CODES
    assert IngressReasonCode.UNSUPPORTED_TRANSPORT not in RETRIABLE_REASON_CODES


def test_source_class_values() -> None:
    """Spec line 464 / 512: source_class = user|service|batch|webhook|alert."""
    assert {sc.value for sc in SourceClass} == {
        "user",
        "service",
        "batch",
        "webhook",
        "alert",
    }


def test_auth_verdict_values() -> None:
    """Spec line 242 / 513."""
    assert {v.value for v in AuthVerdict} == {
        "authenticated",
        "service-bound",
        "anonymous-limited",
        "rejected",
    }


def test_quota_verdict_values() -> None:
    """Spec line 294 / 514."""
    assert {v.value for v in QuotaVerdict} == {
        "allowed",
        "throttled",
        "duplicate",
        "denied",
    }


def test_schema_verdict_values() -> None:
    """Spec line 351 / 515."""
    assert {v.value for v in SchemaVerdict} == {
        "valid",
        "malformed",
        "unsupported",
    }


def test_normalization_verdict_values() -> None:
    """Spec line 516."""
    assert {v.value for v in NormalizationVerdict} == {
        "normalized",
        "preserved",
        "rejected",
    }


def test_principal_type_values() -> None:
    """Spec line 240."""
    assert {v.value for v in PrincipalType} == {
        "user",
        "service",
        "anonymous",
        "unknown",
    }
