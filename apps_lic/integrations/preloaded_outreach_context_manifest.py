"""PreloadedOutreachContextManifest — prerequisite briefing artifact for apps_lic.

The manifest is the canonical prerequisite for R4_SINGLE_ACTION outreach drafts —
same role as the company brief for apps_rg.  It encodes all context needed for
message composition, including claim governance, proof mode, send-mode policy,
and HITL gating metadata.

Manifest rules
--------------
- Frozen dataclass — immutable after construction.
- ``manifest_hash`` is computed deterministically over all fields except itself.
- ``freshness_status`` drives routing: "fresh" → R4, "stale"/"missing" → R3R4.
- ``claim_permission_map`` governs which claims are allowed, omittable,
  HITL-required, or fail-closed.  All keys must be present before R4 dispatch.
- ``omission_policy`` is the default when a claim is not in ``claim_permission_map``.
- BriefingReady validation is enforced by ``validate_briefing_ready``.

BriefingReady criteria (plan §BriefingReady success criteria)
--------------------------------------------------------------
A manifest is valid for R4 dispatch ONLY if ALL of:
  1. ``confidence_score`` >= ``confidence_threshold`` (default 0.60)
  2. ``freshness_status`` in {"fresh"} (or "stale" if policy permits)
  3. All ``required_coverage_fields`` present and non-empty in the manifest
  4. ``source_items`` is non-empty
  5. ``audit_refs`` is non-empty
  6. ``content_hashes`` present for all coverage fields
  7. ``origin_label_map`` is non-empty
  8. All ``unsupported_fact_flags`` entries are classified in
     ``claim_permission_map`` as one of:
     "omit_unsupported" | "hitl_required" | "fail_closed"

Failure mapping:
  - confidence < threshold → APPS_RESEARCH_WEAK_SUPPORT
  - freshness not acceptable → APPS_RESEARCH_STALE
  - required coverage field missing → APPS_RESEARCH_EMPTY
  - source_items empty → APPS_RESEARCH_EMPTY
  - audit_refs empty → APPS_RESEARCH_BLOCKED
  - content_hashes missing → APPS_RESEARCH_EMPTY
  - origin_label_map missing → APPS_RESEARCH_EMPTY
  - unsupported gap not classified → APPS_RESEARCH_BLOCKED

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-lic-canonical-spine-wireup-e7c2a5.md`` W2 P5
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, fields, asdict
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Supporting types
# ---------------------------------------------------------------------------

_ALLOWED_SEND_MODES = frozenset({
    "draft_only",
    "review_required",
    "send_ready_candidate",
})

_FORBIDDEN_SEND_MODES = frozenset({
    "send_now",
    "auto_send",
    "connector_send",
})

_VALID_CHANNELS = frozenset({"email", "linkedin", "text"})

_VALID_OUTREACH_MODES = frozenset({"cold", "warm", "referral", "followup"})

_VALID_RECIPIENT_CLASSES = frozenset({
    "RECRUITER",
    "SENIOR_TA",
    "HIRING_MANAGER",
    "EXECUTIVE",
    "C_LEVEL",
    "VP_ENG",
    "CTO",
    "REFERRAL_CONTACT",
})

_VALID_FRESHNESS_STATUSES = frozenset({"fresh", "stale", "missing"})

_VALID_PROOF_MODES = frozenset({
    "none",
    "resume_metric",
    "repo_link",
    "public_artifact",
    "referral_context",
    "company_brief",
    "recipient_brief",
})

_VALID_PERSONALIZATION_MODES = frozenset({
    "none",
    "company",
    "role",
    "recipient",
    "relationship",
    "asymmetric",
})

_VALID_OMISSION_POLICIES = frozenset({
    "omit_unsupported",
    "hitl_required",
    "fail_closed",
})

_VALID_CLAIM_PERMISSIONS = frozenset({
    "allowed",
    "omit_unsupported",
    "hitl_required",
    "fail_closed",
})

_VALID_APPLICATION_STATUSES = frozenset({
    "applied",
    "referred",
    "interviewing",
    "offer",
    "none",
})

_VALID_SENIORITY = frozenset({"IC", "MANAGER", "DIRECTOR", "VP", "C_LEVEL"})

_VALID_RELATIONSHIP_DISTANCES = frozenset({"cold", "warm", "referral", "known"})

DEFAULT_CONFIDENCE_THRESHOLD = 0.60


@dataclass(frozen=True)
class SourceItem:
    """A single cited source item for a claim in the manifest."""

    source_id: str
    source_type: str         # "resume", "research", "public", "referral"
    label: str               # human-readable label
    uri: str                 # URI or hash of the source
    field_ref: str           # which manifest field this sourced


# ---------------------------------------------------------------------------
# Main manifest class (35 fields)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PreloadedOutreachContextManifest:
    """Prerequisite briefing artifact for apps_lic R4_SINGLE_ACTION dispatch.

    Construct via ``build_manifest`` to get correct ``manifest_hash``.
    Do NOT set ``manifest_hash`` manually — use the factory.
    """

    # ------------------------------------------------------------------
    # Identity (4 fields)
    # ------------------------------------------------------------------
    manifest_id: str
    request_id: str
    run_id: str
    trace_id: str

    # ------------------------------------------------------------------
    # Policy / Blueprint binding (3 fields)
    # ------------------------------------------------------------------
    policy_hash: str
    blueprint_hash: str
    replay_key: str

    # ------------------------------------------------------------------
    # Source references (8 fields)
    # ------------------------------------------------------------------
    user_profile_ref: str           # hash of user profile
    resume_ref: str                 # hash of resume snapshot
    target_role_ref: str            # hash of JD
    job_description_ref: str        # URI + hash of JD
    application_status: str         # "applied"|"referred"|"interviewing"|"offer"|"none"
    company_brief_ref: str          # hash of company briefing
    recipient_brief_ref: str        # hash of recipient research briefing
    relationship_context_ref: str   # hash of relationship context

    # ------------------------------------------------------------------
    # Channel / mode selection (5 fields)
    # ------------------------------------------------------------------
    channel: str                    # "email"|"linkedin"|"text"
    outreach_mode: str              # "cold"|"warm"|"referral"|"followup"
    recipient_class: str            # RECRUITER|SENIOR_TA|HIRING_MANAGER|EXECUTIVE|C_LEVEL|VP_ENG|CTO|REFERRAL_CONTACT
    recipient_seniority: str        # IC|MANAGER|DIRECTOR|VP|C_LEVEL
    relationship_distance: str      # cold|warm|referral|known

    # ------------------------------------------------------------------
    # Content governance (5 fields)
    # ------------------------------------------------------------------
    source_items: tuple             # tuple[SourceItem, ...] — frozen-safe
    origin_label_map: dict          # field → source label
    content_hashes: dict            # field → sha256 hash
    freshness_status: str           # "fresh"|"stale"|"missing"
    unsupported_fact_flags: tuple   # tuple[str, ...] — claims needing HITL

    # ------------------------------------------------------------------
    # Claim governance (4 fields)
    # ------------------------------------------------------------------
    claim_permission_map: dict      # claim → "allowed"|"omit_unsupported"|"hitl_required"|"fail_closed"
    proof_mode: str                 # "none"|"resume_metric"|"repo_link"|"public_artifact"|"referral_context"|"company_brief"|"recipient_brief"
    personalization_mode: str       # "none"|"company"|"role"|"recipient"|"relationship"|"asymmetric"
    omission_policy: str            # "omit_unsupported"|"hitl_required"|"fail_closed"

    # ------------------------------------------------------------------
    # Quality signal (1 field — for BriefingReady validation)
    # ------------------------------------------------------------------
    confidence_score: float         # 0.0–1.0; must be >= threshold for BriefingReady

    # ------------------------------------------------------------------
    # Output governance (1 field)
    # ------------------------------------------------------------------
    send_mode: str                  # "draft_only"|"review_required"|"send_ready_candidate"
                                    # FORBIDDEN: "send_now", "auto_send", "connector_send"
                                    # Defaults to "draft_only" at manifest construction time.

    # ------------------------------------------------------------------
    # HITL gating (2 fields)
    # ------------------------------------------------------------------
    personalization_confidence: float       # 0.0–1.0
    required_hitl_flags: tuple             # tuple[str, ...] e.g. "senior_exec_recipient"

    # ------------------------------------------------------------------
    # Audit (2 fields)
    # ------------------------------------------------------------------
    audit_refs: tuple               # tuple[str, ...] — trace IDs for upstream evidence
    manifest_hash: str              # sha256 of serialized manifest (all other fields)

    # ------------------------------------------------------------------
    # Field count assertion (resolved at class-definition time)
    # ------------------------------------------------------------------
    def __post_init__(self) -> None:
        # 35 fields: Identity(4) + Policy(3) + Source(8) + Channel(5) +
        # Content governance(5) + Claim governance(4) + Quality(1) +
        # Output governance(1) + HITL(2) + Audit(2) = 35
        actual_count = len(fields(self))
        assert actual_count == 35, (
            f"PreloadedOutreachContextManifest has {actual_count} fields; "
            f"expected 35. Add or remove fields to match the plan spec."
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def _compute_manifest_hash(data: dict[str, Any]) -> str:
    """Deterministic sha256 over all manifest fields except manifest_hash."""
    blob = json.dumps(
        {k: v for k, v in data.items() if k != "manifest_hash"},
        sort_keys=True,
        default=str,
    ).encode()
    return f"sha256:{hashlib.sha256(blob).hexdigest()}"


def build_manifest(
    *,
    manifest_id: str,
    request_id: str,
    run_id: str,
    trace_id: str,
    policy_hash: str,
    blueprint_hash: str,
    replay_key: str,
    user_profile_ref: str,
    resume_ref: str,
    target_role_ref: str,
    job_description_ref: str,
    application_status: str,
    company_brief_ref: str,
    recipient_brief_ref: str,
    relationship_context_ref: str,
    channel: str,
    outreach_mode: str,
    recipient_class: str,
    recipient_seniority: str,
    relationship_distance: str,
    source_items: List[SourceItem],
    origin_label_map: Dict[str, str],
    content_hashes: Dict[str, str],
    freshness_status: str,
    unsupported_fact_flags: List[str],
    claim_permission_map: Dict[str, str],
    proof_mode: str,
    personalization_mode: str,
    omission_policy: str,
    confidence_score: float,
    send_mode: str,
    personalization_confidence: float,
    required_hitl_flags: List[str],
    audit_refs: List[str],
) -> PreloadedOutreachContextManifest:
    """Construct a manifest with a correct ``manifest_hash``."""
    # Convert mutable containers to hashable/frozen equivalents
    source_items_frozen = tuple(source_items)
    unsupported_frozen = tuple(unsupported_fact_flags)
    required_hitl_frozen = tuple(required_hitl_flags)
    audit_refs_frozen = tuple(audit_refs)
    origin_frozen = dict(origin_label_map)
    content_hashes_frozen = dict(content_hashes)
    claim_perm_frozen = dict(claim_permission_map)

    # Compute hash over all non-hash fields
    pre_hash_data: dict[str, Any] = {
        "manifest_id": manifest_id,
        "request_id": request_id,
        "run_id": run_id,
        "trace_id": trace_id,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "replay_key": replay_key,
        "user_profile_ref": user_profile_ref,
        "resume_ref": resume_ref,
        "target_role_ref": target_role_ref,
        "job_description_ref": job_description_ref,
        "application_status": application_status,
        "company_brief_ref": company_brief_ref,
        "recipient_brief_ref": recipient_brief_ref,
        "relationship_context_ref": relationship_context_ref,
        "channel": channel,
        "outreach_mode": outreach_mode,
        "recipient_class": recipient_class,
        "recipient_seniority": recipient_seniority,
        "relationship_distance": relationship_distance,
        "source_items": [str(si) for si in source_items_frozen],
        "origin_label_map": origin_frozen,
        "content_hashes": content_hashes_frozen,
        "freshness_status": freshness_status,
        "unsupported_fact_flags": list(unsupported_frozen),
        "claim_permission_map": claim_perm_frozen,
        "proof_mode": proof_mode,
        "personalization_mode": personalization_mode,
        "omission_policy": omission_policy,
        "confidence_score": confidence_score,
        "send_mode": send_mode,
        "personalization_confidence": personalization_confidence,
        "required_hitl_flags": list(required_hitl_frozen),
        "audit_refs": list(audit_refs_frozen),
    }
    manifest_hash = _compute_manifest_hash(pre_hash_data)

    return PreloadedOutreachContextManifest(
        manifest_id=manifest_id,
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        replay_key=replay_key,
        user_profile_ref=user_profile_ref,
        resume_ref=resume_ref,
        target_role_ref=target_role_ref,
        job_description_ref=job_description_ref,
        application_status=application_status,
        company_brief_ref=company_brief_ref,
        recipient_brief_ref=recipient_brief_ref,
        relationship_context_ref=relationship_context_ref,
        channel=channel,
        outreach_mode=outreach_mode,
        recipient_class=recipient_class,
        recipient_seniority=recipient_seniority,
        relationship_distance=relationship_distance,
        source_items=source_items_frozen,
        origin_label_map=origin_frozen,
        content_hashes=content_hashes_frozen,
        freshness_status=freshness_status,
        unsupported_fact_flags=unsupported_frozen,
        claim_permission_map=claim_perm_frozen,
        proof_mode=proof_mode,
        personalization_mode=personalization_mode,
        omission_policy=omission_policy,
        confidence_score=confidence_score,
        send_mode=send_mode,
        personalization_confidence=personalization_confidence,
        required_hitl_flags=required_hitl_frozen,
        audit_refs=audit_refs_frozen,
        manifest_hash=manifest_hash,
    )


# ---------------------------------------------------------------------------
# BriefingReady validation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BriefingReadyResult:
    """Result of validate_briefing_ready()."""

    is_valid: bool
    r5_reason_code: str    # "" when is_valid=True
    detail: str


def validate_briefing_ready(
    manifest: PreloadedOutreachContextManifest,
    *,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    acceptable_freshness: frozenset[str] | None = None,
    required_coverage_fields: List[str] | None = None,
    allow_stale: bool = False,
) -> BriefingReadyResult:
    """Validate that a manifest is BriefingReady for R4 dispatch.

    Returns BriefingReadyResult with is_valid=True when all criteria pass.
    Returns is_valid=False with the appropriate R5 reason code otherwise.
    """
    if acceptable_freshness is None:
        acceptable_freshness = frozenset({"fresh"})
        if allow_stale:
            acceptable_freshness = frozenset({"fresh", "stale"})

    if required_coverage_fields is None:
        required_coverage_fields = [
            "recipient_brief_ref",
            "company_brief_ref",
            "resume_ref",
        ]

    # 1. Confidence score
    if manifest.confidence_score < confidence_threshold:
        return BriefingReadyResult(
            is_valid=False,
            r5_reason_code="APPS_RESEARCH_WEAK_SUPPORT",
            detail=(
                f"confidence_score={manifest.confidence_score:.2f} < "
                f"threshold={confidence_threshold:.2f}"
            ),
        )

    # 2. Freshness
    if manifest.freshness_status not in acceptable_freshness:
        return BriefingReadyResult(
            is_valid=False,
            r5_reason_code="APPS_RESEARCH_STALE",
            detail=(
                f"freshness_status={manifest.freshness_status!r} not in "
                f"acceptable={sorted(acceptable_freshness)}"
            ),
        )

    # 3. Required coverage fields present and non-empty
    for cov_field in required_coverage_fields:
        val = getattr(manifest, cov_field, None)
        if not val:
            return BriefingReadyResult(
                is_valid=False,
                r5_reason_code="APPS_RESEARCH_EMPTY",
                detail=f"required_coverage_field {cov_field!r} is missing or empty",
            )

    # 4. source_items non-empty
    if not manifest.source_items:
        return BriefingReadyResult(
            is_valid=False,
            r5_reason_code="APPS_RESEARCH_EMPTY",
            detail="source_items is empty — no citations for claims",
        )

    # 5. audit_refs non-empty
    if not manifest.audit_refs:
        return BriefingReadyResult(
            is_valid=False,
            r5_reason_code="APPS_RESEARCH_BLOCKED",
            detail="audit_refs is empty — no upstream evidence trace IDs",
        )

    # 6. content_hashes present
    if not manifest.content_hashes:
        return BriefingReadyResult(
            is_valid=False,
            r5_reason_code="APPS_RESEARCH_EMPTY",
            detail="content_hashes is empty — no field-level hash binding",
        )

    # 7. origin_label_map present
    if not manifest.origin_label_map:
        return BriefingReadyResult(
            is_valid=False,
            r5_reason_code="APPS_RESEARCH_EMPTY",
            detail="origin_label_map is empty — no field-to-source traceability",
        )

    # 8. All unsupported gaps classified
    valid_gap_dispositions = {"omit_unsupported", "hitl_required", "fail_closed"}
    for gap_claim in manifest.unsupported_fact_flags:
        perm = manifest.claim_permission_map.get(gap_claim)
        if perm not in valid_gap_dispositions:
            return BriefingReadyResult(
                is_valid=False,
                r5_reason_code="APPS_RESEARCH_BLOCKED",
                detail=(
                    f"unsupported_fact_flag {gap_claim!r} not classified in "
                    f"claim_permission_map (got {perm!r}); must be one of "
                    f"{sorted(valid_gap_dispositions)}"
                ),
            )

    return BriefingReadyResult(is_valid=True, r5_reason_code="", detail="")


# ---------------------------------------------------------------------------
# OutreachDraft — P16
# Output type for apps_lic R4_SINGLE_ACTION draft composition.
# omitted_claims tracks all claims omitted via omission_policy.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OutreachDraft:
    """Sealed outreach draft produced by the L2 hop-based composition stage.

    ``omitted_claims`` lists all claim ids that were omitted from the draft
    because their ``omission_policy`` was ``omit_unsupported``.  The exit
    rubric's ``factual_support`` dimension does NOT check omitted claims.

    ``send_mode`` must be one of the allowed values; forbidden modes
    (send_now, auto_send, connector_send) must never appear here.

    ``manifest_hash`` binds the draft to the manifest that was used for
    composition — enabling audit traceability.
    """

    draft_text: str
    send_mode: str                    # "draft_only"|"review_required"|"send_ready_candidate"
    manifest_hash: str                # binds to PreloadedOutreachContextManifest
    word_count: int
    omitted_claims: tuple             # tuple[str, ...] — claim ids omitted from draft
    channel: str
    outreach_mode: str
    recipient_class: str
    draft_ref: str = ""               # sha256 of draft_text (set by sealing step)

    def __post_init__(self) -> None:
        if self.send_mode in _FORBIDDEN_SEND_MODES:
            raise ValueError(
                f"OutreachDraft.send_mode={self.send_mode!r} is forbidden. "
                f"Allowed: {sorted(_ALLOWED_SEND_MODES)}"
            )


# ---------------------------------------------------------------------------
# Omission policy application — P16
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OmissionDecision:
    """Decision for a single claim under the manifest's omission_policy.

    action:
      "include"   — claim is supported; include in draft
      "omit"      — omit_unsupported: silently omit; track in omitted_claims
      "hitl"      — hitl_required: produce draft but escalate to HITL
      "fail"      — fail_closed: block draft entirely (UNSUPPORTED_MANDATORY_CLAIMS)
    """

    claim_id: str
    action: str               # "include" | "omit" | "hitl" | "fail"
    reason: str = ""
    is_supported: bool = True


def apply_omission_policy(
    *,
    claims: List[str],
    manifest: PreloadedOutreachContextManifest,
) -> List[OmissionDecision]:
    """Evaluate each claim against the manifest's omission_policy.

    For each claim in ``claims``:
    1. If the claim has a source_item in manifest.source_items: action="include"
    2. If the claim is in manifest.claim_permission_map:
       - "allowed" → action="include" (even if unsupported; allowed override)
       - "omit_unsupported" → action="omit" if claim not in source_items
       - "hitl_required" → action="hitl" if claim not in source_items
       - "fail_closed" → action="fail" if claim not in source_items
    3. If claim not in claim_permission_map: use manifest.omission_policy as default
       - "omit_unsupported" → action="omit"
       - "hitl_required" → action="hitl"
       - "fail_closed" → action="fail"

    Returns a list of OmissionDecision, one per claim.
    """
    # Build set of supported claim ids from source_items
    supported_claim_ids = frozenset(
        si.field_ref for si in manifest.source_items if si.field_ref
    )

    decisions = []
    for claim_id in claims:
        is_supported = claim_id in supported_claim_ids

        if is_supported:
            decisions.append(OmissionDecision(
                claim_id=claim_id,
                action="include",
                reason="claim supported by source_items",
                is_supported=True,
            ))
            continue

        # Claim is NOT supported — check permission map
        permission = manifest.claim_permission_map.get(claim_id)
        if permission is None:
            # Fall back to manifest-level omission_policy
            permission = manifest.omission_policy

        if permission == "allowed":
            decisions.append(OmissionDecision(
                claim_id=claim_id,
                action="include",
                reason="claim_permission_map=allowed override (unsupported but permitted)",
                is_supported=False,
            ))
        elif permission == "omit_unsupported":
            decisions.append(OmissionDecision(
                claim_id=claim_id,
                action="omit",
                reason="omit_unsupported: claim not in source_items; silently omitting",
                is_supported=False,
            ))
        elif permission == "hitl_required":
            decisions.append(OmissionDecision(
                claim_id=claim_id,
                action="hitl",
                reason="hitl_required: claim not in source_items; escalating to HITL",
                is_supported=False,
            ))
        elif permission == "fail_closed":
            decisions.append(OmissionDecision(
                claim_id=claim_id,
                action="fail",
                reason=(
                    "fail_closed: mandatory claim not in source_items; "
                    "blocking draft (UNSUPPORTED_MANDATORY_CLAIMS)"
                ),
                is_supported=False,
            ))
        else:
            # Unknown permission — treat as fail_closed for safety
            decisions.append(OmissionDecision(
                claim_id=claim_id,
                action="fail",
                reason=(
                    f"unknown permission={permission!r} for claim {claim_id!r}; "
                    "defaulting to fail_closed for safety"
                ),
                is_supported=False,
            ))

    return decisions
