"""apps_rg C0 binding — per-section evidence provenance trace map.

This module is part of the apps_rg C0 binding / integration path (retrieval wiring
and trace shapes accompanying FinalEvidenceContract). Generic FEC schema and C0
machinery remain in agentic_core.

See ``FinalEvidenceContract`` in agentic_core — this map is not a substitute FEC.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "AppsRgEvidenceTraceMap",
    "SectionEvidenceTrace",
    "C0_BEHAVIOR_CONSTRAINTS",
]

C0_BEHAVIOR_CONSTRAINTS: dict[str, bool] = {
    "c0_is_read_only": True,
    "c0_cannot_write_l4": True,
    "c0_cannot_modify_source_resume": True,
    "c0_evidence_data_only_slot": True,
}


@dataclass(frozen=True)
class SectionEvidenceTrace:
    """Evidence provenance for a single resume section (apps_rg trace companion).

    W7 fields document retrieval provenance alongside core FEC; optional dense /
    sparse seam fields remain for backward compatibility with older bindings.
    """

    section_id: str
    section_type: str = ""
    source_resume_hash: str = ""
    jd_hash: str = ""
    briefing_hash: str = ""
    retrieved_chunk_refs: tuple[str, ...] = ()
    retrieved_chunk_hashes: tuple[str, ...] = ()
    source_span_refs: tuple[dict[str, Any], ...] = ()
    claim_refs: tuple[dict[str, Any], ...] = ()
    blocked_claims: tuple[dict[str, Any], ...] = ()
    injection_risk: str = "UNKNOWN"
    support_status: str = "UNKNOWN"
    evidence_item_ids: tuple[str, ...] = ()
    source_classes: tuple[str, ...] = ()
    retrieval_query: str = ""
    retrieval_score: float = 0.0
    slot: str = "c0_evidence_data_only"


@dataclass
class AppsRgEvidenceTraceMap:
    """Maps each resume section to its C0 evidence items."""

    run_id: str
    traces: dict[str, SectionEvidenceTrace] = field(default_factory=dict)
    total_evidence_items: int = 0
    briefing_mode: str = ""

    def add_trace(self, trace: SectionEvidenceTrace) -> None:
        self.traces[trace.section_id] = trace

    def get_trace(self, section_id: str) -> SectionEvidenceTrace | None:
        return self.traces.get(section_id)

    def section_ids(self) -> list[str]:
        return list(self.traces.keys())
