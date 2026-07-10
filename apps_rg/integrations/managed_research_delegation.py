"""Managed apps_research delegation for apps_rg R3R4 whole-run briefing."""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from apps_rg.integrations.apps_research_bridge import ResearchResult


class ResearchFailureReason(str, Enum):
    APPS_RESEARCH_FAILED = "APPS_RESEARCH_FAILED"
    APPS_RESEARCH_EMPTY = "APPS_RESEARCH_EMPTY"
    APPS_RESEARCH_BLOCKED = "APPS_RESEARCH_BLOCKED"
    APPS_RESEARCH_STALE = "APPS_RESEARCH_STALE"
    APPS_RESEARCH_WEAK_SUPPORT = "APPS_RESEARCH_WEAK_SUPPORT"
    APPS_RESEARCH_ARTIFACT_MISSING = "APPS_RESEARCH_ARTIFACT_MISSING"


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
    job_description_ref: str = ""
    job_description_text: str = ""


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
    apps_research_handoff_envelope: dict[str, Any]
    dispatch_duration_ms: float
    research_briefing_path: str = ""


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


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return True


def _validate_persisted_research_artifacts(
    result: ResearchResult,
) -> tuple[bool, str, dict[str, str]]:
    raw_dir = str(result.research_artifact_dir or "").strip()
    if not raw_dir:
        return False, "missing research_artifact_dir", {}
    run_dir = Path(raw_dir)
    if not run_dir.is_dir():
        return False, f"research_artifact_dir is not a directory: {raw_dir}", {}
    raw_brief = str(result.briefing_artifact_path or "").strip()
    if not raw_brief:
        return False, "missing briefing_artifact_path", {}
    briefing_path = Path(raw_brief)
    company_brief_path = run_dir / "company_brief.json"
    envelope_path = run_dir / "apps_research_briefing_envelope.json"
    metadata_path = run_dir / "run_metadata.json"
    required = (
        briefing_path,
        company_brief_path,
        envelope_path,
        metadata_path,
    )
    for path in required:
        if not _is_within(path, run_dir):
            return False, f"producer artifact escapes research_artifact_dir: {path}", {}
        if not path.is_file() or path.stat().st_size <= 0:
            return False, f"missing persisted apps_research artifact: {path}", {}
    try:
        persisted_text = briefing_path.read_text(encoding="utf-8").strip()
        persisted_envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"unreadable persisted apps_research artifact: {type(exc).__name__}", {}
    if persisted_text != str(result.company_brief_text or "").strip():
        return False, "persisted briefing text does not match bridge result", {}
    if not isinstance(persisted_envelope, dict):
        return False, "persisted apps_research envelope is not an object", {}
    expected_sha = hashlib.sha256(persisted_text.encode("utf-8")).hexdigest()
    if str(persisted_envelope.get("brief_sha256") or "") != expected_sha:
        return False, "persisted apps_research briefing digest mismatch", {}
    if Path(str(persisted_envelope.get("briefing_path") or "")).resolve() != briefing_path.resolve():
        return False, "persisted envelope briefing_path mismatch", {}
    if Path(str(persisted_envelope.get("company_brief_path") or "")).resolve() != company_brief_path.resolve():
        return False, "persisted envelope company_brief_path mismatch", {}
    if persisted_envelope != (result.apps_research_handoff_envelope or {}):
        return False, "bridge envelope differs from persisted producer envelope", {}
    return True, "ok", {
        "run_dir": str(run_dir.resolve()),
        "briefing_path": str(briefing_path.resolve()),
        "company_brief_path": str(company_brief_path.resolve()),
        "envelope_path": str(envelope_path.resolve()),
        "metadata_path": str(metadata_path.resolve()),
    }


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
            job_description_ref=request.job_description_ref,
            job_description_text=request.job_description_text,
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
    artifacts_valid, artifact_detail, artifact_refs = _validate_persisted_research_artifacts(
        research_result
    )
    if not artifacts_valid:
        return ResearchDispatchFailure(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_ARTIFACT_MISSING.value,
            detail=artifact_detail,
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

    # Fail closed: the delegated briefing MUST be a sealed, contract-valid
    # company_brief_text. No evidence-label or generic-heading fallback.
    briefing_text = str(research_result.company_brief_text or "").strip()
    if not briefing_text:
        return ResearchDispatchFailure(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_EMPTY.value,
            detail="missing company_brief_text (no valid delegated briefing)",
            dispatch_duration_ms=_utc_ms() - t_start,
        )
    handoff_envelope = research_result.apps_research_handoff_envelope
    if not isinstance(handoff_envelope, dict) or not handoff_envelope:
        return ResearchDispatchFailure(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_BLOCKED.value,
            detail="missing_apps_research_handoff_envelope",
            dispatch_duration_ms=_utc_ms() - t_start,
        )
    auth = handoff_envelope.get("apps_research_x1_x3_authorization")
    x2 = auth.get("x2") if isinstance(auth, dict) and isinstance(auth.get("x2"), dict) else {}
    x3 = auth.get("x3") if isinstance(auth, dict) and isinstance(auth.get("x3"), dict) else {}
    if x2.get("status") != "PASS" or x2.get("model_backed") is not True:
        return ResearchDispatchFailure(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_BLOCKED.value,
            detail="apps_research_x2_judge_not_model_backed_pass",
            dispatch_duration_ms=_utc_ms() - t_start,
        )
    if x3.get("status") != "PASS" or x3.get("disposition") != "ALLOW":
        return ResearchDispatchFailure(
            request_id=request.request_id,
            run_id=request.run_id,
            trace_id=request.trace_id,
            r5_reason_code=ResearchFailureReason.APPS_RESEARCH_BLOCKED.value,
            detail="apps_research_x3_not_allow",
            dispatch_duration_ms=_utc_ms() - t_start,
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
        apps_research_handoff_envelope=handoff_envelope,
        dispatch_duration_ms=_utc_ms() - t_start,
        research_briefing_path=artifact_refs["briefing_path"],
    )


__all__ = [
    "RequestForResumeBriefing",
    "ResearchDispatchFailure",
    "ResearchFailureReason",
    "ResumeBriefingReady",
    "dispatch_resume_research_briefing",
]
