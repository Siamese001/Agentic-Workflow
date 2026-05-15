"""apps_rg C0 evidence trace map — per-section evidence provenance."""
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
    """Evidence provenance for a single resume section."""

    section_id: str
    evidence_item_ids: list[str]
    source_classes: list[str]
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
