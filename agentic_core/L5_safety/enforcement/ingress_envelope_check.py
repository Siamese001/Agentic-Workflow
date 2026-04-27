"""Ingress Envelope Check — E1 through E7 pre-pipeline gate.

This module is the single mandatory ingress gate that every inbound request
MUST pass before reaching L1 reasoning.  It enforces the E1–E7 contract
described in ``docs/reference/01_Request_Intake/01_request_intake.md``::

    E1  Transport validation     — well-formed request envelope
    E2  Schema + size / nesting  — required fields + oversize / depth guard
    E3  Identity verification    — pluggable IdentityVerifier (JWT / HMAC / OAuth)
    E4  Quota / rate-limit check — default in-process token-bucket limiter
    E5  Payload normalization    — deterministic canonicalisation (NFC, control chars, whitespace)
    E6  Safety screen            — prompt-injection / PII / jailbreak tripwire
    E7  Replay deduplication     — bounded LRU cache with optional TTL

On success  → returns StampedRequest (typed, trace-stamped, quota-consumed).
Ambiguity   → returns ClarificationRequired (third outcome, not an exception).
Rejection   → raises IngressRejected carrying a RejectionSlip.

Layer authority: L5 (cross-cutting policy plane).
Write authority: NONE — read/stamp only; no durable state mutation.
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L5_safety.enforcement.identity_verifier import (
    IdentityVerificationError,
    IdentityVerifier,
    NoopIdentityVerifier,
    VerifiedIdentity,
)
from agentic_core.L5_safety.enforcement.ingress_telemetry import (
    IngressMetrics,
    default_metrics,
    monotonic_ms,
)
from agentic_core.L5_safety.enforcement.input_safety_screen import (
    InputSafetyScreen,
    RegexInputSafetyScreen,
    SafetyFlag,
    extract_screen_text,
)
from agentic_core.L5_safety.enforcement.payload_normalizer import (
    NormalizerOptions,
    PayloadNormalizer,
    estimate_payload_depth,
    estimate_payload_size,
)
from agentic_core.L5_safety.enforcement.rate_limit import (
    RateLimiter,
    TokenBucketRateLimiter,
)
from agentic_core.L5_safety.enforcement.replay_cache import (
    LRUReplayCache,
    ReplayCache,
    SetReplayCache,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_transcripts_response,
    _emit_validated_by_safety_plane,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    emit_determinism_digest,
    emit_replay_key,
)

logger = logging.getLogger(__name__)

_REQUIRED_ENVELOPE_FIELDS = ("request_payload", "caller_identity", "schema_version")
_TRUSTED_SCHEMA_VERSIONS = {"1.0", "1.1", "2.0"}

_DEFAULT_MAX_PAYLOAD_BYTES = 1_048_576  # 1 MiB
_DEFAULT_MAX_PAYLOAD_DEPTH = 32

# E2 attachment / modality limits (W2 — spec lines 79-83).
_DEFAULT_MAX_ATTACHMENTS = 16
_DEFAULT_MAX_ATTACHMENT_BYTES = 32 * 1024 * 1024  # 32 MiB per attachment
_MAX_FILENAME_LEN = 512
_MAX_CONTENT_TYPE_LEN = 256
_FILENAME_FORBIDDEN_RE = re.compile(r"[\x00-\x1f\x7f]|[\\/]")
_DEFAULT_ALLOWED_MODALITIES: frozenset[str] = frozenset(
    {"text", "image", "audio", "video", "document", "mixed"}
)
_VALID_INGRESS_SOURCE_CLASSES: frozenset[str] = frozenset(
    {"user", "service", "batch", "webhook", "alert", "unknown"}
)

_REGISTERED = False


def register() -> None:
    """Register this module with the lifecycle-trace contract plane.

    Call once at application startup; safe to call multiple times. Replaces
    the previous import-time side effects (closes gap G-12).
    """

    global _REGISTERED
    if _REGISTERED:
        return
    emit_replay_key("p0", "ingress_envelope_check")
    emit_determinism_digest("p0", "ingress_envelope_check")
    _emit_reads_policy_state("p1", "ingress_envelope_check", "L5")
    _emit_verifies_policy("p1", "ingress_envelope_check", "policy_check")
    _emit_verifies_boundary("p1", "ingress_envelope_check", "boundary_check")
    _emit_validated_by_safety_plane("p1", "ingress_envelope_check", "safety_validation")
    _emit_hard_fails_untranscripted("p1", "ingress_envelope_check")
    _emit_gated_by_confidence("p1", "ingress_envelope_check", "confidence_gate")
    _REGISTERED = True


class RejectionReasonCode(str, Enum):
    """Rejection reason codes emitted in :class:`RejectionSlip`."""

    MALFORMED_ENVELOPE = "E1_MALFORMED_ENVELOPE"
    SCHEMA_INVALID = "E2_SCHEMA_INVALID"
    PAYLOAD_OVERSIZED = "E2_PAYLOAD_OVERSIZED"
    PAYLOAD_TOO_DEEP = "E2_PAYLOAD_TOO_DEEP"
    TOO_MANY_ATTACHMENTS = "E2_TOO_MANY_ATTACHMENTS"
    ATTACHMENT_OVERSIZED = "E2_ATTACHMENT_OVERSIZED"
    ATTACHMENT_MALFORMED = "E2_ATTACHMENT_MALFORMED"
    UNSUPPORTED_MODALITY = "E2_UNSUPPORTED_MODALITY"
    IDENTITY_MISSING = "E3_IDENTITY_MISSING"
    IDENTITY_UNTRUSTED = "E3_IDENTITY_UNTRUSTED"
    QUOTA_EXCEEDED = "E4_QUOTA_EXCEEDED"
    RATE_LIMITED = "E4_RATE_LIMITED"
    INJECTION_DETECTED = "E6_INJECTION_DETECTED"
    JAILBREAK_DETECTED = "E6_JAILBREAK_DETECTED"
    PII_DETECTED = "E6_PII_DETECTED"
    REPLAY_DUPLICATE = "E7_REPLAY_DUPLICATE"


@dataclass
class RejectionSlip:
    """Typed fail-closed rejection record emitted for every gate failure."""

    reason_code: RejectionReasonCode
    request_id: str
    trace_root: str
    message: str
    gate_stage: str
    timestamp_utc: float = field(default_factory=time.time)
    matched_fragments: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reason_code": self.reason_code.value,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "message": self.message,
            "gate_stage": self.gate_stage,
            "timestamp_utc": self.timestamp_utc,
            "matched_fragments": list(self.matched_fragments),
        }


class IngressRejected(Exception):
    """Raised when any E1–E7 check fails.  Carries the :class:`RejectionSlip`."""

    def __init__(self, slip: RejectionSlip) -> None:
        self.slip = slip
        super().__init__(f"[{slip.reason_code.value}] {slip.message}")


@dataclass
class StampedRequest:
    """Typed output of a fully-cleared ingress gate.

    ``request_payload`` is the raw payload as received (preserved for audit).
    ``normalized_payload`` is the E5 canonical form that downstream consumers
    MUST prefer. ``verified_identity`` carries the E3 verified triple.

    Spec output-contract fields (``docs/reference/01_Request_Intake/01_request_intake.md``
    lines 95-119): ``ingress_source_class``, ``auth_verdict``, ``quota_verdict``,
    ``schema_verdict``, ``raw_payload_ref``, ``attachment_manifest`` are populated
    so L1 can read the bounded slip without re-deriving them.
    """

    request_id: str
    session_id: str
    trace_root: str
    caller_scope_baseline: str
    schema_version: str
    request_payload: Any
    normalized_payload: Any
    caller_identity: str
    tenant_id: str
    verified_identity: VerifiedIdentity | None = None
    stamped_at: float = field(default_factory=time.time)
    # Spec output-contract additions (W1).
    ingress_source_class: str = "unknown"
    auth_verdict: str = "authenticated"
    quota_verdict: str = "allowed"
    schema_verdict: str = "valid"
    raw_payload_ref: str = ""
    attachment_manifest: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    modality: str = "text"

    @property
    def ingress_time_utc(self) -> float:
        """Alias for ``stamped_at`` for v33-map contract parity."""

        return self.stamped_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "trace_root": self.trace_root,
            "caller_scope_baseline": self.caller_scope_baseline,
            "schema_version": self.schema_version,
            "request_payload": self.request_payload,
            "normalized_payload": self.normalized_payload,
            "caller_identity": self.caller_identity,
            "tenant_id": self.tenant_id,
            "verified_identity": (
                {
                    "caller_id": self.verified_identity.caller_id,
                    "tenant_id": self.verified_identity.tenant_id,
                    "scopes": list(self.verified_identity.scopes),
                    "verified_at_utc": self.verified_identity.verified_at_utc,
                }
                if self.verified_identity
                else None
            ),
            "stamped_at": self.stamped_at,
            "ingress_time_utc": self.ingress_time_utc,
            "ingress_source_class": self.ingress_source_class,
            "auth_verdict": self.auth_verdict,
            "quota_verdict": self.quota_verdict,
            "schema_verdict": self.schema_verdict,
            "raw_payload_ref": self.raw_payload_ref,
            "attachment_manifest": [dict(a) for a in self.attachment_manifest],
            "modality": self.modality,
        }


@dataclass
class ClarificationRequired:
    """Third outcome: envelope is structurally valid but intent is missing/ambiguous.

    Returned by :meth:`IngressEnvelopeCheck.check` when the caller supplied a
    well-formed envelope but ``request_payload`` has no usable intent. Callers
    surface this back to the source adapter; no downstream L1 work is started.
    """

    request_id: str
    trace_root: str
    reason: str
    suggested_followups: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "outcome": "CLARIFICATION_REQUIRED",
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "reason": self.reason,
            "suggested_followups": list(self.suggested_followups),
        }


class IngressEnvelopeCheck:
    """E1–E7 ingress gate — single mandatory pre-pipeline enforcement point.

    Usage::

        gate = IngressEnvelopeCheck()  # production defaults
        result = gate.check(raw_envelope)
        if isinstance(result, ClarificationRequired):
            ...  # route back to caller
        else:
            stamped: StampedRequest = result
            ...  # hand to L1

    Layer authority: L5 (policy plane) — read/stamp only.
    """

    def __init__(
        self,
        rate_limiter: RateLimiter | None = None,
        seen_request_ids: set[str] | None = None,
        trusted_schema_versions: set[str] | None = None,
        *,
        identity_verifier: IdentityVerifier | None = None,
        safety_screen: InputSafetyScreen | None = None,
        normalizer: PayloadNormalizer | None = None,
        replay_cache: ReplayCache | None = None,
        max_payload_bytes: int = _DEFAULT_MAX_PAYLOAD_BYTES,
        max_payload_depth: int = _DEFAULT_MAX_PAYLOAD_DEPTH,
        max_attachments: int = _DEFAULT_MAX_ATTACHMENTS,
        max_attachment_bytes: int = _DEFAULT_MAX_ATTACHMENT_BYTES,
        allowed_modalities: frozenset[str] | set[str] | None = None,
        enable_safety_screen: bool = True,
        metrics: IngressMetrics | None = None,
    ) -> None:
        self._rate_limiter: RateLimiter = rate_limiter or TokenBucketRateLimiter()
        self._trusted_schema_versions = trusted_schema_versions or _TRUSTED_SCHEMA_VERSIONS
        self._identity_verifier: IdentityVerifier = identity_verifier or NoopIdentityVerifier()
        self._safety_screen: InputSafetyScreen | None = (
            (safety_screen or RegexInputSafetyScreen()) if enable_safety_screen else None
        )
        self._normalizer = normalizer or PayloadNormalizer(NormalizerOptions())
        self._max_payload_bytes = int(max_payload_bytes)
        self._max_payload_depth = int(max_payload_depth)
        self._max_attachments = int(max_attachments)
        self._max_attachment_bytes = int(max_attachment_bytes)
        self._allowed_modalities: frozenset[str] = (
            frozenset(allowed_modalities) if allowed_modalities is not None else _DEFAULT_ALLOWED_MODALITIES
        )

        if replay_cache is not None:
            self._replay_cache: ReplayCache = replay_cache
        elif seen_request_ids is not None:
            self._replay_cache = SetReplayCache(seen_request_ids)
        else:
            self._replay_cache = LRUReplayCache()

        self._metrics = metrics or default_metrics()

    def check(self, raw_envelope: dict[str, Any]) -> StampedRequest | ClarificationRequired:
        """Run E1–E7 checks in order.

        Returns :class:`StampedRequest` on pass or :class:`ClarificationRequired`
        when intent is missing. Raises :class:`IngressRejected` on any hard
        rejection (fail-closed).
        """

        return self.check_blocking(raw_envelope)

    def check_blocking(self, raw_envelope: dict[str, Any]) -> StampedRequest | ClarificationRequired:
        """Blocking variant — runs all checks before any downstream call.

        This is the recommended mode: no expensive / side-effecting downstream
        stage starts before the gate clears (OpenAI Agents SDK guidance).
        """

        started_ms = monotonic_ms()
        try:
            result = self._do_check(raw_envelope)
        except IngressRejected as exc:
            self._metrics.record_rejection(
                reason_code=exc.slip.reason_code.value,
                gate_stage=exc.slip.gate_stage,
                latency_ms=monotonic_ms() - started_ms,
            )
            raise

        if isinstance(result, ClarificationRequired):
            self._metrics.record_clarification(reason=result.reason, latency_ms=monotonic_ms() - started_ms)
        else:
            self._metrics.record_accepted(tenant_id=result.tenant_id, latency_ms=monotonic_ms() - started_ms)
        return result

    def _do_check(self, raw_envelope: dict[str, Any]) -> StampedRequest | ClarificationRequired:
        pre_request_id = str(uuid.uuid4())
        pre_trace = hashlib.sha256(f"{pre_request_id}:{time.time()}".encode()).hexdigest()[:16]

        self._e1_transport(raw_envelope, pre_request_id, pre_trace)

        request_id = raw_envelope.get("request_id") or str(uuid.uuid4())
        trace_root = hashlib.sha256(f"{request_id}:{time.time()}".encode()).hexdigest()[:16]

        _emit_snapshots_state(request_id, "IngressEnvelopeCheck.check", "ingress_state")
        _emit_applies_guardrail(request_id, "IngressEnvelopeCheck.check", "E1_E7_ingress")
        _emit_records_execution_trace(request_id, "L5_POLICY", "IngressEnvelopeCheck.check")
        _seg_hash = hashlib.sha256(f"{request_id}:IngressEnvelopeCheck".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(request_id, _seg_hash, _seg_hash, 0)

        self._e2_schema_and_size(raw_envelope, request_id, trace_root)
        attachment_manifest = self._e2_attachments(raw_envelope, request_id, trace_root)
        modality = self._e2_modality(raw_envelope, request_id, trace_root)
        verified = self._e3_identity(raw_envelope, request_id, trace_root)
        self._e4_quota(raw_envelope, request_id, trace_root)
        normalized = self._e5_normalize(raw_envelope.get("request_payload"))
        self._e6_safety(normalized, request_id, trace_root)

        session_id = raw_envelope.get("session_id") or str(uuid.uuid4())
        caller_scope_baseline = (
            verified.fingerprint() if verified is not None else self._derive_scope_baseline(raw_envelope)
        )
        tenant_id = verified.tenant_id if verified else str(raw_envelope.get("tenant_id") or "default")

        # Spec output contract additions (W1).
        source_class_raw = str(raw_envelope.get("ingress_source_class") or "unknown").lower()
        ingress_source_class = (
            source_class_raw if source_class_raw in _VALID_INGRESS_SOURCE_CLASSES else "unknown"
        )
        auth_verdict = self._derive_auth_verdict(verified, raw_envelope)
        raw_payload_ref = self._compute_raw_payload_ref(raw_envelope.get("request_payload"))

        stamped = StampedRequest(
            request_id=request_id,
            session_id=session_id,
            trace_root=trace_root,
            caller_scope_baseline=caller_scope_baseline,
            schema_version=raw_envelope.get("schema_version", "1.0"),
            request_payload=raw_envelope.get("request_payload"),
            normalized_payload=normalized,
            caller_identity=raw_envelope.get("caller_identity", ""),
            tenant_id=tenant_id,
            verified_identity=verified,
            ingress_source_class=ingress_source_class,
            auth_verdict=auth_verdict,
            quota_verdict="allowed",  # we passed E4 to reach here
            schema_verdict="valid",  # we passed E2 to reach here
            raw_payload_ref=raw_payload_ref,
            attachment_manifest=attachment_manifest,
            modality=modality,
        )

        self._e7_dedup(stamped, trace_root)

        clarify = self._clarify_if_empty_intent(stamped)
        if clarify is not None:
            return clarify

        _emit_transcripts_response(request_id, "IngressEnvelopeCheck", "stamped_request")
        logger.info(
            "[IngressEnvelopeCheck] Stamped request_id=%s trace_root=%s tenant=%s",
            request_id,
            trace_root,
            tenant_id,
        )
        return stamped

    # ------------------------------------------------------------------ E1
    def _e1_transport(self, env: dict, request_id: str, trace_root: str) -> None:
        if not isinstance(env, dict) or not env:
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.MALFORMED_ENVELOPE,
                    request_id=request_id,
                    trace_root=trace_root,
                    message="Request envelope is not a non-empty dict.",
                    gate_stage="E1_TRANSPORT",
                )
            )

    # ------------------------------------------------------------------ E2
    def _e2_schema_and_size(self, env: dict, request_id: str, trace_root: str) -> None:
        missing = [f for f in _REQUIRED_ENVELOPE_FIELDS if f not in env]
        if missing:
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.SCHEMA_INVALID,
                    request_id=request_id,
                    trace_root=trace_root,
                    message=f"Missing required envelope fields: {missing}",
                    gate_stage="E2_SCHEMA",
                )
            )
        version = env.get("schema_version", "")
        if version not in self._trusted_schema_versions:
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.SCHEMA_INVALID,
                    request_id=request_id,
                    trace_root=trace_root,
                    message=(
                        f"Untrusted schema_version: {version!r}. "
                        f"Accepted: {sorted(self._trusted_schema_versions)}"
                    ),
                    gate_stage="E2_SCHEMA",
                )
            )

        payload = env.get("request_payload")
        size = estimate_payload_size(payload)
        if size > self._max_payload_bytes:
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.PAYLOAD_OVERSIZED,
                    request_id=request_id,
                    trace_root=trace_root,
                    message=f"request_payload size {size} > limit {self._max_payload_bytes} bytes.",
                    gate_stage="E2_SIZE",
                )
            )
        depth = estimate_payload_depth(payload)
        if depth > self._max_payload_depth:
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.PAYLOAD_TOO_DEEP,
                    request_id=request_id,
                    trace_root=trace_root,
                    message=f"request_payload nesting depth {depth} > limit {self._max_payload_depth}.",
                    gate_stage="E2_DEPTH",
                )
            )

    # ------------------------------------------------------------------ E3
    def _e3_identity(self, env: dict, request_id: str, trace_root: str) -> VerifiedIdentity:
        identity = env.get("caller_identity")
        if not identity:
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.IDENTITY_MISSING,
                    request_id=request_id,
                    trace_root=trace_root,
                    message="caller_identity is missing or empty.",
                    gate_stage="E3_IDENTITY",
                )
            )
        if not isinstance(identity, str) or len(identity.strip()) == 0:
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.IDENTITY_UNTRUSTED,
                    request_id=request_id,
                    trace_root=trace_root,
                    message="caller_identity must be a non-empty string.",
                    gate_stage="E3_IDENTITY",
                )
            )
        try:
            return self._identity_verifier.verify(identity, env)
        except IdentityVerificationError as exc:
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.IDENTITY_UNTRUSTED,
                    request_id=request_id,
                    trace_root=trace_root,
                    message=f"Identity verification failed: {exc}",
                    gate_stage="E3_IDENTITY",
                )
            ) from exc

    # ------------------------------------------------------------------ E4
    def _e4_quota(self, env: dict, request_id: str, trace_root: str) -> None:
        caller_id = env.get("caller_identity", "unknown")
        if not self._rate_limiter.is_allowed(caller_id):
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.RATE_LIMITED,
                    request_id=request_id,
                    trace_root=trace_root,
                    message=f"Rate limit exceeded for caller: {caller_id}",
                    gate_stage="E4_QUOTA",
                )
            )

    # --------------------------------------------------- E2 attachments / modality (W2)
    def _e2_attachments(self, env: dict, request_id: str, trace_root: str) -> tuple[dict[str, Any], ...]:
        """Validate attachment list shape & size; return bounded manifest.

        Manifest is sourced from ``env['attachments']`` OR
        ``env['request_payload']['attachments']`` (whichever is present).
        Each attachment must be a dict with at minimum ``filename`` and ``size``.
        """

        atts = env.get("attachments")
        if atts is None and isinstance(env.get("request_payload"), dict):
            atts = env["request_payload"].get("attachments")
        if atts is None:
            return ()
        if not isinstance(atts, (list, tuple)):
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.ATTACHMENT_MALFORMED,
                    request_id=request_id,
                    trace_root=trace_root,
                    message="attachments must be a list of dicts.",
                    gate_stage="E2_ATTACHMENT",
                )
            )
        if len(atts) > self._max_attachments:
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.TOO_MANY_ATTACHMENTS,
                    request_id=request_id,
                    trace_root=trace_root,
                    message=(f"attachment count {len(atts)} > limit {self._max_attachments}."),
                    gate_stage="E2_ATTACHMENT",
                )
            )
        manifest: list[dict[str, Any]] = []
        for idx, att in enumerate(atts):
            if not isinstance(att, dict):
                raise IngressRejected(
                    RejectionSlip(
                        reason_code=RejectionReasonCode.ATTACHMENT_MALFORMED,
                        request_id=request_id,
                        trace_root=trace_root,
                        message=f"attachments[{idx}] is not a dict.",
                        gate_stage="E2_ATTACHMENT",
                    )
                )
            filename = att.get("filename") or att.get("name")
            size_raw = att.get("size")
            content_type = att.get("content_type") or att.get("mime") or "application/octet-stream"
            if not isinstance(filename, str) or not filename.strip():
                raise IngressRejected(
                    RejectionSlip(
                        reason_code=RejectionReasonCode.ATTACHMENT_MALFORMED,
                        request_id=request_id,
                        trace_root=trace_root,
                        message=f"attachments[{idx}] missing filename.",
                        gate_stage="E2_ATTACHMENT",
                    )
                )
            if len(filename) > _MAX_FILENAME_LEN:
                raise IngressRejected(
                    RejectionSlip(
                        reason_code=RejectionReasonCode.ATTACHMENT_MALFORMED,
                        request_id=request_id,
                        trace_root=trace_root,
                        message=(
                            f"attachments[{idx}] filename length {len(filename)} > {_MAX_FILENAME_LEN}."
                        ),
                        gate_stage="E2_ATTACHMENT",
                    )
                )
            if _FILENAME_FORBIDDEN_RE.search(filename):
                raise IngressRejected(
                    RejectionSlip(
                        reason_code=RejectionReasonCode.ATTACHMENT_MALFORMED,
                        request_id=request_id,
                        trace_root=trace_root,
                        message=(f"attachments[{idx}] filename contains control or path separator chars."),
                        gate_stage="E2_ATTACHMENT",
                    )
                )
            # Reject bool explicitly: ``isinstance(True, int) is True`` in Python.
            if isinstance(size_raw, bool) or not isinstance(size_raw, (int, float)) or size_raw < 0:
                raise IngressRejected(
                    RejectionSlip(
                        reason_code=RejectionReasonCode.ATTACHMENT_MALFORMED,
                        request_id=request_id,
                        trace_root=trace_root,
                        message=(f"attachments[{idx}] size must be a non-negative integer or float."),
                        gate_stage="E2_ATTACHMENT",
                    )
                )
            size = int(size_raw)
            if size > self._max_attachment_bytes:
                raise IngressRejected(
                    RejectionSlip(
                        reason_code=RejectionReasonCode.ATTACHMENT_OVERSIZED,
                        request_id=request_id,
                        trace_root=trace_root,
                        message=(
                            f"attachments[{idx}] size {size} > limit {self._max_attachment_bytes} bytes."
                        ),
                        gate_stage="E2_ATTACHMENT",
                    )
                )
            content_type_str = str(content_type)[:_MAX_CONTENT_TYPE_LEN]
            manifest.append(
                {
                    "filename": filename,
                    "size": size,
                    "content_type": content_type_str,
                }
            )
        return tuple(manifest)

    def _e2_modality(self, env: dict, request_id: str, trace_root: str) -> str:
        modality_raw = env.get("modality")
        if modality_raw is None and isinstance(env.get("request_payload"), dict):
            modality_raw = env["request_payload"].get("modality")
        if modality_raw is None:
            return "text"
        modality = str(modality_raw).strip().lower()
        if modality not in self._allowed_modalities:
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.UNSUPPORTED_MODALITY,
                    request_id=request_id,
                    trace_root=trace_root,
                    message=(f"modality {modality!r} not in allowlist {sorted(self._allowed_modalities)}."),
                    gate_stage="E2_MODALITY",
                )
            )
        return modality

    # ------------------------------------------------------------------ E5
    def _e5_normalize(self, payload: Any) -> Any:
        return self._normalizer.normalize(payload)

    # ------------------------------------------------------------------ E6
    def _e6_safety(self, normalized_payload: Any, request_id: str, trace_root: str) -> None:
        if self._safety_screen is None:
            return
        text = extract_screen_text(normalized_payload)
        result = self._safety_screen.screen(text)
        if not result.tripwire:
            return

        # Priority: JAILBREAK > INJECTION > PII (most severe first)
        if SafetyFlag.JAILBREAK_DETECTED in result.flags:
            code = RejectionReasonCode.JAILBREAK_DETECTED
        elif SafetyFlag.INJECTION_DETECTED in result.flags:
            code = RejectionReasonCode.INJECTION_DETECTED
        else:
            code = RejectionReasonCode.PII_DETECTED

        raise IngressRejected(
            RejectionSlip(
                reason_code=code,
                request_id=request_id,
                trace_root=trace_root,
                message=f"Input safety screen tripped: flags={[f.value for f in result.flags]}",
                gate_stage="E6_SAFETY",
                matched_fragments=result.matched_fragments,
            )
        )

    # ------------------------------------------------------------------ E7
    def _e7_dedup(self, stamped: StampedRequest, trace_root: str) -> None:
        if self._replay_cache.seen_and_mark(stamped.request_id):
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.REPLAY_DUPLICATE,
                    request_id=stamped.request_id,
                    trace_root=trace_root,
                    message=f"Duplicate request_id detected: {stamped.request_id}",
                    gate_stage="E7_DEDUP",
                )
            )

    # ------------------------------------------------------------------ clarify
    @staticmethod
    def _clarify_if_empty_intent(stamped: StampedRequest) -> ClarificationRequired | None:
        payload = stamped.normalized_payload
        if payload is None:
            return ClarificationRequired(
                request_id=stamped.request_id,
                trace_root=stamped.trace_root,
                reason="request_payload is null after normalization.",
                suggested_followups=("Provide a non-null request_payload with intent.",),
            )
        if isinstance(payload, str) and not payload.strip():
            return ClarificationRequired(
                request_id=stamped.request_id,
                trace_root=stamped.trace_root,
                reason="request_payload is empty after normalization.",
                suggested_followups=("Provide non-empty request text describing your intent.",),
            )
        if isinstance(payload, dict):
            intent_fields = ("intent", "query", "prompt", "question", "goal", "task")
            has_intent = any(
                isinstance(payload.get(f), str) and payload.get(f, "").strip() for f in intent_fields
            )
            if not has_intent and not payload:
                return ClarificationRequired(
                    request_id=stamped.request_id,
                    trace_root=stamped.trace_root,
                    reason="request_payload dict is empty.",
                    suggested_followups=(
                        "Include at least one of: intent, query, prompt, question, goal, task.",
                    ),
                )
        return None

    @staticmethod
    def _derive_scope_baseline(env: dict) -> str:
        identity = env.get("caller_identity", "")
        version = env.get("schema_version", "")
        return hashlib.sha256(f"{identity}:{version}".encode()).hexdigest()[:24]

    @staticmethod
    def _derive_auth_verdict(verified: VerifiedIdentity | None, env: dict[str, Any]) -> str:
        """Map E3 verification outcome to spec auth_verdict label.

        Spec values: ``authenticated`` / ``anonymous`` / ``service_bound`` / ``rejected``.
        Rejected paths never reach the stamp (they raise IngressRejected) so this
        only distinguishes the success-path labels.

        Identity preference: the verified caller_id (from the IdentityVerifier)
        is authoritative; the raw envelope value is only used as a fallback when
        no verifier is configured.
        """

        if verified is None:
            return "anonymous"
        identity = str(verified.caller_id or env.get("caller_identity") or "").lower()
        if identity.startswith("svc-") or identity.startswith("service:"):
            return "service_bound"
        if identity.endswith("-anon") or identity in {"anonymous", "anon", "unknown"}:
            return "anonymous"
        return "authenticated"

    @staticmethod
    def _compute_raw_payload_ref(payload: Any) -> str:
        """Stable short content hash of the raw payload (spec output contract).

        We hash the deterministic JSON encoding when possible; otherwise fall
        back to ``repr()``. Output is ``sha256:<24-hex>``.
        """

        try:
            import json as _json

            encoded = _json.dumps(payload, sort_keys=True, default=repr, ensure_ascii=False).encode("utf-8")
        except (TypeError, ValueError):
            encoded = repr(payload).encode("utf-8", errors="replace")
        digest = hashlib.sha256(encoded).hexdigest()[:24]
        return f"sha256:{digest}"


__all__ = [
    "ClarificationRequired",
    "IngressEnvelopeCheck",
    "IngressRejected",
    "RejectionReasonCode",
    "RejectionSlip",
    "StampedRequest",
    "register",
]
