"""Managed workflow dispatcher for apps_lic R3R4_MANAGED_WORKFLOW route.

This module is the L3 orchestration layer for the missing/stale briefing path.
When L0 emits R3R4_MANAGED_WORKFLOW, this dispatcher:

  1. Validates the RequestForBriefing input.
  2. Calls apps_research via AppsResearchBridge (registered public interface only).
  3. On success: converts the research result into a PreloadedOutreachContextManifest
     and returns BriefingReady — the dispatcher hands control back to the R4 path.
  4. On any research failure: emits a DispatchFailurePacket with the appropriate
     R5 reason code. The caller (managed_workflow_r3r4 entrypoint) routes this
     through Exit V6 as a terminal path.

Fail-closed invariants (P9)
---------------------------
Every research failure maps to EXACTLY ONE R5 reason code:

  APPS_RESEARCH_FAILED       — apps_research raised an unhandled exception
  APPS_RESEARCH_EMPTY        — apps_research returned zero usable evidence items
  APPS_RESEARCH_BLOCKED      — apps_research returned a blocked/capability-unavailable signal
  APPS_RESEARCH_STALE        — research result is outside freshness TTL
  APPS_RESEARCH_WEAK_SUPPORT — confidence_score below configured threshold

No code path in this module generates a generic fallback draft. No draft is
produced when research fails — only a DispatchFailurePacket for Exit V6 to consume.

Decision-only constraints
-------------------------
This dispatcher is L3 orchestration. It:
  - MUST NOT write durable state directly (all writes go through Exit → UWG → L4).
  - MUST NOT call provider APIs (no openai, anthropic, etc.).
  - MUST NOT use subprocess or os.system.
  - MAY call AppsResearchBridge (registered public interface only).
  - MAY read config via open(path, "r") / yaml.safe_load / json.load.

Plan: .windsurf/plans/apps-lic-canonical-spine-wireup-e7c2a5.md W3 P7 + P9
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# R5 reason codes for research failures (P9)
# ---------------------------------------------------------------------------

RESEARCH_FAILURE_REASON_CODES = frozenset({
    "APPS_RESEARCH_FAILED",
    "APPS_RESEARCH_EMPTY",
    "APPS_RESEARCH_BLOCKED",
    "APPS_RESEARCH_STALE",
    "APPS_RESEARCH_WEAK_SUPPORT",
})


class ResearchFailureReason(str, Enum):
    """R5 reason codes emitted when apps_research fails in the managed workflow."""

    APPS_RESEARCH_FAILED = "APPS_RESEARCH_FAILED"
    APPS_RESEARCH_EMPTY = "APPS_RESEARCH_EMPTY"
    APPS_RESEARCH_BLOCKED = "APPS_RESEARCH_BLOCKED"
    APPS_RESEARCH_STALE = "APPS_RESEARCH_STALE"
    APPS_RESEARCH_WEAK_SUPPORT = "APPS_RESEARCH_WEAK_SUPPORT"


# ---------------------------------------------------------------------------
# Input / output types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RequestForBriefing:
    """Input to the managed workflow dispatcher.

    Carries all context needed to perform an apps_research call and convert
    the result into a PreloadedOutreachContextManifest.
    """

    # Identity
    request_id: str
    run_id: str
    trace_id: str

    # Who we are reaching out to / about
    recipient_class: str          # RECRUITER|SENIOR_TA|HIRING_MANAGER|EXECUTIVE|C_LEVEL|VP_ENG|CTO|REFERRAL_CONTACT
    recipient_name: str           # for personalization
    company_name: str             # target company
    job_title: str                # target role (may be empty for exploratory outreach)

    # Channel / mode
    channel: str                  # "email"|"linkedin"|"text"
    outreach_mode: str            # "cold"|"warm"|"referral"|"followup"
    relationship_distance: str    # "cold"|"warm"|"referral"|"known"

    # Sender
    sender_resume_ref: str        # hash of sender resume snapshot
    sender_policy_hash: str       # hash of policy config at request time
    sender_blueprint_hash: str    # hash of blueprint config at request time

    # Research authorization (must be True to proceed)
    research_authorized: bool     # from L0 policy check
    research_capability_ref: str  # capability token for apps_research binding

    # Freshness config
    freshness_ttl_days: int = 7   # for executive; 30 for recruiter
    min_confidence_threshold: float = 0.60

    # Audit
    audit_refs: tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class BriefingReady:
    """Successful result of the managed workflow dispatcher.

    Contains a fully-constructed PreloadedOutreachContextManifest ready
    for R4_SINGLE_ACTION dispatch, plus dispatch metadata.
    """

    request_id: str
    run_id: str
    trace_id: str
    manifest: Any   # PreloadedOutreachContextManifest — avoid circular import at type level
    research_run_id: str
    research_evidence_count: int
    confidence_score: float
    dispatch_duration_ms: float
    audit_refs: tuple
    evidence_lineage: tuple = field(default_factory=tuple)


@dataclass(frozen=True)
class DispatchFailurePacket:
    """Fail-closed result when research fails or authorization is denied.

    The caller feeds this into Exit V6 as a terminal R5 receipt.
    No draft is produced — this is the sole output of a failed dispatch.
    """

    request_id: str
    run_id: str
    trace_id: str
    r5_reason_code: str   # one of RESEARCH_FAILURE_REASON_CODES
    detail: str
    dispatch_duration_ms: float
    is_terminal: bool = True   # always True — caller must NOT proceed to R4


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


def _utc_ms() -> float:
    return time.time() * 1000.0


def dispatch_managed_briefing(
    request: RequestForBriefing,
    *,
    bridge: Any,  # AppsResearchBridge — injected to avoid circular import
) -> BriefingReady | DispatchFailurePacket:
    """Orchestrate apps_research and convert result to PreloadedOutreachContextManifest.

    Args:
        request: RequestForBriefing with all context for the research call.
        bridge: AppsResearchBridge instance (injected — registered public interface only).

    Returns:
        BriefingReady on success, DispatchFailurePacket on any failure.

    Fail-closed invariants (P9):
        - research_authorized=False → DispatchFailurePacket (APPS_RESEARCH_BLOCKED)
        - bridge.fetch raises → DispatchFailurePacket (APPS_RESEARCH_FAILED)
        - result.evidence_items empty → DispatchFailurePacket (APPS_RESEARCH_EMPTY)
        - result.is_blocked → DispatchFailurePacket (APPS_RESEARCH_BLOCKED)
        - result.is_stale → DispatchFailurePacket (APPS_RESEARCH_STALE)
        - result.confidence < threshold → DispatchFailurePacket (APPS_RESEARCH_WEAK_SUPPORT)
        - success → BriefingReady with manifest
    """
    t_start = _utc_ms()
    run_id = request.run_id
    request_id = request.request_id
    trace_id = request.trace_id

    # ------------------------------------------------------------------
    # Authorization check (P9: APPS_RESEARCH_BLOCKED for policy deny)
    # ------------------------------------------------------------------
    if not request.research_authorized:
        return DispatchFailurePacket(
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_BLOCKED.value,
            detail=(
                "research_authorized=False — policy or capability disabled "
                "apps_research for this run. "
                "Route: BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED."
            ),
            dispatch_duration_ms=_utc_ms() - t_start,
        )

    # ------------------------------------------------------------------
    # Call apps_research via bridge (P7)
    # ------------------------------------------------------------------
    try:
        research_result = bridge.fetch(
            recipient_class=request.recipient_class,
            recipient_name=request.recipient_name,
            company_name=request.company_name,
            job_title=request.job_title,
            channel=request.channel,
            outreach_mode=request.outreach_mode,
            relationship_distance=request.relationship_distance,
            capability_ref=request.research_capability_ref,
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
        )
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- apps_research is an external system;
        # any exception here is an unhandled research failure → fail-closed.
        return DispatchFailurePacket(
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_FAILED.value,
            detail=f"apps_research bridge raised: {type(exc).__name__}: {exc}",
            dispatch_duration_ms=_utc_ms() - t_start,
        )

    # ------------------------------------------------------------------
    # Validate research result (P9: all 5 failure codes)
    # ------------------------------------------------------------------

    # APPS_RESEARCH_BLOCKED — bridge returned a blocked signal
    if getattr(research_result, "is_blocked", False):
        return DispatchFailurePacket(
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_BLOCKED.value,
            detail=(
                f"apps_research returned blocked signal: "
                f"{getattr(research_result, 'block_reason', 'unknown')}"
            ),
            dispatch_duration_ms=_utc_ms() - t_start,
        )

    # APPS_RESEARCH_EMPTY — no usable evidence items
    evidence_items = getattr(research_result, "evidence_items", [])
    if not evidence_items:
        return DispatchFailurePacket(
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_EMPTY.value,
            detail=(
                "apps_research returned zero evidence_items. "
                "No briefing can be constructed without evidence."
            ),
            dispatch_duration_ms=_utc_ms() - t_start,
        )

    # APPS_RESEARCH_STALE — result outside freshness TTL
    if getattr(research_result, "is_stale", False):
        return DispatchFailurePacket(
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_STALE.value,
            detail=(
                f"apps_research result is stale "
                f"(ttl_days={request.freshness_ttl_days}, "
                f"result_age_days={getattr(research_result, 'age_days', 'unknown')}). "
                "Re-run with a fresh research pass."
            ),
            dispatch_duration_ms=_utc_ms() - t_start,
        )

    # APPS_RESEARCH_WEAK_SUPPORT — confidence below threshold
    confidence = float(getattr(research_result, "confidence_score", 0.0))
    if confidence < request.min_confidence_threshold:
        return DispatchFailurePacket(
            request_id=request_id,
            run_id=run_id,
            trace_id=trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_WEAK_SUPPORT.value,
            detail=(
                f"apps_research confidence_score={confidence:.2f} < "
                f"threshold={request.min_confidence_threshold:.2f}. "
                "Insufficient evidence support for outreach draft."
            ),
            dispatch_duration_ms=_utc_ms() - t_start,
        )

    # ------------------------------------------------------------------
    # Build PreloadedOutreachContextManifest from research result (P7)
    # ------------------------------------------------------------------
    manifest = _build_manifest_from_research(
        request=request,
        research_result=research_result,
        confidence=confidence,
    )

    research_run_id = str(getattr(research_result, "run_id", uuid.uuid4()))
    evidence_count = len(evidence_items)
    audit_refs_list = list(request.audit_refs) + [
        getattr(research_result, "trace_id", trace_id)
    ]

    lineage = tuple(
        {
            "source_id": getattr(ev, "source_id", ""),
            "label": getattr(ev, "label", ""),
            "uri": getattr(ev, "uri", ""),
            "source_type": getattr(ev, "source_type", ""),
            "field_ref": getattr(ev, "field_ref", ""),
            "confidence": float(getattr(ev, "confidence", 0.0)),
        }
        for ev in evidence_items
    )
    return BriefingReady(
        request_id=request_id,
        run_id=run_id,
        trace_id=trace_id,
        manifest=manifest,
        research_run_id=research_run_id,
        research_evidence_count=evidence_count,
        confidence_score=confidence,
        dispatch_duration_ms=_utc_ms() - t_start,
        audit_refs=tuple(audit_refs_for := audit_refs_list),
        evidence_lineage=lineage,
    )


# ---------------------------------------------------------------------------
# Internal manifest builder
# ---------------------------------------------------------------------------


def _build_manifest_from_research(
    *,
    request: RequestForBriefing,
    research_result: Any,
    confidence: float,
) -> Any:
    """Convert an apps_research result into a PreloadedOutreachContextManifest.

    Deferred import to avoid circular dependency at module load time.
    The manifest module is loaded lazily here.
    """
    from apps_lic.integrations.preloaded_outreach_context_manifest import (
        build_manifest,
        SourceItem,
    )

    evidence_items = getattr(research_result, "evidence_items", [])
    recipient_brief_ref = getattr(research_result, "result_hash", f"sha256:{uuid.uuid4().hex[:32]}")
    research_trace_id = getattr(research_result, "trace_id", request.trace_id)
    research_run_id = str(getattr(research_result, "run_id", uuid.uuid4()))

    # Build SourceItems from evidence
    source_items = []
    origin_label_map: Dict[str, str] = {}
    content_hashes: Dict[str, str] = {}

    for i, ev in enumerate(evidence_items):
        sid = f"ev-{i:03d}"
        label = str(getattr(ev, "label", f"evidence_{i}"))
        uri = str(getattr(ev, "uri", getattr(ev, "source_uri", sid)))
        field_ref = str(getattr(ev, "field_ref", "recipient_brief_ref"))
        source_items.append(SourceItem(
            source_id=sid,
            source_type="research",
            label=label,
            uri=uri,
            field_ref=field_ref,
        ))
        origin_label_map[field_ref] = label
        content_hashes[field_ref] = uri

    # Ensure resume_ref always has a source entry
    if request.sender_resume_ref:
        source_items.append(SourceItem(
            source_id="resume-ref",
            source_type="resume",
            label="Sender Resume",
            uri=request.sender_resume_ref,
            field_ref="resume_ref",
        ))
        origin_label_map["resume_ref"] = "Sender Resume"
        content_hashes["resume_ref"] = request.sender_resume_ref

    recipient_seniority = _infer_seniority(request.recipient_class)
    manifest_id = str(uuid.uuid4())
    import hashlib, json as _json
    replay_blob = _json.dumps({
        "recipient_brief_ref": recipient_brief_ref,
        "resume_ref": request.sender_resume_ref,
        "policy_hash": request.sender_policy_hash,
    }, sort_keys=True).encode()
    replay_key = f"r4_lic:{hashlib.sha256(replay_blob).hexdigest()[:16]}"

    return build_manifest(
        manifest_id=manifest_id,
        request_id=request.request_id,
        run_id=request.run_id,
        trace_id=request.trace_id,
        policy_hash=request.sender_policy_hash,
        blueprint_hash=request.sender_blueprint_hash,
        replay_key=replay_key,
        user_profile_ref="",
        resume_ref=request.sender_resume_ref,
        target_role_ref=getattr(research_result, "jd_hash", ""),
        job_description_ref=getattr(research_result, "jd_uri", ""),
        application_status="none",
        company_brief_ref=getattr(research_result, "company_brief_hash", ""),
        recipient_brief_ref=recipient_brief_ref,
        relationship_context_ref="",
        channel=request.channel,
        outreach_mode=request.outreach_mode,
        recipient_class=request.recipient_class,
        recipient_seniority=recipient_seniority,
        relationship_distance=request.relationship_distance,
        source_items=source_items,
        origin_label_map=origin_label_map,
        content_hashes=content_hashes,
        freshness_status="fresh",
        unsupported_fact_flags=[],
        claim_permission_map={},
        proof_mode="none",
        personalization_mode="recipient",
        omission_policy="omit_unsupported",
        confidence_score=confidence,
        send_mode="draft_only",
        personalization_confidence=confidence,
        required_hitl_flags=[],
        audit_refs=[research_trace_id, research_run_id],
    )


def _infer_seniority(recipient_class: str) -> str:
    """Map recipient_class to canonical seniority string."""
    _map = {
        "C_LEVEL": "C_LEVEL",
        "CTO": "C_LEVEL",
        "EXECUTIVE": "VP",
        "VP_ENG": "VP",
        "HIRING_MANAGER": "DIRECTOR",
        "SENIOR_TA": "MANAGER",
        "RECRUITER": "IC",
        "REFERRAL_CONTACT": "IC",
    }
    return _map.get(recipient_class.upper(), "IC")
