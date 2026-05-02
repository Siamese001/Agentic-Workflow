"""Extended run-report types for apps_rg narrative pipeline.

Adds:
  - per_section_verdicts: judge verdicts per HOP-4A..4H
  - gate_failures: list of failed hard gates by section
  - degraded_sections: medium-tier sections that fell through fail-soft
  - narrative_candidates_path: archive directory for ensemble candidates
  - company_brief_provenance: where the CompanyBrief came from
  - jd_keyword_coverage: hit/miss counts post-narrative

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P7.3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SectionVerdict:
    section_id: str
    tier: str  # "critical" | "medium" | "skip"
    accepted: bool
    composite: float
    chosen_source: str  # "pool" | "ensemble" | "judge_only" | "deterministic" | "fallback"
    failed_gate: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "section_id": self.section_id,
            "tier": self.tier,
            "accepted": self.accepted,
            "composite": round(self.composite, 4),
            "chosen_source": self.chosen_source,
            "failed_gate": self.failed_gate,
        }


@dataclass
class NarrativeRunReport:
    per_section_verdicts: List[SectionVerdict] = field(default_factory=list)
    degraded_sections: List[str] = field(default_factory=list)
    gate_failures: List[Dict[str, Any]] = field(default_factory=list)
    narrative_candidates_path: Optional[str] = None
    company_brief_provenance: Optional[Dict[str, Any]] = None
    jd_keyword_coverage: Optional[Dict[str, Any]] = None
    pool_first_hit_rate: Optional[float] = None

    def add_verdict(self, verdict: SectionVerdict) -> None:
        self.per_section_verdicts.append(verdict)
        if verdict.tier == "medium" and not verdict.accepted:
            if verdict.section_id not in self.degraded_sections:
                self.degraded_sections.append(verdict.section_id)
        if verdict.failed_gate:
            self.gate_failures.append(
                {
                    "section_id": verdict.section_id,
                    "failed_gate": verdict.failed_gate,
                    "tier": verdict.tier,
                }
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "per_section_verdicts": [v.to_dict() for v in self.per_section_verdicts],
            "degraded_sections": list(self.degraded_sections),
            "gate_failures": list(self.gate_failures),
            "narrative_candidates_path": self.narrative_candidates_path,
            "company_brief_provenance": self.company_brief_provenance,
            "jd_keyword_coverage": self.jd_keyword_coverage,
            "pool_first_hit_rate": self.pool_first_hit_rate,
        }


__all__ = ["NarrativeRunReport", "SectionVerdict"]
