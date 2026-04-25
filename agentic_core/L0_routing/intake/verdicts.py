"""
Verdicts and source classifications for L0 Request Intake.

These are the bounded enums used in the validated_request slip per the
spec's INGRESS OUTPUT CONTRACT and PASS / FAIL DECISION TABLE.
"""

from __future__ import annotations

from enum import Enum


class SourceClass(str, Enum):
    """Ingress source class: U1 user, U2 service, U3 batch, U4 alert/webhook."""

    USER = "user"
    SERVICE = "service"
    BATCH = "batch"
    WEBHOOK = "webhook"
    ALERT = "alert"


class PrincipalType(str, Enum):
    """Resolved principal kind after E2."""

    USER = "user"
    SERVICE = "service"
    ANONYMOUS = "anonymous"
    UNKNOWN = "unknown"


class AuthVerdict(str, Enum):
    """E2 auth verdict (spec line 242, 513)."""

    AUTHENTICATED = "authenticated"
    SERVICE_BOUND = "service-bound"
    ANONYMOUS_LIMITED = "anonymous-limited"
    REJECTED = "rejected"


class QuotaVerdict(str, Enum):
    """E3 quota verdict (spec line 294, 514)."""

    ALLOWED = "allowed"
    THROTTLED = "throttled"
    DUPLICATE = "duplicate"
    DENIED = "denied"


class SchemaVerdict(str, Enum):
    """E4 schema verdict (spec line 351, 515)."""

    VALID = "valid"
    MALFORMED = "malformed"
    UNSUPPORTED = "unsupported"


class NormalizationVerdict(str, Enum):
    """E5 normalization verdict (spec line 516).

    Note: spec line 424 describes E5_verdict as pass|reject, but the
    INGRESS OUTPUT CONTRACT (line 516) uses normalized|preserved|rejected.
    We adopt the contract form because that is what L1 consumes.
    """

    NORMALIZED = "normalized"
    PRESERVED = "preserved"
    REJECTED = "rejected"


class IdempotencyStatus(str, Enum):
    """E3 idempotency status (spec line 298)."""

    NOT_APPLICABLE = "not_applicable"
    NEW = "new"
    IN_FLIGHT = "in_flight"
    ALREADY_PROCESSED = "already_processed"


class AbusePrecheckStatus(str, Enum):
    """E3 abuse precheck status (spec line 299)."""

    CLEAR = "clear"
    FLAGGED = "flagged"
    BLOCKED = "blocked"


class StageVerdict(str, Enum):
    """Generic per-stage pass/reject verdict (E1, E5)."""

    PASS = "pass"
    REJECT = "reject"


__all__ = [
    "AbusePrecheckStatus",
    "AuthVerdict",
    "IdempotencyStatus",
    "NormalizationVerdict",
    "PrincipalType",
    "QuotaVerdict",
    "SchemaVerdict",
    "SourceClass",
    "StageVerdict",
]
