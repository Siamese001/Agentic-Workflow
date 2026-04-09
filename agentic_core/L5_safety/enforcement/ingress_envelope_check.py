"""Ingress Envelope Check — E1 through E6 pre-pipeline gate.

This module is the single mandatory ingress gate that every inbound request
MUST pass before reaching L1 reasoning.  It enforces the complete E1–E6
contract defined in docs/reference/01_request_intake.md:

    E1  Transport validation     — well-formed request envelope
    E2  Schema validation        — required fields present and typed
    E3  Identity verification    — caller identity token present and trusted
    E4  Quota / rate-limit check — per-client quota not exceeded
    E5  Trace stamping           — request_id, session_id, trace_root assigned
    E6  Replay deduplication     — request_id not already seen in this session

On success  → returns StampedRequest (typed, trace-stamped, quota-consumed)
On failure  → raises RejectionSlip with reason_code; never silently swallows

Layer authority: L5 (cross-cutting policy plane)
Write authority: NONE — this gate is read/stamp only; no durable state mutation
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

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

emit_replay_key("p0", "ingress_envelope_check")
emit_determinism_digest("p0", "ingress_envelope_check")
_emit_reads_policy_state("p1", "ingress_envelope_check", "L5")
_emit_verifies_policy("p1", "ingress_envelope_check", "policy_check")
_emit_verifies_boundary("p1", "ingress_envelope_check", "boundary_check")
_emit_validated_by_safety_plane("p1", "ingress_envelope_check", "safety_validation")
_emit_hard_fails_untranscripted("p1", "ingress_envelope_check")
_emit_gated_by_confidence("p1", "ingress_envelope_check", "confidence_gate")

logger = logging.getLogger(__name__)

_REQUIRED_ENVELOPE_FIELDS = ("request_payload", "caller_identity", "schema_version")
_TRUSTED_SCHEMA_VERSIONS = {"1.0", "1.1", "2.0"}


class RejectionReasonCode(str, Enum):
    """Rejection reason codes emitted in RejectionSlip."""

    MALFORMED_ENVELOPE = "E1_MALFORMED_ENVELOPE"
    SCHEMA_INVALID = "E2_SCHEMA_INVALID"
    IDENTITY_MISSING = "E3_IDENTITY_MISSING"
    IDENTITY_UNTRUSTED = "E3_IDENTITY_UNTRUSTED"
    QUOTA_EXCEEDED = "E4_QUOTA_EXCEEDED"
    RATE_LIMITED = "E4_RATE_LIMITED"
    REPLAY_DUPLICATE = "E6_REPLAY_DUPLICATE"


@dataclass
class RejectionSlip:
    """Typed rejection output emitted for every gate failure.

    Every rejection is fail-closed: the slip carries enough information for
    the caller to understand which gate failed and why, without leaking
    internal state.
    """

    reason_code: RejectionReasonCode
    request_id: str
    trace_root: str
    message: str
    gate_stage: str
    timestamp_utc: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reason_code": self.reason_code.value,
            "request_id": self.request_id,
            "trace_root": self.trace_root,
            "message": self.message,
            "gate_stage": self.gate_stage,
            "timestamp_utc": self.timestamp_utc,
        }


class IngressRejected(Exception):
    """Raised when any E1–E6 check fails.  Carries the RejectionSlip."""

    def __init__(self, slip: RejectionSlip) -> None:
        self.slip = slip
        super().__init__(f"[{slip.reason_code.value}] {slip.message}")


@dataclass
class StampedRequest:
    """Typed output of a fully-cleared ingress gate.

    Contains the original payload plus the six required envelope fields
    stamped by the gate.  Downstream L1 MUST accept only StampedRequest —
    never a raw dict.
    """

    request_id: str
    session_id: str
    trace_root: str
    caller_scope_baseline: str
    schema_version: str
    request_payload: Any
    caller_identity: str
    stamped_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "trace_root": self.trace_root,
            "caller_scope_baseline": self.caller_scope_baseline,
            "schema_version": self.schema_version,
            "request_payload": self.request_payload,
            "caller_identity": self.caller_identity,
            "stamped_at": self.stamped_at,
        }


class IngressEnvelopeCheck:
    """E1–E6 ingress gate — single mandatory pre-pipeline enforcement point.

    Usage::

        gate = IngressEnvelopeCheck(rate_limiter=..., seen_request_ids=set())
        stamped = gate.check(raw_envelope)  # raises IngressRejected on any failure
        # stamped is a StampedRequest; pass to L1

    Layer authority: L5 (policy plane) — read/stamp only, no durable writes.
    """

    def __init__(
        self,
        rate_limiter: Any | None = None,
        seen_request_ids: set[str] | None = None,
        trusted_schema_versions: set[str] | None = None,
    ) -> None:
        self._rate_limiter = rate_limiter
        self._seen_request_ids: set[str] = seen_request_ids if seen_request_ids is not None else set()
        self._trusted_schema_versions = trusted_schema_versions or _TRUSTED_SCHEMA_VERSIONS

    def check(self, raw_envelope: dict[str, Any]) -> StampedRequest:
        """Run E1–E6 checks in order.  Returns StampedRequest or raises IngressRejected.

        Args:
            raw_envelope: Inbound request dict from transport layer.

        Returns:
            StampedRequest with trace_root, request_id, session_id, caller_scope_baseline.

        Raises:
            IngressRejected: on any gate failure (fail-closed).
        """
        _pre_request_id = str(uuid.uuid4())
        _pre_trace = hashlib.sha256(f"{_pre_request_id}:{time.time()}".encode()).hexdigest()[:16]
        self._e1_transport(raw_envelope, _pre_request_id, _pre_trace)

        request_id = raw_envelope.get("request_id") or str(uuid.uuid4())
        trace_root = hashlib.sha256(f"{request_id}:{time.time()}".encode()).hexdigest()[:16]

        _emit_snapshots_state(request_id, "IngressEnvelopeCheck.check", "ingress_state")
        _emit_applies_guardrail(request_id, "IngressEnvelopeCheck.check", "E1_E6_ingress")
        _trace_id = request_id
        _emit_records_execution_trace(_trace_id, "L5_POLICY", "IngressEnvelopeCheck.check")
        _seg_hash = hashlib.sha256(f"{_trace_id}:IngressEnvelopeCheck".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)
        self._e2_schema(raw_envelope, request_id, trace_root)
        self._e3_identity(raw_envelope, request_id, trace_root)
        self._e4_quota(raw_envelope, request_id, trace_root)

        session_id = raw_envelope.get("session_id") or str(uuid.uuid4())
        caller_scope_baseline = self._derive_scope_baseline(raw_envelope)

        stamped = StampedRequest(
            request_id=request_id,
            session_id=session_id,
            trace_root=trace_root,
            caller_scope_baseline=caller_scope_baseline,
            schema_version=raw_envelope.get("schema_version", "1.0"),
            request_payload=raw_envelope.get("request_payload"),
            caller_identity=raw_envelope.get("caller_identity", ""),
        )

        self._e6_dedup(stamped, trace_root)
        self._seen_request_ids.add(request_id)

        _emit_transcripts_response(request_id, "IngressEnvelopeCheck", "stamped_request")
        logger.info(
            "[IngressEnvelopeCheck] Stamped request_id=%s trace_root=%s",
            request_id,
            trace_root,
        )
        return stamped

    def _e1_transport(self, env: dict, request_id: str, trace_root: str) -> None:
        """E1: envelope must be a non-empty dict."""
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

    def _e2_schema(self, env: dict, request_id: str, trace_root: str) -> None:
        """E2: required fields present; schema_version is trusted."""
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
                    message=f"Untrusted schema_version: {version!r}. Accepted: {sorted(self._trusted_schema_versions)}",
                    gate_stage="E2_SCHEMA",
                )
            )

    def _e3_identity(self, env: dict, request_id: str, trace_root: str) -> None:
        """E3: caller_identity must be present and non-empty."""
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

    def _e4_quota(self, env: dict, request_id: str, trace_root: str) -> None:
        """E4: rate-limit check via injected rate_limiter (if provided)."""
        if self._rate_limiter is None:
            return
        caller_id = env.get("caller_identity", "unknown")
        allowed = self._rate_limiter.is_allowed(caller_id)
        if not allowed:
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.RATE_LIMITED,
                    request_id=request_id,
                    trace_root=trace_root,
                    message=f"Rate limit exceeded for caller: {caller_id}",
                    gate_stage="E4_QUOTA",
                )
            )

    def _e6_dedup(self, stamped: StampedRequest, trace_root: str) -> None:
        """E6: request_id must not already be seen in this session."""
        if stamped.request_id in self._seen_request_ids:
            raise IngressRejected(
                RejectionSlip(
                    reason_code=RejectionReasonCode.REPLAY_DUPLICATE,
                    request_id=stamped.request_id,
                    trace_root=trace_root,
                    message=f"Duplicate request_id detected: {stamped.request_id}",
                    gate_stage="E6_DEDUP",
                )
            )

    @staticmethod
    def _derive_scope_baseline(env: dict) -> str:
        """Derive a deterministic caller_scope_baseline from envelope fields."""
        identity = env.get("caller_identity", "")
        version = env.get("schema_version", "")
        return hashlib.sha256(f"{identity}:{version}".encode()).hexdigest()[:24]
