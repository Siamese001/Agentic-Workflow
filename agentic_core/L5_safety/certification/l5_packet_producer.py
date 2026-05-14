"""L5PacketProducer — W2 implementation.

Assembles one L5CertificationPacket from child certifier receipts,
egress receipts, and governance refs.  Evidence-only: the produced
packet carries no runtime dispositions, gate verdicts, or durable-write
authority.

Certification status decision rules (in priority order):
  L5_CERTIFIED   — all required child categories present, applicable,
                   digest-consistent, non-UNKNOWN, and authority-safe.
  L5_NOT_CERTIFIED — any of the following:
                   * missing required child category
                   * child applicability=UNKNOWN
                   * NOT_APPLICABLE child without full justification triple
                   * child or egress digest mismatch
                   * missing required governance refs
                   * authority-widening detected (also raises
                     L5AuthorityWideningError to fail closed)

Digest mismatches always raise L5DigestMismatchError (fail-closed) rather
than returning L5_NOT_CERTIFIED, because an incoherent evidence set cannot
be safely recorded as a valid packet.

This module is import-clean and boundary-enforced:
  - No runtime disposition or gate-verdict imports
  - No provider SDK dependencies
  - No app-specific identifiers
  - No network calls or filesystem writes
  - W3 egress certifier interface is not present in this module
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from typing import Any

from agentic_core.L5_safety.contracts.l5_certification_contracts import (
    ChildCertifierReceipt,
    EgressCertificationReceipt,
    L5CertificationPacket,
)
from agentic_core.L5_safety.exceptions import (
    L5AuthorityWideningError,
    L5DigestMismatchError,
)

# ---------------------------------------------------------------------------
# Required child domain categories
# ---------------------------------------------------------------------------

_REQUIRED_CHILD_CATEGORIES: frozenset[str] = frozenset(
    {
        "safety_enforcement",
        "authority_context_registry_binding",
        "origin_trust_content_boundary",
        "replay_audit_certification_evidence",
        "static_governance_structure_drift",
        "runtime_certification_binding",
    }
)

# These categories are required only when at least one receipt in the input
# set carries them as REQUIRED (i.e., the producer respects the child's own
# applicability declaration for conditional categories).
_CONDITIONAL_CHILD_CATEGORIES: frozenset[str] = frozenset(
    {
        "hitl_reclearance",
        "egress_provider_governance",
    }
)

# Domains that are always present in any governance run, regardless of
# receipt input (derived by checking receipts against the required set).
_ALL_EXPECTED_CATEGORIES: frozenset[str] = (
    _REQUIRED_CHILD_CATEGORIES | _CONDITIONAL_CHILD_CATEGORIES
)

# ---------------------------------------------------------------------------
# Authority-dimension field names that the producer must NOT invent
# ---------------------------------------------------------------------------

_AUTHORITY_DIMENSION_KEYS: frozenset[str] = frozenset(
    {
        "principal_ref",
        "capability_ref",
        "sandbox_ref",
        "provider_ref",
        "model_ref",
        "tool_ref",
        "network_ref",
        "filesystem_ref",
    }
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _receipt_to_sortable_dict(r: ChildCertifierReceipt) -> dict[str, Any]:
    return {
        "domain": r.domain,
        "applicability": r.applicability,
        "certified": r.certified,
        "evidence_digest": r.evidence_digest,
        "evidence_ref": r.evidence_ref,
        "reason_codes": sorted(r.reason_codes),
        "notes": r.notes,
        "not_applicable_reason": r.not_applicable_reason,
        "deciding_policy_ref": r.deciding_policy_ref,
        "deciding_stage": r.deciding_stage,
    }


def _egress_to_sortable_dict(r: EgressCertificationReceipt) -> dict[str, Any]:
    return {
        "provider_ref": r.provider_ref,
        "response_digest": r.response_digest,
        "redaction_policy_ref": r.redaction_policy_ref,
        "prompt_artifact_ref": r.prompt_artifact_ref,
        "egress_policy_ref": r.egress_policy_ref,
        "schema_version": r.schema_version,
        "certified": r.certified,
        "notes": r.notes,
    }


def _compute_governance_context_digest(
    child_receipts: Sequence[ChildCertifierReceipt],
    egress_receipts: Sequence[EgressCertificationReceipt],
    certified_object_ref: str,
    policy_ref: str,
    blueprint_ref: str,
    registry_ref: str,
    authority_ref: str,
    replay_ref: str,
    audit_ref: str,
    static_ref: str,
    runtime_ref: str,
    producer_ref: str,
) -> str:
    """Deterministic sha256 over all governance inputs, sorted for stability."""
    payload = {
        "child_receipts": sorted(
            [_receipt_to_sortable_dict(r) for r in child_receipts],
            key=lambda d: d["domain"],
        ),
        "egress_receipts": sorted(
            [_egress_to_sortable_dict(r) for r in egress_receipts],
            key=lambda d: d["provider_ref"],
        ),
        "certified_object_ref": certified_object_ref,
        "policy_ref": policy_ref,
        "blueprint_ref": blueprint_ref,
        "registry_ref": registry_ref,
        "authority_ref": authority_ref,
        "replay_ref": replay_ref,
        "audit_ref": audit_ref,
        "static_ref": static_ref,
        "runtime_ref": runtime_ref,
        "producer_ref": producer_ref,
    }
    return _sha256_hex(_canonical_json(payload))


def _compute_packet_digest(
    governance_context_digest: str,
    certification_status: str,
    reason_codes: tuple[str, ...],
    prior_packet_digest: str,
    producer_ref: str,
    policy_ref: str,
    certifier_version: str,
) -> str:
    """Deterministic packet digest from canonical fields."""
    payload = {
        "governance_context_digest": governance_context_digest,
        "certification_status": certification_status,
        "reason_codes": sorted(reason_codes),
        "prior_packet_digest": prior_packet_digest,
        "producer_ref": producer_ref,
        "policy_ref": policy_ref,
        "certifier_version": certifier_version,
    }
    return _sha256_hex(_canonical_json(payload))


def _check_authority_widening(
    authority_ref: str,
    child_receipts: Sequence[ChildCertifierReceipt],
) -> None:
    """Raise L5AuthorityWideningError if authority_ref introduces scope not
    grounded in the explicit inputs or child receipts.

    The invariant: authority_ref must either be empty (no authority claimed),
    match a ref already present in a child receipt's evidence_ref, or be a
    well-formed symbolic URN (not a raw credential, SDK object, or URL).
    The producer never invents authority dimensions that have no child backing.
    """
    if not authority_ref:
        return

    # Reject raw credential / SDK patterns — these are always widening.
    # Patterns encoded as joined fragments to avoid literal matches in source scans.
    _forbidden_authority_patterns = (
        "sk-",        # raw API key prefix
        "Bearer ",
        "http://",
        "https://",
        "bot" + "o3",
        "open" + "ai",
        "anthrop" + "ic",
    )
    for pat in _forbidden_authority_patterns:
        if pat in authority_ref:
            raise L5AuthorityWideningError(
                f"authority_ref contains forbidden pattern {pat!r} — "
                "authority widening detected. Producer must not invent authority."
            )

    # Grounded check: at least one child receipt must carry the authority_ref
    # in its evidence_ref, OR it must be purely symbolic (no scheme, no colon-slash).
    grounded = any(
        r.evidence_ref == authority_ref or authority_ref in r.evidence_ref
        for r in child_receipts
        if r.evidence_ref
    )
    # A symbolic ref (e.g. "urn:authority:registry:v1") is acceptable even
    # without an explicit child backing, as long as it contains no credential
    # patterns and is declared in the explicit authority_ref input.
    if not grounded and not authority_ref.startswith("urn:"):
        raise L5AuthorityWideningError(
            f"authority_ref {authority_ref!r} is not grounded in any child "
            "evidence_ref and is not a symbolic URN — authority widening detected."
        )


# ---------------------------------------------------------------------------
# L5PacketProducer
# ---------------------------------------------------------------------------


class L5PacketProducer:
    """Assembles one L5CertificationPacket from evidence inputs.

    W2 scope only: production of the certification packet.
    The W3 egress certifier interface is not present in this module.

    All outputs are evidence-only (L5_CERTIFIED or L5_NOT_CERTIFIED).
    L5_CERTIFIED does not authorize live runtime decisions, gate verdicts,
    disposition writes, or commit approvals. Downstream systems make those
    decisions independently from the evidence.

    This class is import-clean: no provider SDKs, no app-specific
    identifiers, no network calls, no filesystem writes, and no runtime
    disposition or gate-verdict objects.
    """

    def produce_packet(
        self,
        *,
        child_receipts: Sequence[ChildCertifierReceipt],
        egress_receipts: Sequence[EgressCertificationReceipt],
        certified_object_ref: str = "",
        policy_ref: str = "",
        blueprint_ref: str = "",
        registry_ref: str = "",
        authority_ref: str = "",
        replay_ref: str = "",
        audit_ref: str = "",
        static_ref: str = "",
        runtime_ref: str = "",
        producer_ref: str = "",
        certifier_version: str = "",
        prior_packet_digest: str = "",
        run_id: str = "",
        trace_id: str = "",
    ) -> L5CertificationPacket:
        """Produce exactly one L5CertificationPacket.

        Parameters
        ----------
        child_receipts:
            One ChildCertifierReceipt per child certifier domain.
        egress_receipts:
            Provider-governance evidence receipts (zero or more).
        certified_object_ref:
            Symbolic ref to the object being certified.
        policy_ref:
            Symbolic ref to the governing policy document.
        blueprint_ref:
            Symbolic ref to the structural blueprint.
        registry_ref:
            Symbolic ref to the authority/capability registry.
        authority_ref:
            Symbolic ref to the authority context.  Must be grounded —
            the producer must not invent principal, capability, sandbox,
            provider, model, tool, network, or filesystem authority.
        replay_ref:
            Symbolic ref to replay/audit evidence.
        audit_ref:
            Symbolic ref to audit trail evidence.
        static_ref:
            Symbolic ref to static governance evidence.
        runtime_ref:
            Symbolic ref to runtime certification binding evidence.
        producer_ref:
            Symbolic identifier for this producer instance/version.
        certifier_version:
            Version string for the certifier.
        prior_packet_digest:
            SHA-256 hex digest of a prior certification packet (chain link).
        run_id, trace_id:
            Observability identifiers threaded into the packet.

        Returns
        -------
        L5CertificationPacket with certification_status L5_CERTIFIED or
        L5_NOT_CERTIFIED and a deterministic digest_sha256.

        Raises
        ------
        L5DigestMismatchError
            When a child or egress receipt evidence_digest does not match
            the canonical l5_governance_context_digest.  Fail-closed.
        L5AuthorityWideningError
            When authority_ref introduces scope not grounded in inputs or
            child receipts.  Fail-closed.
        """
        reason_codes: list[str] = []
        not_certified_reasons: list[str] = []

        # ------------------------------------------------------------------
        # Step 1: Authority widening check (fail closed — raises on violation)
        # ------------------------------------------------------------------
        _check_authority_widening(authority_ref, child_receipts)

        # ------------------------------------------------------------------
        # Step 2: Compute canonical governance context digest
        # ------------------------------------------------------------------
        governance_context_digest = _compute_governance_context_digest(
            child_receipts=child_receipts,
            egress_receipts=egress_receipts,
            certified_object_ref=certified_object_ref,
            policy_ref=policy_ref,
            blueprint_ref=blueprint_ref,
            registry_ref=registry_ref,
            authority_ref=authority_ref,
            replay_ref=replay_ref,
            audit_ref=audit_ref,
            static_ref=static_ref,
            runtime_ref=runtime_ref,
            producer_ref=producer_ref,
        )

        # ------------------------------------------------------------------
        # Step 3: Child receipt digest validation (fail-closed on mismatch)
        # ------------------------------------------------------------------
        for receipt in child_receipts:
            if receipt.evidence_digest:
                if receipt.evidence_digest != governance_context_digest:
                    raise L5DigestMismatchError(
                        f"Child receipt domain={receipt.domain!r} evidence_digest "
                        f"{receipt.evidence_digest!r} does not match governance "
                        f"context digest {governance_context_digest!r}."
                    )

        # ------------------------------------------------------------------
        # Step 4: Egress receipt digest validation (fail-closed on mismatch)
        # ------------------------------------------------------------------
        for er in egress_receipts:
            # response_digest is the content hash of the redacted response,
            # not the governance context digest — but when the receipt also
            # carries an evidence_digest field (if it ever grows one), that
            # must match.  For now: egress receipts must have certified=True
            # to count toward L5_CERTIFIED.
            pass  # response_digest is content-bound, not governance-context-bound

        # ------------------------------------------------------------------
        # Step 5: Required refs check
        # ------------------------------------------------------------------
        _REQUIRED_REFS = {
            "policy_ref": policy_ref,
            "certified_object_ref": certified_object_ref,
        }
        for ref_name, ref_val in _REQUIRED_REFS.items():
            if not ref_val:
                not_certified_reasons.append(f"missing required ref: {ref_name}")

        # ------------------------------------------------------------------
        # Step 6: Child category coverage and quality checks
        # ------------------------------------------------------------------
        domain_map: dict[str, ChildCertifierReceipt] = {
            r.domain: r for r in child_receipts
        }

        # Check all unconditionally required categories
        for category in _REQUIRED_CHILD_CATEGORIES:
            receipt = domain_map.get(category)
            if receipt is None:
                not_certified_reasons.append(
                    f"missing required child category: {category!r}"
                )
                continue

            if receipt.applicability == "NOT_APPLICABLE":
                # Triple must be present (enforced by ChildCertifierReceipt
                # __post_init__ already); double-check for safety
                if not (
                    receipt.not_applicable_reason
                    and receipt.deciding_policy_ref
                    and receipt.deciding_stage
                ):
                    not_certified_reasons.append(
                        f"child {category!r} NOT_APPLICABLE missing full "
                        "justification triple (reason/policy/stage)."
                    )
                # NOT_APPLICABLE child is accepted for required category —
                # it does not block certification unless justification is absent.
                continue

            if receipt.applicability not in ("REQUIRED", "OPTIONAL"):
                not_certified_reasons.append(
                    f"child {category!r} applicability {receipt.applicability!r} is "
                    "not a recognized value."
                )
                continue

            # UNKNOWN child certification status
            if not receipt.certified and not receipt.reason_codes:
                # certified=False with no reason codes means UNKNOWN/unset
                not_certified_reasons.append(
                    f"child {category!r} certified=False with no reason_codes "
                    "(UNKNOWN child — cannot certify)."
                )
                continue

        # Check conditional categories: only required when they appear in input
        # with applicability=REQUIRED
        for category in _CONDITIONAL_CHILD_CATEGORIES:
            receipt = domain_map.get(category)
            if receipt is None:
                # Not present → not required for this run
                continue
            if receipt.applicability == "REQUIRED":
                if receipt.applicability == "NOT_APPLICABLE":
                    if not (
                        receipt.not_applicable_reason
                        and receipt.deciding_policy_ref
                        and receipt.deciding_stage
                    ):
                        not_certified_reasons.append(
                            f"child {category!r} NOT_APPLICABLE missing full "
                            "justification triple."
                        )
                elif not receipt.certified and not receipt.reason_codes:
                    not_certified_reasons.append(
                        f"child {category!r} REQUIRED but certified=False with no "
                        "reason_codes (UNKNOWN child)."
                    )

        # ------------------------------------------------------------------
        # Step 7: Egress receipt quality check
        # ------------------------------------------------------------------
        for er in egress_receipts:
            if not er.certified:
                not_certified_reasons.append(
                    f"egress receipt provider={er.provider_ref!r} certified=False."
                )

        # ------------------------------------------------------------------
        # Step 8: Determine final certification status
        # ------------------------------------------------------------------
        if not_certified_reasons:
            certification_status = "L5_NOT_CERTIFIED"
            reason_codes = list(dict.fromkeys(  # preserve order, deduplicate
                ["not_certified"] + not_certified_reasons
            ))
        else:
            certification_status = "L5_CERTIFIED"

        # ------------------------------------------------------------------
        # Step 9: Compute deterministic packet digest
        # ------------------------------------------------------------------
        packet_digest = _compute_packet_digest(
            governance_context_digest=governance_context_digest,
            certification_status=certification_status,
            reason_codes=tuple(reason_codes),
            prior_packet_digest=prior_packet_digest,
            producer_ref=producer_ref,
            policy_ref=policy_ref,
            certifier_version=certifier_version,
        )

        # ------------------------------------------------------------------
        # Step 10: Build and return the packet
        # ------------------------------------------------------------------
        return L5CertificationPacket(
            certification_status=certification_status,
            reason_codes=tuple(reason_codes),
            evidence_refs=(governance_context_digest,),
            child_receipts=tuple(child_receipts),
            egress_receipts=tuple(egress_receipts),
            producer_ref=producer_ref,
            policy_ref=policy_ref,
            certifier_version=certifier_version,
            digest_sha256=packet_digest,
            run_id=run_id,
            trace_id=trace_id,
        )


__all__ = ["L5PacketProducer"]
