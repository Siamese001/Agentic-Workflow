"""Deprecated managed workflow dispatcher compatibility shim.

The live apps_lic path is LinkedIn recruiter drafting through canonical
dispatch. Managed research delegation is disabled. This module is retained for
legacy imports only and never returns a success-producing briefing.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

APPS_RESEARCH_DEPRECATED = "APPS_RESEARCH_DEPRECATED"

RESEARCH_FAILURE_REASON_CODES = frozenset({APPS_RESEARCH_DEPRECATED})


class ResearchFailureReason(str, Enum):
    """Terminal reason emitted for deprecated managed research."""

    APPS_RESEARCH_DEPRECATED = "APPS_RESEARCH_DEPRECATED"


@dataclass(frozen=True)
class RequestForBriefing:
    """Legacy request shape retained for import compatibility."""

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
    """Terminal fail-closed result for deprecated managed research."""

    request_id: str
    run_id: str
    trace_id: str
    r5_reason_code: str
    detail: str = ""
    dispatch_duration_ms: float = 0.0
    is_terminal: bool = True


@dataclass(frozen=True)
class BriefingReady:
    """Legacy success shape retained for imports; dispatcher never returns it."""

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


def _utc_ms() -> float:
    return time.time() * 1000.0


def dispatch_managed_briefing(
    request: RequestForBriefing,
    *,
    bridge: Any | None = None,
) -> DispatchFailurePacket:
    """Fail closed for all deprecated managed briefing requests."""
    start_ms = _utc_ms()
    return DispatchFailurePacket(
        request_id=request.request_id or f"req-{uuid.uuid4().hex[:8]}",
        run_id=request.run_id or f"run-{uuid.uuid4().hex[:8]}",
        trace_id=request.trace_id,
        r5_reason_code=APPS_RESEARCH_DEPRECATED,
        detail="apps_lic managed research delegation is deprecated and disabled.",
        dispatch_duration_ms=_utc_ms() - start_ms,
        is_terminal=True,
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
