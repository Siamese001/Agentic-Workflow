"""
Typed Intake receipts (01.1, 01.2, 01.3, 01.4).

This module owns the typed receipt contracts defined by the
01_Request_Intake child specs. Each receipt:

- is a frozen dataclass (immutable evidence)
- carries a deterministic_receipt_hash computed from STABLE fields only
  (volatile observed_at / ingress_time / random ids excluded)
- never carries route, retrieval, prompt, execution, or write authority

All receipts are *evidence*. They are NEVER interpreted as runtime
dispositions. Spec-canonical statuses live in `status.py`.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.verdicts import (
    AuthVerdict,
    IdempotencyStatus,
    NormalizationVerdict,
    PrincipalType,
    QuotaVerdict,
    SchemaVerdict,
    SourceClass,
)


# ---------------------------------------------------------------------------
# Hashing helper
# ---------------------------------------------------------------------------


def _stable_hash(parts: Sequence[Any]) -> str:
    """Deterministic SHA-256 hex over a sequence of stable values.

    Each part is JSON-canonicalized (sorted keys, no whitespace, default=str)
    so dict order or non-string types do not perturb the digest. Volatile
    inputs (wall-clock, random IDs) MUST NOT appear in `parts`.
    """
    payload = "\n".join(json.dumps(p, sort_keys=True, separators=(",", ":"), default=str) for p in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ===========================================================================
# 01.1 — TRANSPORT / ENVELOPE INGRESS
# ===========================================================================


@dataclass(frozen=True)
class TransportEnvelopeReceipt:
    """01.1 evidence that an inbound frame arrived through an approved
    carrier and was parsed into a bounded envelope.

    Fields exactly track 01.1 §PHASE 1 DATA CONTRACTS §2.
    """

    receipt_id: str
    raw_envelope_id: str
    transport: str
    channel: str
    accepted_transport: bool
    frame_parse_status: str  # "ok" | "malformed" | "empty"
    method_allowed: bool
    content_type_allowed: bool
    encoding_allowed: bool
    body_size_status: str  # "ok" | "too_large" | "absent"
    attachment_inventory_status: str  # "ok" | "absent" | "bad_handle"
    raw_capture_status: str  # "ok" | "missing"
    transport_policy_ref: str
    rejection_reason_codes: tuple[IngressReasonCode, ...] = ()
    warnings: tuple[str, ...] = ()
    deterministic_receipt_hash: str = ""

    def with_hash(self) -> "TransportEnvelopeReceipt":
        """Return a copy with deterministic_receipt_hash filled.

        raw_envelope_id is excluded because it embeds the volatile
        request_id when no request_id_hint is supplied. Replay identity
        is established by transport+channel+raw_capture_status, not by the
        per-run envelope id.
        """
        h = _stable_hash(
            [
                self.transport,
                self.channel,
                self.accepted_transport,
                self.frame_parse_status,
                self.method_allowed,
                self.content_type_allowed,
                self.encoding_allowed,
                self.body_size_status,
                self.attachment_inventory_status,
                self.raw_capture_status,
                self.transport_policy_ref,
                [c.value for c in self.rejection_reason_codes],
            ]
        )
        return TransportEnvelopeReceipt(
            receipt_id=self.receipt_id,
            raw_envelope_id=self.raw_envelope_id,
            transport=self.transport,
            channel=self.channel,
            accepted_transport=self.accepted_transport,
            frame_parse_status=self.frame_parse_status,
            method_allowed=self.method_allowed,
            content_type_allowed=self.content_type_allowed,
            encoding_allowed=self.encoding_allowed,
            body_size_status=self.body_size_status,
            attachment_inventory_status=self.attachment_inventory_status,
            raw_capture_status=self.raw_capture_status,
            transport_policy_ref=self.transport_policy_ref,
            rejection_reason_codes=self.rejection_reason_codes,
            warnings=self.warnings,
            deterministic_receipt_hash=h,
        )


@dataclass(frozen=True)
class MalformedEnvelopeReport:
    """01.1 typed report when a transport-level rejection occurs."""

    report_id: str
    raw_envelope_id: str
    malformed_class: str
    decisive_reason: IngressReasonCode
    parse_error_summary: str
    recoverable_by_user: bool
    safe_user_visible_summary: str
    audit_refs: tuple[str, ...] = ()
    deterministic_report_hash: str = ""

    def with_hash(self) -> "MalformedEnvelopeReport":
        h = _stable_hash(
            [
                self.raw_envelope_id,
                self.malformed_class,
                self.decisive_reason.value,
                self.parse_error_summary,
                self.recoverable_by_user,
                self.safe_user_visible_summary,
                list(self.audit_refs),
            ]
        )
        return MalformedEnvelopeReport(
            report_id=self.report_id,
            raw_envelope_id=self.raw_envelope_id,
            malformed_class=self.malformed_class,
            decisive_reason=self.decisive_reason,
            parse_error_summary=self.parse_error_summary,
            recoverable_by_user=self.recoverable_by_user,
            safe_user_visible_summary=self.safe_user_visible_summary,
            audit_refs=self.audit_refs,
            deterministic_report_hash=h,
        )


# ===========================================================================
# 01.2 — IDENTITY / TENANT / SESSION BASELINE
# ===========================================================================


@dataclass(frozen=True)
class CallerIdentityClaim:
    """01.2 §1 — identity evidence captured from envelope metadata only."""

    caller_claim_id: str
    raw_envelope_id: str
    auth_mode: str  # "api_key" | "oauth" | "session" | "mtls" | "anonymous" | ...
    principal_id_hash: str | None
    principal_type: PrincipalType
    actor_class: str  # human_user | service_account | scheduler | webhook | cli_local_user | ...
    authenticated: bool
    auth_evidence_refs: tuple[str, ...] = ()
    auth_issuer: str | None = None
    auth_expiry_status: str = "n/a"  # ok | expired | unknown | n/a
    anonymous_allowed: bool = False
    identity_confidence: float = 0.0
    identity_warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class CallerScopeBaseline:
    """01.2 §2 — bound caller scope. baseline_hash deterministic from stable fields."""

    caller_scope_baseline_id: str
    caller_claim_id: str
    tenant_id: str | None
    tenant_scope: str | None
    session_id: str | None
    session_scope: str | None
    region: str | None
    data_residency_hint: str | None
    account_status: str  # "active" | "suspended" | "unknown"
    baseline_acl_tags: tuple[str, ...] = ()
    allowed_intake_surfaces: tuple[str, ...] = ()
    restricted_intake_surfaces: tuple[str, ...] = ()
    cross_tenant_risk: str = "none"  # none | low | medium | high
    cross_session_risk: str = "none"
    baseline_hash: str = ""

    def with_hash(self) -> "CallerScopeBaseline":
        # caller_claim_id is excluded because it is a volatile per-run uuid.
        # The deterministic identity of the scope is the (tenant, session,
        # region, scope tag) tuple.
        h = _stable_hash(
            [
                self.tenant_id,
                self.tenant_scope,
                self.session_id,
                self.session_scope,
                self.region,
                self.data_residency_hint,
                self.account_status,
                list(self.baseline_acl_tags),
                list(self.allowed_intake_surfaces),
                list(self.restricted_intake_surfaces),
                self.cross_tenant_risk,
                self.cross_session_risk,
            ]
        )
        return CallerScopeBaseline(
            caller_scope_baseline_id=self.caller_scope_baseline_id,
            caller_claim_id=self.caller_claim_id,
            tenant_id=self.tenant_id,
            tenant_scope=self.tenant_scope,
            session_id=self.session_id,
            session_scope=self.session_scope,
            region=self.region,
            data_residency_hint=self.data_residency_hint,
            account_status=self.account_status,
            baseline_acl_tags=self.baseline_acl_tags,
            allowed_intake_surfaces=self.allowed_intake_surfaces,
            restricted_intake_surfaces=self.restricted_intake_surfaces,
            cross_tenant_risk=self.cross_tenant_risk,
            cross_session_risk=self.cross_session_risk,
            baseline_hash=h,
        )


@dataclass(frozen=True)
class TenantBoundaryReceipt:
    """01.2 §3 — proves tenant binding decision."""

    receipt_id: str
    tenant_id: str | None
    tenant_resolved: bool
    tenant_source: str  # "claim" | "credential" | "header" | "inferred" | "none"
    tenant_allowed: bool
    tenant_conflict_detected: bool
    conflicting_tenant_refs: tuple[str, ...] = ()
    region_allowed: bool = True
    data_residency_status: str = "ok"
    reason_codes: tuple[IngressReasonCode, ...] = ()
    deterministic_receipt_hash: str = ""

    def with_hash(self) -> "TenantBoundaryReceipt":
        h = _stable_hash(
            [
                self.tenant_id,
                self.tenant_resolved,
                self.tenant_source,
                self.tenant_allowed,
                self.tenant_conflict_detected,
                list(self.conflicting_tenant_refs),
                self.region_allowed,
                self.data_residency_status,
                [c.value for c in self.reason_codes],
            ]
        )
        return TenantBoundaryReceipt(
            receipt_id=self.receipt_id,
            tenant_id=self.tenant_id,
            tenant_resolved=self.tenant_resolved,
            tenant_source=self.tenant_source,
            tenant_allowed=self.tenant_allowed,
            tenant_conflict_detected=self.tenant_conflict_detected,
            conflicting_tenant_refs=self.conflicting_tenant_refs,
            region_allowed=self.region_allowed,
            data_residency_status=self.data_residency_status,
            reason_codes=self.reason_codes,
            deterministic_receipt_hash=h,
        )


@dataclass(frozen=True)
class SessionBindingReceipt:
    """01.2 §4 — proves session bind/resume decision."""

    receipt_id: str
    session_id: str | None
    session_created_or_resumed: str  # "created" | "resumed" | "anonymous" | "rejected"
    session_scope: str | None
    session_valid: bool
    session_expiry_status: str = "ok"
    conversation_context_allowed: bool = False
    prior_context_access_baseline: str = "none"
    reason_codes: tuple[IngressReasonCode, ...] = ()
    deterministic_receipt_hash: str = ""

    def with_hash(self) -> "SessionBindingReceipt":
        h = _stable_hash(
            [
                self.session_id,
                self.session_created_or_resumed,
                self.session_scope,
                self.session_valid,
                self.session_expiry_status,
                self.conversation_context_allowed,
                self.prior_context_access_baseline,
                [c.value for c in self.reason_codes],
            ]
        )
        return SessionBindingReceipt(
            receipt_id=self.receipt_id,
            session_id=self.session_id,
            session_created_or_resumed=self.session_created_or_resumed,
            session_scope=self.session_scope,
            session_valid=self.session_valid,
            session_expiry_status=self.session_expiry_status,
            conversation_context_allowed=self.conversation_context_allowed,
            prior_context_access_baseline=self.prior_context_access_baseline,
            reason_codes=self.reason_codes,
            deterministic_receipt_hash=h,
        )


# ===========================================================================
# 01.3 — QUOTA / SIZE / DUPLICATE CONTROLS
# ===========================================================================


@dataclass(frozen=True)
class QuotaReceipt:
    """01.3 §2 — proves quota / rate / size / concurrency decision."""

    receipt_id: str
    tenant_id: str | None
    principal_id_hash: str | None
    session_id: str | None
    quota_policy_ref: str
    request_size_status: str  # "ok" | "too_large"
    attachment_count_status: str  # "ok" | "too_many"
    rate_limit_status: str  # "ok" | "throttled"
    daily_limit_status: str  # "ok" | "exceeded" | "unknown"
    concurrent_request_status: str  # "ok" | "exceeded" | "unknown"
    allowed_to_continue_intake: bool
    reason_codes: tuple[IngressReasonCode, ...] = ()
    quota_snapshot_ref: str = ""
    deterministic_receipt_hash: str = ""

    def with_hash(self) -> "QuotaReceipt":
        h = _stable_hash(
            [
                self.tenant_id,
                self.principal_id_hash,
                self.session_id,
                self.quota_policy_ref,
                self.request_size_status,
                self.attachment_count_status,
                self.rate_limit_status,
                self.daily_limit_status,
                self.concurrent_request_status,
                self.allowed_to_continue_intake,
                [c.value for c in self.reason_codes],
                self.quota_snapshot_ref,
            ]
        )
        return QuotaReceipt(
            receipt_id=self.receipt_id,
            tenant_id=self.tenant_id,
            principal_id_hash=self.principal_id_hash,
            session_id=self.session_id,
            quota_policy_ref=self.quota_policy_ref,
            request_size_status=self.request_size_status,
            attachment_count_status=self.attachment_count_status,
            rate_limit_status=self.rate_limit_status,
            daily_limit_status=self.daily_limit_status,
            concurrent_request_status=self.concurrent_request_status,
            allowed_to_continue_intake=self.allowed_to_continue_intake,
            reason_codes=self.reason_codes,
            quota_snapshot_ref=self.quota_snapshot_ref,
            deterministic_receipt_hash=h,
        )


@dataclass(frozen=True)
class DuplicateRequestFingerprint:
    """01.3 §3 — fingerprint that includes tenant/session boundary."""

    fingerprint_id: str
    raw_payload_hash: str
    normalized_payload_pre_hash: str | None
    principal_id_hash: str | None
    tenant_id: str | None
    session_id: str | None
    transport: str
    idempotency_key: str | None
    dedupe_window: int
    fingerprint_hash: str = ""
    duplicate_candidate_refs: tuple[str, ...] = ()

    def with_hash(self) -> "DuplicateRequestFingerprint":
        h = _stable_hash(
            [
                self.raw_payload_hash,
                self.normalized_payload_pre_hash,
                self.principal_id_hash,
                self.tenant_id,
                self.session_id,
                self.transport,
                self.idempotency_key,
                self.dedupe_window,
            ]
        )
        return DuplicateRequestFingerprint(
            fingerprint_id=self.fingerprint_id,
            raw_payload_hash=self.raw_payload_hash,
            normalized_payload_pre_hash=self.normalized_payload_pre_hash,
            principal_id_hash=self.principal_id_hash,
            tenant_id=self.tenant_id,
            session_id=self.session_id,
            transport=self.transport,
            idempotency_key=self.idempotency_key,
            dedupe_window=self.dedupe_window,
            fingerprint_hash=h,
            duplicate_candidate_refs=self.duplicate_candidate_refs,
        )


@dataclass(frozen=True)
class DuplicateSuppressionReceipt:
    """01.3 §4 — proves dedupe decision."""

    receipt_id: str
    duplicate_detected: bool
    duplicate_class: str
    prior_request_ref: str | None = None
    suppress_or_continue: str = "continue"  # "continue" | "suppress"
    reason_codes: tuple[IngressReasonCode, ...] = ()
    deterministic_receipt_hash: str = ""

    def with_hash(self) -> "DuplicateSuppressionReceipt":
        h = _stable_hash(
            [
                self.duplicate_detected,
                self.duplicate_class,
                self.prior_request_ref,
                self.suppress_or_continue,
                [c.value for c in self.reason_codes],
            ]
        )
        return DuplicateSuppressionReceipt(
            receipt_id=self.receipt_id,
            duplicate_detected=self.duplicate_detected,
            duplicate_class=self.duplicate_class,
            prior_request_ref=self.prior_request_ref,
            suppress_or_continue=self.suppress_or_continue,
            reason_codes=self.reason_codes,
            deterministic_receipt_hash=h,
        )


# Duplicate class label set per spec line 259-265
DUPLICATE_CLASSES: frozenset[str] = frozenset(
    {
        "exact_replay_same_idempotency_key",
        "exact_replay_same_payload",
        "near_duplicate_transport_retry",
        "double_submit",
        "suspicious_replay",
        "not_duplicate",
    }
)


# ===========================================================================
# 01.4 — SCHEMA / NORMALIZATION / SECURITY
# ===========================================================================


@dataclass(frozen=True)
class RequestSchemaValidationReceipt:
    """01.4 §2 — proves schema validation outcome."""

    receipt_id: str
    request_schema_ref: str
    schema_version: str
    schema_valid: bool
    missing_fields: tuple[str, ...] = ()
    malformed_fields: tuple[str, ...] = ()
    unknown_fields: tuple[str, ...] = ()
    coercions_applied: tuple[str, ...] = ()
    structural_risk_flags: tuple[str, ...] = ()
    reason_codes: tuple[IngressReasonCode, ...] = ()
    deterministic_receipt_hash: str = ""

    def with_hash(self) -> "RequestSchemaValidationReceipt":
        h = _stable_hash(
            [
                self.request_schema_ref,
                self.schema_version,
                self.schema_valid,
                list(self.missing_fields),
                list(self.malformed_fields),
                list(self.unknown_fields),
                list(self.coercions_applied),
                list(self.structural_risk_flags),
                [c.value for c in self.reason_codes],
            ]
        )
        return RequestSchemaValidationReceipt(
            receipt_id=self.receipt_id,
            request_schema_ref=self.request_schema_ref,
            schema_version=self.schema_version,
            schema_valid=self.schema_valid,
            missing_fields=self.missing_fields,
            malformed_fields=self.malformed_fields,
            unknown_fields=self.unknown_fields,
            coercions_applied=self.coercions_applied,
            structural_risk_flags=self.structural_risk_flags,
            reason_codes=self.reason_codes,
            deterministic_receipt_hash=h,
        )


@dataclass(frozen=True)
class NormalizedUserPayload:
    """01.4 §3 — bounded normalized representation of the user payload.

    The raw payload remains preserved separately by hash + ref. Original
    user text is recoverable through body_ref / audit_ref.
    """

    normalized_payload_id: str
    raw_payload_hash: str
    normalized_text: str
    normalized_fields: Mapping[str, Any] = field(default_factory=dict)
    attachment_refs: tuple[str, ...] = ()
    url_refs: tuple[str, ...] = ()
    file_refs: tuple[str, ...] = ()
    quoted_text_blocks: tuple[str, ...] = ()
    command_like_blocks: tuple[str, ...] = ()
    language_hint: str | None = None
    user_visible_text: str = ""
    normalization_warnings: tuple[str, ...] = ()
    normalized_payload_hash: str = ""


# ===========================================================================
# 01.5 — TRACE / REPLAY / CORRELATION (data shapes; pipeline in correlation.py)
# ===========================================================================


@dataclass(frozen=True)
class RequestCorrelationReceipt:
    """01.5 §1 — receipt that binds request_id / session_id / trace_root."""

    receipt_id: str
    request_id: str
    session_id: str
    trace_root: str
    tenant_id: str | None
    principal_id_hash: str | None
    raw_envelope_id: str
    normalized_payload_id: str | None
    correlation_source: str  # "client_provided" | "intake_assigned" | "upstream_traceparent"
    parent_trace_ref: str | None = None
    provisional_span_refs: tuple[str, ...] = ()
    deterministic_receipt_hash: str = ""

    def with_hash(self) -> "RequestCorrelationReceipt":
        # Exclude request_id, trace_root, raw_envelope_id, normalized_payload_id,
        # parent_trace_ref, provisional_span_refs — all volatile per-run.
        # Stable correlation identity is (session, tenant, principal,
        # correlation_source).
        h = _stable_hash(
            [
                self.session_id,
                self.tenant_id,
                self.principal_id_hash,
                self.correlation_source,
            ]
        )
        return RequestCorrelationReceipt(
            receipt_id=self.receipt_id,
            request_id=self.request_id,
            session_id=self.session_id,
            trace_root=self.trace_root,
            tenant_id=self.tenant_id,
            principal_id_hash=self.principal_id_hash,
            raw_envelope_id=self.raw_envelope_id,
            normalized_payload_id=self.normalized_payload_id,
            correlation_source=self.correlation_source,
            parent_trace_ref=self.parent_trace_ref,
            provisional_span_refs=self.provisional_span_refs,
            deterministic_receipt_hash=h,
        )


@dataclass(frozen=True)
class IngressReplaySeed:
    """01.5 §2 — replay seed scoped to ingress; NOT the L0 RouteContract replay_key."""

    replay_seed_id: str
    request_id: str
    session_id: str
    tenant_id: str | None
    principal_id_hash: str | None
    transport: str
    raw_payload_hash: str
    normalized_payload_hash: str
    schema_version: str
    intake_policy_ref: str
    replay_key_seed: str
    replay_seed_hash: str = ""

    def with_hash(self) -> "IngressReplaySeed":
        h = _stable_hash(
            [
                self.session_id,
                self.tenant_id,
                self.principal_id_hash,
                self.transport,
                self.raw_payload_hash,
                self.normalized_payload_hash,
                self.schema_version,
                self.intake_policy_ref,
                self.replay_key_seed,
            ]
        )
        return IngressReplaySeed(
            replay_seed_id=self.replay_seed_id,
            request_id=self.request_id,
            session_id=self.session_id,
            tenant_id=self.tenant_id,
            principal_id_hash=self.principal_id_hash,
            transport=self.transport,
            raw_payload_hash=self.raw_payload_hash,
            normalized_payload_hash=self.normalized_payload_hash,
            schema_version=self.schema_version,
            intake_policy_ref=self.intake_policy_ref,
            replay_key_seed=self.replay_key_seed,
            replay_seed_hash=h,
        )


@dataclass(frozen=True)
class NormalizedRequestHash:
    """01.5 §3 — hash that identifies the *logical* request across replay."""

    hash_id: str
    normalized_payload_hash: str
    caller_scope_baseline_hash: str
    schema_version: str
    origin_label_manifest_hash: str
    entry_policy_refs: tuple[str, ...] = ()
    normalized_request_hash: str = ""

    def with_hash(self) -> "NormalizedRequestHash":
        h = _stable_hash(
            [
                self.normalized_payload_hash,
                self.caller_scope_baseline_hash,
                self.schema_version,
                self.origin_label_manifest_hash,
                list(self.entry_policy_refs),
            ]
        )
        return NormalizedRequestHash(
            hash_id=self.hash_id,
            normalized_payload_hash=self.normalized_payload_hash,
            caller_scope_baseline_hash=self.caller_scope_baseline_hash,
            schema_version=self.schema_version,
            origin_label_manifest_hash=self.origin_label_manifest_hash,
            entry_policy_refs=self.entry_policy_refs,
            normalized_request_hash=h,
        )


@dataclass(frozen=True)
class IntakeManifestHash:
    """01.5 §4 — composite hash over all child receipt hashes."""

    manifest_hash_id: str
    transport_receipt_hash: str
    caller_scope_baseline_hash: str
    quota_receipt_hash: str
    schema_validation_receipt_hash: str
    origin_label_manifest_hash: str
    normalized_request_hash: str
    replay_seed_hash: str
    intake_manifest_hash: str = ""

    def with_hash(self) -> "IntakeManifestHash":
        h = _stable_hash(
            [
                self.transport_receipt_hash,
                self.caller_scope_baseline_hash,
                self.quota_receipt_hash,
                self.schema_validation_receipt_hash,
                self.origin_label_manifest_hash,
                self.normalized_request_hash,
                self.replay_seed_hash,
            ]
        )
        return IntakeManifestHash(
            manifest_hash_id=self.manifest_hash_id,
            transport_receipt_hash=self.transport_receipt_hash,
            caller_scope_baseline_hash=self.caller_scope_baseline_hash,
            quota_receipt_hash=self.quota_receipt_hash,
            schema_validation_receipt_hash=self.schema_validation_receipt_hash,
            origin_label_manifest_hash=self.origin_label_manifest_hash,
            normalized_request_hash=self.normalized_request_hash,
            replay_seed_hash=self.replay_seed_hash,
            intake_manifest_hash=h,
        )


__all__ = [
    "CallerIdentityClaim",
    "CallerScopeBaseline",
    "DUPLICATE_CLASSES",
    "DuplicateRequestFingerprint",
    "DuplicateSuppressionReceipt",
    "IngressReplaySeed",
    "IntakeManifestHash",
    "MalformedEnvelopeReport",
    "NormalizedRequestHash",
    "NormalizedUserPayload",
    "QuotaReceipt",
    "RequestCorrelationReceipt",
    "RequestSchemaValidationReceipt",
    "SessionBindingReceipt",
    "TenantBoundaryReceipt",
    "TransportEnvelopeReceipt",
]
