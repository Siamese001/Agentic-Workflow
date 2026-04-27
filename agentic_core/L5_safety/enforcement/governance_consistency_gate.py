"""L5 Governance Consistency Gate — cross-child digest equality enforcement.

Maps to: docs/reference/00A_L5_Governance_Safety/00A.7a_L5_Governance_Context_Invariant.md

This module is the single chokepoint enforcing INV-L5C-1..9 from 00A.7a.
It is pure: no I/O, no logging side effects beyond the explicit OTEL
emission (which goes through `agentic_core.L5_safety.v5.governance_spans`),
no HITL, no durable write.

Public surface:
  - `L5GovernanceContextMismatchError` — raised on any mismatch
  - `assert_l5_cross_child_match` — the gate function
  - `L5_GOVERNANCE_CONTEXT_MISMATCH_RULE_ID` — re-exported constant

Behavior:
  1. Reject if any required per-child digest is empty or malformed.
  2. Reject if a conditionally-required digest is missing when its
     trigger is active (HITL when execution_form=HITL_ONLY, Egress when
     side_effect_class=EXTERNAL_EGRESS).
  3. Reject if a conditionally-required digest is present when its
     trigger is NOT active (conditional_digest_unexpected).
  4. Reject if any required-or-applicable digest != l5_context_digest
     (bit-for-bit, no substring).
  5. Defense-in-depth: per-child contexts must agree field-wise.
"""

from __future__ import annotations

import re
import uuid

from agentic_core.L5_safety.types.l5_certification_evidence import (
    L5_GOVERNANCE_CONTEXT_MISMATCH_RULE_ID,
    L5CertificationEvidence,
    L5GovernanceContextMismatchError,
    ParticipatingDigests,
)
from agentic_core.L5_safety.types.l5_governance_context import (
    L5GovernanceContext,
)

_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")


def _looks_like_digest(value: str) -> bool:
    return isinstance(value, str) and bool(_HEX64_RE.match(value))


def _build_evidence(
    *,
    canonical_context: L5GovernanceContext,
    participating: ParticipatingDigests,
    first_mismatched_field: str,
    reason: str,
) -> L5CertificationEvidence:
    return L5CertificationEvidence(
        decisive_rule_id=L5_GOVERNANCE_CONTEXT_MISMATCH_RULE_ID,
        certified=False,
        certification_scope="AGGREGATE",
        first_mismatched_field=first_mismatched_field,
        participating_digests=participating,
        trace_id=canonical_context.trace_id,
        request_id=canonical_context.request_id,
        run_id=canonical_context.run_id,
        route_id=canonical_context.route_id,
        step_id=canonical_context.step_id,
        tenant_id=canonical_context.tenant_id,
        principal_id=canonical_context.principal_id,
        sealed_evidence_id=f"l5-evid-{uuid.uuid4().hex}",
        reason=reason,
        downstream_recommendation="deny",
        dispatch_target="EXIT_CONTROL",
    )


def assert_l5_cross_child_match(
    *,
    canonical_context: L5GovernanceContext,
    safety_enforcement_digest: str,
    authority_binding_digest: str,
    origin_trust_digest: str,
    replay_audit_digest: str,
    static_governance_digest: str,
    hitl_reclearance_digest: str = "",
    egress_certification_digest: str = "",
) -> str:
    """Raise `L5GovernanceContextMismatchError` unless every INV-L5C-* holds.

    On success returns the canonical aggregate_governance_digest (the digest
    of the canonical_context, which every per-child digest must equal).

    All keyword-only so callers cannot accidentally swap children.
    """
    # The single equality anchor that every required/applicable child must equal.
    canonical_digest = canonical_context.digest()

    # Snapshot for evidence (filled in regardless of outcome)
    participating = ParticipatingDigests(
        safety_enforcement_digest=safety_enforcement_digest,
        authority_binding_digest=authority_binding_digest,
        origin_trust_digest=origin_trust_digest,
        hitl_reclearance_digest=hitl_reclearance_digest,
        egress_certification_digest=egress_certification_digest,
        replay_audit_digest=replay_audit_digest,
        static_governance_digest=static_governance_digest,
        aggregate_governance_digest="",
    )

    # 1. Required digest format
    required_pairs: tuple[tuple[str, str], ...] = (
        ("safety_enforcement_digest", safety_enforcement_digest),
        ("authority_binding_digest", authority_binding_digest),
        ("origin_trust_digest", origin_trust_digest),
        ("replay_audit_digest", replay_audit_digest),
        ("static_governance_digest", static_governance_digest),
    )
    for name, value in required_pairs:
        if not _looks_like_digest(value):
            raise L5GovernanceContextMismatchError(
                _build_evidence(
                    canonical_context=canonical_context,
                    participating=participating,
                    first_mismatched_field=name,
                    reason=f"{name} is not a 64-char hex SHA-256",
                )
            )

    # 2. Conditional applicability — required-but-missing
    if canonical_context.is_hitl_required():
        if not _looks_like_digest(hitl_reclearance_digest):
            raise L5GovernanceContextMismatchError(
                _build_evidence(
                    canonical_context=canonical_context,
                    participating=participating,
                    first_mismatched_field="hitl_reclearance_digest",
                    reason=(
                        "hitl_reclearance_digest required when "
                        f"execution_form={canonical_context.execution_form.value}"
                    ),
                )
            )
    else:
        # 3. Conditional applicability — present-but-not-allowed
        if hitl_reclearance_digest != "":
            raise L5GovernanceContextMismatchError(
                _build_evidence(
                    canonical_context=canonical_context,
                    participating=participating,
                    first_mismatched_field="hitl_reclearance_digest",
                    reason=(
                        "hitl_reclearance_digest must be empty when "
                        f"execution_form={canonical_context.execution_form.value} "
                        "(conditional_digest_unexpected)"
                    ),
                )
            )

    if canonical_context.is_egress_required():
        if not _looks_like_digest(egress_certification_digest):
            raise L5GovernanceContextMismatchError(
                _build_evidence(
                    canonical_context=canonical_context,
                    participating=participating,
                    first_mismatched_field="egress_certification_digest",
                    reason=(
                        "egress_certification_digest required when "
                        f"side_effect_class={canonical_context.side_effect_class.value}"
                    ),
                )
            )
    else:
        if egress_certification_digest != "":
            raise L5GovernanceContextMismatchError(
                _build_evidence(
                    canonical_context=canonical_context,
                    participating=participating,
                    first_mismatched_field="egress_certification_digest",
                    reason=(
                        "egress_certification_digest must be empty when "
                        f"side_effect_class={canonical_context.side_effect_class.value} "
                        "(conditional_digest_unexpected)"
                    ),
                )
            )

    # 4. Equality (INV-L5C-1, bit-for-bit) against the canonical digest
    equality_pairs: list[tuple[str, str]] = [
        ("safety_enforcement_digest", safety_enforcement_digest),
        ("authority_binding_digest", authority_binding_digest),
        ("origin_trust_digest", origin_trust_digest),
        ("replay_audit_digest", replay_audit_digest),
        ("static_governance_digest", static_governance_digest),
    ]
    if canonical_context.is_hitl_required():
        equality_pairs.append(("hitl_reclearance_digest", hitl_reclearance_digest))
    if canonical_context.is_egress_required():
        equality_pairs.append(("egress_certification_digest", egress_certification_digest))

    for name, value in equality_pairs:
        if value != canonical_digest:
            raise L5GovernanceContextMismatchError(
                _build_evidence(
                    canonical_context=canonical_context,
                    participating=participating,
                    first_mismatched_field=name,
                    reason=f"{name} != l5_context_digest",
                )
            )

    # All checks passed. Return the canonical aggregate digest.
    return canonical_digest


__all__ = [
    "L5_GOVERNANCE_CONTEXT_MISMATCH_RULE_ID",
    "L5GovernanceContextMismatchError",
    "assert_l5_cross_child_match",
]
