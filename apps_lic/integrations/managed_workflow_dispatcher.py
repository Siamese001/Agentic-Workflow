"""Managed workflow dispatcher for apps_lic briefing generation."""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
import uuid
from typing import Any

from apps_lic.engines.archetype_tone_selector import ArchetypeToneSelector
from apps_lic.engines.multi_touch_sequencer import MultiTouchSequencer
from apps_lic.engines.mutual_network_engine import MutualNetworkEngine
from apps_lic.engines.narrative_arc_engine import NarrativeArcEngine
from apps_lic.engines.resurfacing_detector import ResurfacingDetector
from apps_lic.integrations.apps_research_bridge import AppsResearchBridge
from apps_lic.integrations.briefing_quality_gate import (
    BriefingQualityDecision,
    BriefingQualityGate,
)
from apps_lic.integrations.preloaded_outreach_context_manifest import (
    SourceItem,
    build_manifest,
    validate_briefing_ready,
)
from apps_lic.integrations.research_reason_codes import (
    APPS_RESEARCH_BLOCKED,
    APPS_RESEARCH_DEPRECATED,
    APPS_RESEARCH_EMPTY,
    APPS_RESEARCH_FAILED,
    APPS_RESEARCH_STALE,
    APPS_RESEARCH_WEAK_SUPPORT,
    RESEARCH_FAILURE_REASON_CODES,
    ResearchFailureReason,
)


@dataclass(frozen=True)
class RequestForBriefing:
    """Request envelope for managed research delegation."""

    request_id: str
    run_id: str
    trace_id: str
    recipient_class: str
    recipient_name: str
    company_name: str
    job_title: str
    channel: str
    outreach_mode: str
    relationship_distance: str
    sender_resume_ref: str
    sender_policy_hash: str
    sender_blueprint_hash: str
    research_authorized: bool
    research_capability_ref: str
    freshness_ttl_days: int = 30
    min_confidence_threshold: float = 0.70
    audit_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class DispatchFailurePacket:
    """Terminal fail-closed result for managed research requests."""

    request_id: str
    run_id: str
    trace_id: str
    r5_reason_code: str
    detail: str = ""
    dispatch_duration_ms: float = 0.0
    is_terminal: bool = True


@dataclass(frozen=True)
class BriefingReady:
    """Success result produced after a managed research delegation."""

    request_id: str
    run_id: str
    trace_id: str
    manifest: Any
    research_run_id: str
    research_evidence_count: int
    confidence_score: float
    dispatch_duration_ms: float
    audit_refs: tuple[str, ...] = field(default_factory=tuple)
    evidence_lineage: tuple[dict[str, Any], ...] = field(default_factory=tuple)
    quality_decision: BriefingQualityDecision | None = None
    arc_decision: Any | None = None
    tone_decision: Any | None = None
    touch_decision: Any | None = None
    resurfacing_decision: Any | None = None
    mutual_network_signal: Any | None = None


def _utc_ms() -> float:
    return time.time() * 1000.0


def _stable_hash(*parts: Any) -> str:
    payload = json.dumps([str(part) for part in parts], sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _env_flag(name: str) -> bool:
    value = os.environ.get(name, "").strip().lower()
    return value not in {"", "0", "false", "no", "off"}


def _coerce_bool(value: Any) -> bool:
    return bool(value)


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_str(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def _iter_evidence_items(research_result: Any) -> list[Any]:
    items = getattr(research_result, "evidence_items", None)
    if items is None:
        items = getattr(research_result, "items", None)
    if not items:
        return []
    return list(items)


def _source_item_from_evidence(
    item: Any,
    *,
    index: int,
    default_field_ref: str,
) -> SourceItem:
    source_id = _coerce_str(getattr(item, "source_id", None), default=f"ev-{index}")
    label = _coerce_str(getattr(item, "label", None), default=f"evidence_{index}")
    uri = _coerce_str(
        getattr(item, "uri", None) or getattr(item, "source_uri", None),
        default=f"sha256:{_stable_hash(source_id, label, index)}",
    )
    source_type = _coerce_str(getattr(item, "source_type", None), default="research")
    field_ref = _coerce_str(getattr(item, "field_ref", None), default=default_field_ref)
    return SourceItem(
        source_id=source_id,
        source_type=source_type,
        label=label,
        uri=uri,
        field_ref=field_ref,
    )


def _recipient_seniority(recipient_class: str) -> str:
    rc = str(recipient_class or "").upper()
    if rc in {"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"}:
        return "C_LEVEL"
    if rc == "HIRING_MANAGER":
        return "MANAGER"
    if rc in {"RECRUITER", "SENIOR_TA", "REFERRAL_CONTACT"}:
        return "IC"
    return "IC"


def _build_manifest(
    *,
    request: RequestForBriefing,
    research_result: Any,
    evidence_items: list[Any],
) -> Any:
    confidence_score = _coerce_float(getattr(research_result, "confidence_score", None), 0.0)
    company_brief_hash = _coerce_str(
        getattr(research_result, "company_brief_hash", None)
        or getattr(research_result, "result_hash", None),
        default=f"sha256:{_stable_hash(request.company_name, request.job_title, request.request_id)}",
    )
    recipient_brief_ref = _coerce_str(
        getattr(research_result, "result_hash", None),
        default=company_brief_hash,
    )
    source_items = [
        _source_item_from_evidence(
            item,
            index=idx,
            default_field_ref="recipient_brief_ref",
        )
        for idx, item in enumerate(evidence_items)
    ]

    origin_label_map = {
        "resume_ref": "sender_resume",
        "job_description_ref": "job_description",
        "company_brief_ref": "company_research",
        "recipient_brief_ref": "recipient_research",
        "relationship_context_ref": "relationship_context",
    }
    content_hashes = {
        "resume_ref": f"sha256:{_stable_hash(request.sender_resume_ref)}",
        "job_description_ref": f"sha256:{_stable_hash(request.company_name, request.job_title, request.trace_id)}",
        "company_brief_ref": f"sha256:{_stable_hash(company_brief_hash)}",
        "recipient_brief_ref": f"sha256:{_stable_hash(recipient_brief_ref, request.recipient_name)}",
        "relationship_context_ref": f"sha256:{_stable_hash(request.relationship_distance, request.recipient_class)}",
    }
    audit_refs = tuple(
        dict.fromkeys(
            [
                *request.audit_refs,
                _coerce_str(getattr(research_result, "audit_ref", None), default=request.trace_id),
            ]
        )
    )

    return build_manifest(
        manifest_id=f"manifest-{_coerce_str(request.run_id, default=request.request_id)}",
        request_id=_coerce_str(request.request_id),
        run_id=_coerce_str(request.run_id),
        trace_id=_coerce_str(request.trace_id),
        policy_hash=_coerce_str(request.sender_policy_hash),
        blueprint_hash=_coerce_str(request.sender_blueprint_hash),
        replay_key=f"{_coerce_str(request.run_id)}:{_coerce_str(request.request_id)}",
        user_profile_ref=_coerce_str(request.sender_resume_ref),
        resume_ref=_coerce_str(request.sender_resume_ref),
        target_role_ref=f"role:{_coerce_str(request.job_title, default='role')}",
        job_description_ref=f"jd:{_coerce_str(request.job_title, default='job')}",
        application_status="none",
        company_brief_ref=company_brief_hash,
        recipient_brief_ref=recipient_brief_ref,
        relationship_context_ref=f"relationship:{_coerce_str(request.relationship_distance, default='cold')}",
        channel=_coerce_str(request.channel, default="email"),
        outreach_mode=_coerce_str(request.outreach_mode, default="cold"),
        recipient_class=_coerce_str(request.recipient_class, default="RECRUITER"),
        recipient_seniority=_recipient_seniority(request.recipient_class),
        relationship_distance=_coerce_str(request.relationship_distance, default="cold"),
        source_items=source_items,
        origin_label_map=origin_label_map,
        content_hashes=content_hashes,
        freshness_status="stale" if _coerce_bool(getattr(research_result, "is_stale", False)) else "fresh",
        unsupported_fact_flags=[],
        claim_permission_map={"default_claim": "allowed"},
        proof_mode="company_brief",
        personalization_mode="role",
        omission_policy="omit_unsupported",
        confidence_score=confidence_score,
        send_mode="draft_only",
        personalization_confidence=confidence_score,
        required_hitl_flags=[],
        audit_refs=list(audit_refs),
    )


def _build_failure(
    request: RequestForBriefing,
    *,
    reason_code: str,
    detail: str,
    start_ms: float,
) -> DispatchFailurePacket:
    return DispatchFailurePacket(
        request_id=_coerce_str(request.request_id, default=f"req-{uuid.uuid4().hex[:8]}"),
        run_id=_coerce_str(request.run_id, default=f"run-{uuid.uuid4().hex[:8]}"),
        trace_id=_coerce_str(request.trace_id),
        r5_reason_code=reason_code,
        detail=detail,
        dispatch_duration_ms=_utc_ms() - start_ms,
        is_terminal=True,
    )


def _select_signal(engine_cls: Any, method_name: str, **kwargs: Any) -> Any | None:
    try:
        engine = engine_cls()
        method = getattr(engine, method_name)
        return method(**kwargs)
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- signal engines must never abort dispatch
        return None


def dispatch_managed_briefing(
    request: RequestForBriefing,
    *,
    bridge: Any | None = None,
) -> DispatchFailurePacket | BriefingReady:
    """Run managed research and attach signal decisions on success."""
    start_ms = _utc_ms()
    bridge = bridge or AppsResearchBridge(capability_ref=request.research_capability_ref)

    if not request.research_authorized:
        return _build_failure(
            request,
            reason_code=APPS_RESEARCH_BLOCKED,
            detail="research_authorized=False; managed research is disabled for this request.",
            start_ms=start_ms,
        )

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
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
        )
    except Exception as exc:  # noqa: BLE001
        return _build_failure(
            request,
            reason_code=APPS_RESEARCH_FAILED,
            detail=f"{type(exc).__name__}: {exc}",
            start_ms=start_ms,
        )

    if _coerce_bool(getattr(research_result, "is_blocked", False)):
        return _build_failure(
            request,
            reason_code=APPS_RESEARCH_BLOCKED,
            detail=_coerce_str(getattr(research_result, "block_reason", None), default="research_result_blocked"),
            start_ms=start_ms,
        )

    evidence_items = _iter_evidence_items(research_result)
    if not evidence_items:
        return _build_failure(
            request,
            reason_code=APPS_RESEARCH_EMPTY,
            detail="research_result.evidence_items is empty",
            start_ms=start_ms,
        )

    quality_bypass = _env_flag("BRIEFING_QUALITY_BYPASS")
    confidence_score = _coerce_float(getattr(research_result, "confidence_score", None), 0.0)

    if not quality_bypass and _coerce_bool(getattr(research_result, "is_stale", False)):
        return _build_failure(
            request,
            reason_code=APPS_RESEARCH_STALE,
            detail="research_result.is_stale=True",
            start_ms=start_ms,
        )

    if not quality_bypass and confidence_score < float(request.min_confidence_threshold):
        return _build_failure(
            request,
            reason_code=APPS_RESEARCH_WEAK_SUPPORT,
            detail=(
                f"confidence_score={confidence_score:.2f} "
                f"< threshold={float(request.min_confidence_threshold):.2f}"
            ),
            start_ms=start_ms,
        )

    manifest = _build_manifest(
        request=request,
        research_result=research_result,
        evidence_items=evidence_items,
    )
    manifest_check = validate_briefing_ready(manifest, allow_stale=quality_bypass)
    if not manifest_check.is_valid:
        return _build_failure(
            request,
            reason_code=manifest_check.r5_reason_code or APPS_RESEARCH_BLOCKED,
            detail=manifest_check.detail,
            start_ms=start_ms,
        )

    quality_decision = BriefingQualityGate().evaluate(
        research_result,
        recipient_class=request.recipient_class,
    )
    if quality_decision.quality_level == "fail" and not quality_bypass:
        return _build_failure(
            request,
            reason_code=quality_decision.r5_reason_code or APPS_RESEARCH_WEAK_SUPPORT,
            detail="; ".join(quality_decision.fail_reasons) or "quality gate failed",
            start_ms=start_ms,
        )

    arc_decision = _select_signal(
        NarrativeArcEngine,
        "select",
        recipient_class=request.recipient_class,
        relationship_distance=request.relationship_distance,
    )
    tone_decision = _select_signal(
        ArchetypeToneSelector,
        "select",
        recipient_class=request.recipient_class,
        relationship_distance=request.relationship_distance,
    )
    touch_decision = _select_signal(
        MultiTouchSequencer,
        "sequence",
        recipient_class=request.recipient_class,
        outreach_history=[],
    )
    resurfacing_decision = _select_signal(
        ResurfacingDetector,
        "detect",
        days_since_last_contact=_coerce_float(getattr(research_result, "age_days", None), default=None),
        prior_response_received=False,
        relationship_distance=request.relationship_distance,
        trigger_event_detected=False,
    )
    mutual_network_signal = _select_signal(
        MutualNetworkEngine,
        "extract",
        connection_items=[],
    )

    audit_refs = tuple(
        dict.fromkeys(
            [
                *request.audit_refs,
                _coerce_str(getattr(research_result, "audit_ref", None), default=request.trace_id),
            ]
        )
    )
    evidence_lineage = tuple(asdict(item) for item in manifest.source_items)

    return BriefingReady(
        request_id=_coerce_str(request.request_id),
        run_id=_coerce_str(request.run_id),
        trace_id=_coerce_str(request.trace_id),
        manifest=manifest,
        research_run_id=_coerce_str(getattr(research_result, "run_id", None), default=request.run_id),
        research_evidence_count=len(evidence_items),
        confidence_score=confidence_score,
        dispatch_duration_ms=_utc_ms() - start_ms,
        audit_refs=audit_refs,
        evidence_lineage=evidence_lineage,
        quality_decision=quality_decision,
        arc_decision=arc_decision,
        tone_decision=tone_decision,
        touch_decision=touch_decision,
        resurfacing_decision=resurfacing_decision,
        mutual_network_signal=mutual_network_signal,
    )


__all__ = [
    "APPS_RESEARCH_DEPRECATED",
    "BriefingReady",
    "DispatchFailurePacket",
    "RESEARCH_FAILURE_REASON_CODES",
    "RequestForBriefing",
    "ResearchFailureReason",
    "dispatch_managed_briefing",
]
