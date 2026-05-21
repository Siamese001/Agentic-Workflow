"""Managed apps_research delegation for apps_rg R3R4 whole-run briefing."""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

from apps_rg.integrations.apps_research_bridge import ResearchResult


class ResearchFailureReason(str, Enum):
    APPS_RESEARCH_FAILED = "APPS_RESEARCH_FAILED"
    APPS_RESEARCH_EMPTY = "APPS_RESEARCH_EMPTY"
    APPS_RESEARCH_BLOCKED = "APPS_RESEARCH_BLOCKED"
    APPS_RESEARCH_STALE = "APPS_RESEARCH_STALE"
    APPS_RESEARCH_WEAK_SUPPORT = "APPS_RESEARCH_WEAK_SUPPORT"


@dataclass(frozen=True)
class RequestForResumeBriefing:
    request_id: str
    run_id: str
    trace_id: str
    company_name: str
    job_title: str
    research_authorized: bool
    research_capability_ref: str = "apps_research.v1"
    freshness_ttl_days: int = 7
    min_confidence_threshold: float = 0.60


@dataclass(frozen=True)
class ResumeBriefingReady:
    request_id: str
    run_id: str
    trace_id: str
    briefing_text: str
    research_run_id: str
    research_evidence_count: int
    confidence_score: float
    research_artifact_dir: str
    result_hash: str
    evidence_lineage: tuple[dict[str, Any], ...]
    dispatch_duration_ms: float


@dataclass(frozen=True)
class ResearchDispatchFailure:
    request_id: str
    run_id: str
    trace_id: str
    r5_reason_code: str
    detail: str
    dispatch_duration_ms: float


def _utc_ms() -> float:
    return time.time() * 1000.0


def dispatch_resume_research_briefing(
    request: RequestForResumeBriefing,
    *,
    bridge: Any,
) -> ResumeBriefingReady | ResearchDispatchFailure:
    t_start = _utc_ms()
    if not request.research_authorized:
        return ResearchDispatchFailure(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_BLOCKED.value,
            detail="research_authorized=False",
            dispatch_duration_ms=_utc_ms() - t_start,
        )
    try:
        research_result = bridge.fetch(
            company_name=request.company_name,
            job_title=request.job_title,
            capability_ref=request.research_capability_ref,
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
        )
    except Exception as exc:  # noqa: BLE001
        return ResearchDispatchFailure(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_FAILED.value,
            detail=f"{type(exc).__name__}: {exc}",
            dispatch_duration_ms=_utc_ms() - t_start,
        )

    if not isinstance(research_result, ResearchResult):
        return ResearchDispatchFailure(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_FAILED.value,
            detail="bridge returned unexpected type",
            dispatch_duration_ms=_utc_ms() - t_start,
        )

    if research_result.is_blocked:
        return ResearchDispatchFailure(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_BLOCKED.value,
            detail=research_result.block_reason or "blocked",
            dispatch_duration_ms=_utc_ms() - t_start,
        )
    if not research_result.evidence_items:
        return ResearchDispatchFailure(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_EMPTY.value,
            detail="zero evidence_items",
            dispatch_duration_ms=_utc_ms() - t_start,
        )
    if research_result.is_stale:
        return ResearchDispatchFailure(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_STALE.value,
            detail=f"stale age_days={research_result.age_days}",
            dispatch_duration_ms=_utc_ms() - t_start,
        )
    if research_result.confidence_score < request.min_confidence_threshold:
        return ResearchDispatchFailure(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_WEAK_SUPPORT.value,
            detail=(
                f"confidence={research_result.confidence_score:.2f} "
                f"< {request.min_confidence_threshold:.2f}"
            ),
            dispatch_duration_ms=_utc_ms() - t_start,
        )

    briefing_text = str(research_result.company_brief_text or "").strip()
    if not briefing_text:
        lines = [
            f"- {getattr(ev, 'label', '')}: {getattr(ev, 'uri', '')}"
            for ev in research_result.evidence_items
        ]
        briefing_text = (
            f"# Company research briefing: {request.company_name}\n\n"
            + "\n".join(lines)
        )

    lineage = tuple(
        {
            "source_id": getattr(ev, "source_id", ""),
            "label": getattr(ev, "label", ""),
            "uri": getattr(ev, "uri", ""),
            "source_type": getattr(ev, "source_type", ""),
            "field_ref": getattr(ev, "field_ref", ""),
            "confidence": float(getattr(ev, "confidence", 0.0)),
        }
        for ev in research_result.evidence_items
    )
    return ResumeBriefingReady(
        request_id=request.request_id,
        run_id=request.run_id,
        trace_id=request.trace_id,
        briefing_text=briefing_text,
        research_run_id=str(research_result.run_id or uuid.uuid4()),
        research_evidence_count=len(research_result.evidence_items),
        confidence_score=research_result.confidence_score,
        research_artifact_dir=str(research_result.research_artifact_dir or ""),
        result_hash=research_result.result_hash,
        evidence_lineage=lineage,
        dispatch_duration_ms=_utc_ms() - t_start,
    )


__all__ = [
    "RequestForResumeBriefing",
    "ResearchDispatchFailure",
    "ResearchFailureReason",
    "ResumeBriefingReady",
    "dispatch_resume_research_briefing",
]
