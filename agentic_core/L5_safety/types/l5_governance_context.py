"""L5 Governance Context — canonical cross-child certification binding.

Maps to: docs/reference/00A_L5_Governance_Safety/00A.7a_L5_Governance_Context_Invariant.md

Invariant (00A.7a INV-L5C-1..9):
  For any packet certified by L5, every required per-child certifier
  (Safety, Authority, Origin, Replay/Audit, Static-Gov) and every
  applicable conditionally-required certifier (HITL when execution_form
  is HITL_ONLY, Egress when side_effect_class is EXTERNAL_EGRESS) MUST
  emit the same SHA-256 digest of the same L5GovernanceContext, bit-for-bit.
  Mismatch is fail-closed via
  `agentic_core.L5_safety.enforcement.governance_consistency_gate`.

This module provides:
  - `ExecutionForm`, `RiskTier`, `SideEffectClass`, `CertificationScope` enums
  - `L5GovernanceContext` frozen dataclass (28 fields)
  - `compute_l5_context_digest()` — canonical-JSON SHA-256
  - `L5GovernanceContextField` enum naming every field for mismatch reporting
  - `is_hitl_required()` / `is_egress_required()` applicability helpers

Determinism:
  - `digest()` is canonical (sort_keys, ensure_ascii=False, compact separators).
  - All fields frozen at construction; enum values normalize to .value strings.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class ExecutionForm(str, Enum):
    """Frozen execution form — see 00A.7a Phase 1."""

    L1_ADVISORY = "L1_ADVISORY"
    L2_BOUNDED = "L2_BOUNDED"
    L3_WORKFLOW = "L3_WORKFLOW"
    HITL_ONLY = "HITL_ONLY"


class RiskTier(str, Enum):
    """Frozen risk tier — see config/risk_tier_bands.md."""

    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"


class SideEffectClass(str, Enum):
    """Frozen side-effect class."""

    READ_ONLY = "READ_ONLY"
    TRANSIENT = "TRANSIENT"
    DURABLE = "DURABLE"
    EXTERNAL_EGRESS = "EXTERNAL_EGRESS"


class CertificationScope(str, Enum):
    """Per-child certification scope — names match 00A child files."""

    SAFETY = "SAFETY"
    AUTHORITY = "AUTHORITY"
    ORIGIN = "ORIGIN"
    HITL = "HITL"
    EGRESS = "EGRESS"
    REPLAY_AUDIT = "REPLAY_AUDIT"
    STATIC_GOV = "STATIC_GOV"
    AGGREGATE = "AGGREGATE"


class L5GovernanceContextField(str, Enum):
    """Field names used in mismatch reporting. Names match dataclass fields."""

    REQUEST_ID = "request_id"
    RUN_ID = "run_id"
    TRACE_ID = "trace_id"
    TENANT_ID = "tenant_id"
    PRINCIPAL_ID = "principal_id"
    SESSION_ID = "session_id"
    ROUTE_ID = "route_id"
    STEP_ID = "step_id"
    EXECUTION_FORM = "execution_form"
    RISK_TIER = "risk_tier"
    SIDE_EFFECT_CLASS = "side_effect_class"
    POLICY_HASH = "policy_hash"
    BLUEPRINT_HASH = "blueprint_hash"
    REGISTRY_SNAPSHOT_HASH = "registry_snapshot_hash"
    AGENT_PROFILE_HASH = "agent_profile_hash"
    CAPABILITY_SCOPE_HASH = "capability_scope_hash"
    SANDBOX_ENVELOPE_HASH = "sandbox_envelope_hash"
    ORIGIN_TRUST_MANIFEST_HASH = "origin_trust_manifest_hash"
    EGRESS_PROFILE_HASH = "egress_profile_hash"
    HITL_PACKET_HASH = "hitl_packet_hash"
    RECLEARANCE_HASH = "reclearance_hash"
    REPLAY_ENVELOPE_HASH = "replay_envelope_hash"
    AUDIT_MANIFEST_HASH = "audit_manifest_hash"
    STATIC_GOVERNANCE_SNAPSHOT_HASH = "static_governance_snapshot_hash"
    CERTIFIER_ID = "certifier_id"
    CERTIFIER_VERSION = "certifier_version"
    CERTIFICATION_SCOPE = "certification_scope"
    FROZEN_GOVERNANCE_CONTEXT_HASH = "frozen_governance_context_hash"
    L5_RESOLVER_DIGEST = "l5_resolver_digest"


# Order is significant for canonical JSON serialization. Do NOT reorder.
_DIGEST_FIELD_ORDER: tuple[str, ...] = tuple(f.value for f in L5GovernanceContextField)

# Required-string fields excluded from digest comparison rules. These can be
# legitimately empty: step_id (no L3 step), session_id (anonymous),
# hitl_packet_hash (HITL not applicable), reclearance_hash (no re-clearance),
# egress_profile_hash (no external egress).
_NULLABLE_FIELDS: frozenset[str] = frozenset(
    {
        "step_id",
        "session_id",
        "hitl_packet_hash",
        "reclearance_hash",
        "egress_profile_hash",
    },
)


@dataclass(frozen=True, slots=True)
class L5GovernanceContext:
    """Canonical L5 cross-child governance context — see 00A.7a Phase 1.

    Every L5 child certifier consumes ONE L5GovernanceContext and emits a
    digest of it. The aggregator (00A.8) requires all per-child digests to
    match before issuing aggregate_governance_digest.

    Forbidden patterns (enforced upstream by the consistency gate):
      - Mutating any field after construction (frozen=True, slots=True).
      - Re-resolving a binding field inside a child certifier (drives
        widening — caught as a mismatch by the gate).
      - Emitting a conditionally-required digest when its trigger is not
        active, or omitting one when the trigger IS active.
    """

    # Identity
    request_id: str
    run_id: str
    trace_id: str
    tenant_id: str
    principal_id: str
    session_id: str  # may be empty for anonymous sessions

    # Routing / execution scope
    route_id: str
    step_id: str  # may be empty when no L3 step
    execution_form: ExecutionForm
    risk_tier: RiskTier
    side_effect_class: SideEffectClass

    # Authority / policy / registry surface
    policy_hash: str
    blueprint_hash: str
    registry_snapshot_hash: str
    agent_profile_hash: str
    capability_scope_hash: str
    sandbox_envelope_hash: str

    # Trust / egress / human-input surface
    origin_trust_manifest_hash: str
    egress_profile_hash: str  # may be empty when not EXTERNAL_EGRESS
    hitl_packet_hash: str  # may be empty when HITL not applicable
    reclearance_hash: str  # may be empty when no re-clearance

    # Certification evidence surface
    replay_envelope_hash: str
    audit_manifest_hash: str
    static_governance_snapshot_hash: str

    # Certifier identity
    certifier_id: str
    certifier_version: str
    certification_scope: CertificationScope

    # Frozen-context surface
    frozen_governance_context_hash: str
    l5_resolver_digest: str

    def __post_init__(self) -> None:
        # Required strings — non-empty unless in _NULLABLE_FIELDS
        raw = asdict(self)
        for name in _DIGEST_FIELD_ORDER:
            value = raw[name]
            if name in _NULLABLE_FIELDS:
                if not isinstance(value, str):
                    raise TypeError(
                        f"L5GovernanceContext.{name} must be a string (may be ''); "
                        f"got {type(value).__name__}"
                    )
                continue
            if name == "execution_form":
                if not isinstance(self.execution_form, ExecutionForm):
                    raise TypeError(
                        "L5GovernanceContext.execution_form must be an ExecutionForm enum; "
                        f"got {type(self.execution_form).__name__}"
                    )
                continue
            if name == "risk_tier":
                if not isinstance(self.risk_tier, RiskTier):
                    raise TypeError(
                        "L5GovernanceContext.risk_tier must be a RiskTier enum; "
                        f"got {type(self.risk_tier).__name__}"
                    )
                continue
            if name == "side_effect_class":
                if not isinstance(self.side_effect_class, SideEffectClass):
                    raise TypeError(
                        "L5GovernanceContext.side_effect_class must be a SideEffectClass enum; "
                        f"got {type(self.side_effect_class).__name__}"
                    )
                continue
            if name == "certification_scope":
                if not isinstance(self.certification_scope, CertificationScope):
                    raise TypeError(
                        "L5GovernanceContext.certification_scope must be a "
                        f"CertificationScope enum; got {type(self.certification_scope).__name__}"
                    )
                continue
            if not isinstance(value, str) or value == "":
                raise ValueError(
                    f"L5GovernanceContext.{name} must be a non-empty string; "
                    f"resolver_digest={self.l5_resolver_digest!r}"
                )

        # Conditional applicability checks
        if self.is_hitl_required() and self.hitl_packet_hash == "":
            raise ValueError(
                "L5GovernanceContext.hitl_packet_hash must be non-empty when "
                f"execution_form={self.execution_form.value}"
            )
        if self.is_egress_required() and self.egress_profile_hash == "":
            raise ValueError(
                "L5GovernanceContext.egress_profile_hash must be non-empty when "
                f"side_effect_class={self.side_effect_class.value}"
            )

    # ------------------------------------------------------------------ #
    # Applicability helpers (00A.7a Phase 3)
    # ------------------------------------------------------------------ #

    def is_hitl_required(self) -> bool:
        """True when HITL re-clearance digest MUST be emitted."""
        return self.execution_form is ExecutionForm.HITL_ONLY

    def is_egress_required(self) -> bool:
        """True when Egress certification digest MUST be emitted."""
        return self.side_effect_class is SideEffectClass.EXTERNAL_EGRESS

    # ------------------------------------------------------------------ #
    # Canonical serialization + digest
    # ------------------------------------------------------------------ #

    def to_canonical_dict(self) -> dict[str, Any]:
        """Return the deterministic dict used for digest computation.

        Field order is fixed by `_DIGEST_FIELD_ORDER`. Enums serialize as
        their `.value` strings.
        """
        raw = asdict(self)
        canonical: dict[str, Any] = {}
        for name in _DIGEST_FIELD_ORDER:
            value = raw[name]
            if isinstance(value, Enum):
                canonical[name] = value.value
            else:
                canonical[name] = value
        return canonical

    def digest(self) -> str:
        """Stable SHA-256 hex digest of the canonical representation."""
        return compute_l5_context_digest(self)

    def first_mismatched_field(self, other: L5GovernanceContext) -> str:
        """Return the first field name that differs between self and other.

        Returns "" when self and other agree on every field. Field order
        matches `_DIGEST_FIELD_ORDER` so the answer is deterministic.
        """
        a = self.to_canonical_dict()
        b = other.to_canonical_dict()
        for name in _DIGEST_FIELD_ORDER:
            if a[name] != b[name]:
                return name
        return ""


def compute_l5_context_digest(ctx: L5GovernanceContext) -> str:
    """Compute the canonical SHA-256 digest of an L5GovernanceContext."""
    canonical = ctx.to_canonical_dict()
    body = json.dumps(
        canonical,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


__all__ = [
    "CertificationScope",
    "ExecutionForm",
    "L5GovernanceContext",
    "L5GovernanceContextField",
    "RiskTier",
    "SideEffectClass",
    "compute_l5_context_digest",
]
