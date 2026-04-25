"""
Observability events and metrics emitted by L0 Request Intake.

Spec section: OBSERVABILITY EVENTS EMITTED BY INTAKE (lines 614-665).

INVARIANT (HARD NO):
- Do NOT log secrets or raw credentials.
- Do NOT log full sensitive payloads where policy forbids it.
- Do NOT store hidden tool authority in telemetry.
- Do NOT infer user intent in observability tags.

Events are facts about the envelope, not judgments about the semantic task.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class IngressEvent(str, Enum):
    """The 11 events emitted by intake (spec lines 622-632)."""

    INGRESS_RECEIVED = "IngressReceived"
    REQUEST_ID_ASSIGNED = "RequestIdAssigned"
    TRACE_ROOT_BOUND = "TraceRootBound"
    SOURCE_CLASSIFIED = "SourceClassified"
    AUTH_BASELINE_EVALUATED = "AuthBaselineEvaluated"
    QUOTA_EVALUATED = "QuotaEvaluated"
    SCHEMA_EVALUATED = "SchemaEvaluated"
    PAYLOAD_NORMALIZED = "PayloadNormalized"
    ATTACHMENT_MANIFEST_CAPTURED = "AttachmentManifestCaptured"
    INGRESS_ACCEPTED = "IngressAccepted"
    INGRESS_REJECTED = "IngressRejected"


# Metric names (spec lines 634-645). Names are stable so dashboards bind to them.
INGRESS_METRIC_NAMES: tuple[str, ...] = (
    "ingress_count",                 # by source_class
    "ingress_reject_rate",           # by reason_code
    "auth_reject_rate",
    "quota_throttle_rate",
    "duplicate_rate",
    "malformed_schema_rate",
    "unsupported_modality_rate",
    "average_payload_size",
    "attachment_count_distribution",
    "ingress_latency_ms",
    "normalization_failure_rate",
)


# Trace fields the intake event MUST carry (spec lines 647-658).
INGRESS_TRACE_FIELDS: tuple[str, ...] = (
    "request_id",
    "trace_root",
    "session_id",
    "tenant_id",
    "workspace_id",
    "source_channel",
    "source_class",
    "auth_verdict",
    "quota_verdict",
    "schema_verdict",
    "normalization_verdict",
    "reason_codes",
)


# Fields that MUST NEVER appear in event payloads under any circumstance.
# Used by the test suite as a denylist invariant check.
FORBIDDEN_EVENT_FIELDS: frozenset[str] = frozenset(
    {
        "auth_credential",
        "auth_token",
        "api_key",
        "oauth_token",
        "session_cookie",
        "raw_payload",  # full raw body text
        "body_text",    # full raw body text
        "secret",
        "password",
    }
)


@dataclass(frozen=True)
class IngressEventRecord:
    """One emitted intake event."""

    event: IngressEvent
    request_id: str
    trace_root: str
    fields: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Hard fail (loudly) if a forbidden field leaks into a record. This
        # is enforced at construction time so a bad caller cannot bypass it.
        bad = FORBIDDEN_EVENT_FIELDS.intersection(self.fields.keys())
        if bad:
            raise ValueError(
                f"IngressEventRecord must not include forbidden fields: {sorted(bad)}"
            )


__all__ = [
    "FORBIDDEN_EVENT_FIELDS",
    "INGRESS_METRIC_NAMES",
    "INGRESS_TRACE_FIELDS",
    "IngressEvent",
    "IngressEventRecord",
]
