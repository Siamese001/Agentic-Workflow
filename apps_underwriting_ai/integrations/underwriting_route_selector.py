"""UnderwritingRouteSelector — metadata-only route resolution for apps_underwriting_ai.

Resolves the canonical route family and route mode from request metadata.
This selector is METADATA ONLY — it does not execute any stage, call any
provider, or write any state. L0 retains full authority; this selector
provides the app-side input to L0's route decision.

Route Decision Matrix:
  Full underwriting demo      → R3R4_MANAGED_WORKFLOW   / FULL_DECISION_PACKET
  Evidence-only review        → R3_SIMPLE_GROUNDED_READ / EVIDENCE_ONLY_REVIEW
  Schema / demo utility       → R4_SINGLE_ACTION         / ADMIN_OR_SCHEMA_UTILITY
  Exact replay of fixture     → R1A_EXACT_CACHE          / EXACT_REPLAY
  Similar prior demo          → R1B_SEMANTIC_CACHE       / DOC_HELP_ONLY
  Missing fixture documents   → R5_FALLBACK              / MISSING_INPUT_SAFE_FALLBACK
  Borderline synthetic case   → R3R4_MANAGED_WORKFLOW   / BORDERLINE_HITL_POSTURE

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 P1.2.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Literal

RouteFamily = Literal[
    "R1A_EXACT_CACHE",
    "R1B_SEMANTIC_CACHE",
    "R3_SIMPLE_GROUNDED_READ",
    "R3R4_MANAGED_WORKFLOW",
    "R4_SINGLE_ACTION",
    "R5_FALLBACK",
]

RouteMode = Literal[
    "FULL_DECISION_PACKET",
    "EVIDENCE_ONLY_REVIEW",
    "ADMIN_OR_SCHEMA_UTILITY",
    "EXACT_REPLAY",
    "DOC_HELP_ONLY",
    "MISSING_INPUT_SAFE_FALLBACK",
    "BORDERLINE_HITL_POSTURE",
]

HitlPosture = Literal["NONE", "SOFT_POSTURE", "HARD_FREEZE"]
CachePolicy = Literal["NO_CACHE", "ALLOW_EXACT", "ALLOW_SEMANTIC_DOC_HELP_ONLY"]
C0Mode = Literal["SUBMITTED_DOCUMENT_EVIDENCE_ONLY", "NONE"]
ExitMode = Literal["FAIL_CLOSED", "SOFT"]

_COMPLETENESS_THRESHOLD = 0.40
_CONTRADICTION_HARD_FREEZE_THRESHOLD = 0.60
_CONTRADICTION_SOFT_THRESHOLD = 0.30
_RATIONALE_SUPPORT_HARD_FREEZE_THRESHOLD = 0.50
_BORDERLINE_RISK_BANDS = {"BORDERLINE"}
_HIGH_RISK_BANDS = {"HIGH"}


@dataclass
class RouteSelectorInput:
    """Input bundle for the UnderwritingRouteSelector.

    All fields are required. Defaults represent the safest/most conservative
    values so that missing data routes to R5_FALLBACK rather than a degraded
    decision path.
    """

    product_class: str = ""
    applicant_type: Literal["INDIVIDUAL", "JOINT", "ENTITY"] = "INDIVIDUAL"
    submitted_document_profile: list[str] = field(default_factory=list)
    completeness_score: float = 0.0
    contradiction_score: float = 0.0
    risk_tier_band: Literal["LOW", "MEDIUM", "HIGH", "BORDERLINE", "UNKNOWN"] = "UNKNOWN"
    demo_mode: Literal[
        "full_decision",
        "evidence_only",
        "schema_utility",
        "replay",
        "doc_help",
    ] = "full_decision"
    demo_policy_profile: str = ""
    human_review_threshold_ref: str = ""
    exact_cache_key: str = ""
    semantic_cache_available: bool = False


@dataclass
class RouteSelectorOutput:
    """Output bundle from the UnderwritingRouteSelector.

    L0 consumes this output to make the final route decision.
    This output is metadata only — no execution is triggered by producing it.
    """

    canonical_route_family: RouteFamily = "R5_FALLBACK"
    underwriting_route_mode: RouteMode = "MISSING_INPUT_SAFE_FALLBACK"
    route_reason_codes: list[str] = field(default_factory=list)
    required_evidence_standard: Literal["FULL", "PARTIAL", "NONE"] = "NONE"
    hitl_posture: HitlPosture = "NONE"
    cache_policy: CachePolicy = "NO_CACHE"
    c0_mode: C0Mode = "NONE"
    pa_required: Literal["rationale_enrichment_enabled", "none"] = "none"
    l3_required: bool = False
    exit_mode: ExitMode = "FAIL_CLOSED"


def build_r1a_cache_key(
    *,
    request_envelope_hash: str,
    doc_content_hashes: list[str],
    policy_hash: str,
    blueprint_hash: str,
    scorer_version: str,
    schema_version: str,
) -> str:
    """Build the canonical R1A exact-cache key for apps_underwriting_ai.

    Key = SHA-256 of the canonical JSON serialisation of all 6 components.
    The serialisation is deterministic (sorted keys, no whitespace). Any
    change to any component — including document order — yields a distinct
    digest, guaranteeing a cache miss rather than a stale hit.

    Components (D2.1 specification):
      1. request_envelope_hash  — SHA-256 of the raw request envelope bytes.
      2. doc_content_hashes     — sorted list of per-document SHA-256 digests.
      3. policy_hash            — SHA-256 of the bound policy YAML blob.
      4. blueprint_hash         — SHA-256 of the bound blueprint YAML blob.
      5. scorer_version         — version tag of DeterministicRiskScorer.
      6. schema_version         — FEC / contract schema version string.

    Returns:
        Lowercase hex SHA-256 digest (64 chars).
    """
    payload = {
        "request_envelope_hash": request_envelope_hash,
        "doc_content_hashes": sorted(doc_content_hashes),
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "scorer_version": scorer_version,
        "schema_version": schema_version,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class UnderwritingRouteSelector:
    """Resolve the canonical route family and mode from request metadata.

    This selector is METADATA ONLY. It never executes stages, calls providers,
    reads documents, or writes state. L0 is the authoritative route decision
    maker; this class provides the app-side routing signal for L0 to consume.

    Routing priority (first match wins):
      1. schema_utility demo_mode        → R4_SINGLE_ACTION
      2. exact replay cache key present  → R1A_EXACT_CACHE
      3. doc_help demo_mode              → R1B_SEMANTIC_CACHE (DOC_HELP_ONLY)
      4. completeness below threshold    → R5_FALLBACK
      5. evidence_only demo_mode         → R3_SIMPLE_GROUNDED_READ
      6. borderline risk band            → R3R4_MANAGED_WORKFLOW + BORDERLINE_HITL_POSTURE
      7. default full decision           → R3R4_MANAGED_WORKFLOW + FULL_DECISION_PACKET
    """

    def select(self, inp: RouteSelectorInput) -> RouteSelectorOutput:
        """Resolve the route family and mode for the given request.

        Args:
            inp: The RouteSelectorInput describing the request metadata.

        Returns:
            RouteSelectorOutput with canonical_route_family and full metadata.
        """
        if inp.demo_mode == "schema_utility":
            return RouteSelectorOutput(
                canonical_route_family="R4_SINGLE_ACTION",
                underwriting_route_mode="ADMIN_OR_SCHEMA_UTILITY",
                route_reason_codes=["demo_mode=schema_utility"],
                required_evidence_standard="NONE",
                hitl_posture="NONE",
                cache_policy="NO_CACHE",
                c0_mode="NONE",
                pa_required="none",
                l3_required=False,
                exit_mode="SOFT",
            )

        if inp.exact_cache_key:
            return RouteSelectorOutput(
                canonical_route_family="R1A_EXACT_CACHE",
                underwriting_route_mode="EXACT_REPLAY",
                route_reason_codes=["exact_cache_key_present"],
                required_evidence_standard="NONE",
                hitl_posture="NONE",
                cache_policy="ALLOW_EXACT",
                c0_mode="NONE",
                pa_required="none",
                l3_required=False,
                exit_mode="SOFT",
            )

        if inp.demo_mode == "doc_help":
            return RouteSelectorOutput(
                canonical_route_family="R1B_SEMANTIC_CACHE",
                underwriting_route_mode="DOC_HELP_ONLY",
                route_reason_codes=["demo_mode=doc_help", "no_verdict_reuse"],
                required_evidence_standard="NONE",
                hitl_posture="NONE",
                cache_policy="ALLOW_SEMANTIC_DOC_HELP_ONLY",
                c0_mode="NONE",
                pa_required="none",
                l3_required=False,
                exit_mode="SOFT",
            )

        if inp.completeness_score < _COMPLETENESS_THRESHOLD:
            return RouteSelectorOutput(
                canonical_route_family="R5_FALLBACK",
                underwriting_route_mode="MISSING_INPUT_SAFE_FALLBACK",
                route_reason_codes=[
                    f"completeness_score={inp.completeness_score:.2f} < threshold={_COMPLETENESS_THRESHOLD}"
                ],
                required_evidence_standard="NONE",
                hitl_posture="NONE",
                cache_policy="NO_CACHE",
                c0_mode="NONE",
                pa_required="none",
                l3_required=False,
                exit_mode="FAIL_CLOSED",
            )

        if inp.demo_mode == "evidence_only":
            return RouteSelectorOutput(
                canonical_route_family="R3_SIMPLE_GROUNDED_READ",
                underwriting_route_mode="EVIDENCE_ONLY_REVIEW",
                route_reason_codes=["demo_mode=evidence_only", "no_verdict_assembly"],
                required_evidence_standard="PARTIAL",
                hitl_posture="NONE",
                cache_policy="NO_CACHE",
                c0_mode="SUBMITTED_DOCUMENT_EVIDENCE_ONLY",
                pa_required="none",
                l3_required=False,
                exit_mode="SOFT",
            )

        reason_codes: list[str] = ["demo_mode=full_decision"]
        hitl_posture: HitlPosture = "NONE"

        if inp.risk_tier_band in _BORDERLINE_RISK_BANDS:
            hitl_posture = "SOFT_POSTURE"
            reason_codes.append("risk_tier_band=BORDERLINE")

        if inp.contradiction_score >= _CONTRADICTION_HARD_FREEZE_THRESHOLD:
            hitl_posture = "HARD_FREEZE"
            reason_codes.append(
                f"contradiction_score={inp.contradiction_score:.2f} >= hard_freeze_threshold"
            )
        elif inp.contradiction_score >= _CONTRADICTION_SOFT_THRESHOLD:
            if hitl_posture == "NONE":
                hitl_posture = "SOFT_POSTURE"
            reason_codes.append(
                f"contradiction_score={inp.contradiction_score:.2f} >= soft_threshold"
            )

        route_mode: RouteMode = (
            "BORDERLINE_HITL_POSTURE" if hitl_posture != "NONE" else "FULL_DECISION_PACKET"
        )

        return RouteSelectorOutput(
            canonical_route_family="R3R4_MANAGED_WORKFLOW",
            underwriting_route_mode=route_mode,
            route_reason_codes=reason_codes,
            required_evidence_standard="FULL",
            hitl_posture=hitl_posture,
            cache_policy="NO_CACHE",
            c0_mode="SUBMITTED_DOCUMENT_EVIDENCE_ONLY",
            pa_required="rationale_enrichment_enabled",
            l3_required=True,
            exit_mode="FAIL_CLOSED",
        )
