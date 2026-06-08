"""Deprecated research bridge compatibility shim for apps_lic.

The live apps_lic product path no longer delegates to the research app. This
module remains importable for old callers, but every fetch is terminally
blocked with ``APPS_RESEARCH_DEPRECATED`` and no external app is imported.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

APPS_RESEARCH_DEPRECATED = "APPS_RESEARCH_DEPRECATED"


@dataclass(frozen=True)
class EvidenceItem:
    """Legacy evidence item shape retained for import compatibility."""

    source_id: str
    label: str
    uri: str
    source_type: str
    field_ref: str
    confidence: float = 0.0


@dataclass(frozen=True)
class ResearchResult:
    """Structured blocked result from the deprecated bridge."""

    run_id: str
    trace_id: str
    request_id: str
    is_blocked: bool
    block_reason: str
    is_stale: bool
    age_days: float
    evidence_items: tuple[EvidenceItem, ...]
    confidence_score: float
    result_hash: str
    jd_hash: str
    jd_uri: str
    company_brief_hash: str
    fetch_duration_ms: float
    audit_ref: str


class AppsResearchBridge:
    """Import-compatible bridge that always blocks deprecated research."""

    SUPPORTED_CAPABILITIES = frozenset()

    def __init__(self, capability_ref: str = "apps_research.v1") -> None:
        self._capability_ref = capability_ref
        self._bridge_id = f"lic_research_bridge:{uuid.uuid4().hex[:8]}"

    def fetch(
        self,
        *,
        recipient_class: str,
        recipient_name: str,
        company_name: str,
        job_title: str,
        channel: str,
        outreach_mode: str,
        relationship_distance: str,
        capability_ref: str,
        request_id: str,
        run_id: str,
        trace_id: str,
    ) -> ResearchResult:
        """Return a blocked result. Never invokes another app."""
        t_start = time.time() * 1000.0
        bridge_trace_id = f"bridge:{self._bridge_id}:{trace_id}"
        return ResearchResult(
            run_id=run_id,
            trace_id=bridge_trace_id,
            request_id=request_id,
            is_blocked=True,
            block_reason=APPS_RESEARCH_DEPRECATED,
            is_stale=False,
            age_days=0.0,
            evidence_items=(),
            confidence_score=0.0,
            result_hash="",
            jd_hash="",
            jd_uri="",
            company_brief_hash="",
            fetch_duration_ms=time.time() * 1000.0 - t_start,
            audit_ref=bridge_trace_id,
        )


class MockAppsResearchBridge(AppsResearchBridge):
    """Legacy mock name retained for imports; behavior is always blocked."""

    def __init__(
        self,
        *,
        is_blocked: bool = True,
        block_reason: str = APPS_RESEARCH_DEPRECATED,
        is_stale: bool = False,
        age_days: float = 0.0,
        evidence_items: list[EvidenceItem] | None = None,
        confidence_score: float = 0.0,
        capability_ref: str = "apps_research.v1",
    ) -> None:
        super().__init__(capability_ref=capability_ref)
        self._compat_kwargs = {
            "is_blocked": is_blocked,
            "block_reason": block_reason,
            "is_stale": is_stale,
            "age_days": age_days,
            "evidence_items": tuple(evidence_items or ()),
            "confidence_score": confidence_score,
        }


__all__ = [
    "APPS_RESEARCH_DEPRECATED",
    "AppsResearchBridge",
    "EvidenceItem",
    "MockAppsResearchBridge",
    "ResearchResult",
]
