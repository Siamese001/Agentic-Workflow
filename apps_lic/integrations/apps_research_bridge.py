"""apps_lic research bridge compatibility layer.

The base bridge remains deprecated and fail-closed for live delegation.
``MockAppsResearchBridge`` is the test fixture used by the managed-workflow
dispatcher; it returns a deterministic ResearchResult when not explicitly
blocked.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass
from typing import Any

from apps_lic.integrations.research_reason_codes import APPS_RESEARCH_DEPRECATED


def _stable_hash(*parts: Any) -> str:
    """Return a deterministic sha256 hex digest over the provided parts."""
    payload = json.dumps([str(part) for part in parts], sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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
    """Structured result returned by the apps_lic research bridge."""

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
    """Deterministic bridge fixture used by managed-workflow tests."""

    SUPPORTED_CAPABILITIES = frozenset({"apps_research.v1", "apps_research.v2"})

    def __init__(
        self,
        *,
        is_blocked: bool = False,
        block_reason: str = "",
        is_stale: bool = False,
        age_days: float = 0.0,
        evidence_items: list[EvidenceItem] | None = None,
        confidence_score: float = 0.85,
        capability_ref: str = "apps_research.v1",
    ) -> None:
        super().__init__(capability_ref=capability_ref)
        self._mock_is_blocked = is_blocked
        self._mock_block_reason = block_reason
        self._mock_is_stale = is_stale
        self._mock_age_days = age_days
        if evidence_items is None:
            evidence_items = [
                EvidenceItem(
                    source_id="mock-ev-000",
                    label="Mock research insight",
                    uri="sha256:mock-ev-000",
                    source_type="research",
                    field_ref="recipient_brief_ref",
                    confidence=confidence_score,
                )
            ]
        self._mock_evidence = tuple(evidence_items)
        self._mock_confidence = confidence_score

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
        t_start = time.time() * 1000.0
        bridge_trace_id = f"bridge:{self._bridge_id}:{trace_id}"

        if capability_ref not in self.SUPPORTED_CAPABILITIES:
            return ResearchResult(
                run_id=run_id,
                trace_id=bridge_trace_id,
                request_id=request_id,
                is_blocked=True,
                block_reason=f"Unsupported capability_ref={capability_ref!r}",
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

        if self._mock_is_blocked:
            return ResearchResult(
                run_id=run_id,
                trace_id=bridge_trace_id,
                request_id=request_id,
                is_blocked=True,
                block_reason=self._mock_block_reason or APPS_RESEARCH_DEPRECATED,
                is_stale=self._mock_is_stale,
                age_days=self._mock_age_days,
                evidence_items=(),
                confidence_score=self._mock_confidence,
                result_hash="",
                jd_hash="",
                jd_uri="",
                company_brief_hash="",
                fetch_duration_ms=time.time() * 1000.0 - t_start,
                audit_ref=bridge_trace_id,
            )

        result_hash = f"sha256:{_stable_hash(self._bridge_id, request_id, run_id, company_name, job_title, capability_ref)}"
        jd_hash = f"sha256:{_stable_hash(company_name, job_title, relationship_distance, outreach_mode)}"
        jd_uri = f"jd://{company_name}/{job_title}".replace(" ", "_")

        return ResearchResult(
            run_id=run_id,
            trace_id=bridge_trace_id,
            request_id=request_id,
            is_blocked=False,
            block_reason="",
            is_stale=self._mock_is_stale,
            age_days=self._mock_age_days,
            evidence_items=self._mock_evidence,
            confidence_score=self._mock_confidence,
            result_hash=result_hash,
            jd_hash=jd_hash,
            jd_uri=jd_uri,
            company_brief_hash=result_hash,
            fetch_duration_ms=time.time() * 1000.0 - t_start,
            audit_ref=bridge_trace_id,
        )


__all__ = [
    "APPS_RESEARCH_DEPRECATED",
    "AppsResearchBridge",
    "EvidenceItem",
    "MockAppsResearchBridge",
    "ResearchResult",
]
