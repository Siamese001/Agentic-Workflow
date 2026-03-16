"""
_emit_reads_through("l4", "research_types", "urg_read_1")
_emit_reads_through("l4", "research_types", "urg_read_2")
_emit_reads_through("l4", "research_types", "urg_read_3")
_emit_reads_through("l4", "research_types", "urg_read_4")
_emit_reads_through("l4", "research_types", "urg_read_5")
_emit_reads_through("l4", "research_types", "urg_read_6")
_emit_reads_through("l4", "research_types", "urg_read_7")
_emit_reads_through("l4", "research_types", "urg_read_8")
_emit_reads_through("l4", "research_types", "urg_read_9")
_emit_reads_through("l4", "research_types", "urg_read_10")
_emit_reads_through("l4", "research_types", "urg_read_11")
_emit_reads_through("l4", "research_types", "urg_read_12")
_emit_reads_through("l4", "research_types", "urg_read_13")
_emit_reads_through("l4", "research_types", "urg_read_14")
_emit_reads_through("l4", "research_types", "urg_read_15")
_emit_reads_through("l4", "research_types", "urg_read_16")
_emit_reads_through("l4", "research_types", "urg_read_17")
_emit_reads_through("l4", "research_types", "urg_read_18")
_emit_reads_through("l4", "research_types", "urg_read_19")
_emit_reads_through("l4", "research_types", "urg_read_20")
_emit_reads_through("l4", "research_types", "urg_read_21")
_emit_reads_through("l4", "research_types", "urg_read_22")
_emit_reads_through("l4", "research_types", "urg_read_23")
_emit_reads_through("l4", "research_types", "urg_read_24")
_emit_reads_through("l4", "research_types", "urg_read_25")
_emit_reads_through("l4", "research_types", "urg_read_26")
_emit_reads_through("l4", "research_types", "urg_read_27")
_emit_reads_through("l4", "research_types", "urg_read_28")
_emit_reads_through("l4", "research_types", "urg_read_29")
_emit_reads_through("l4", "research_types", "urg_read_30")
_emit_reads_through("l4", "research_types", "urg_read_31")
_emit_reads_through("l4", "research_types", "urg_read_32")
_emit_reads_through("l4", "research_types", "urg_read_33")
_emit_reads_through("l4", "research_types", "urg_read_34")
_emit_reads_through("l4", "research_types", "urg_read_35")
_emit_reads_through("l4", "research_types", "urg_read_36")
_emit_reads_through("l4", "research_types", "urg_read_37")
_emit_reads_through("l4", "research_types", "urg_read_38")
_emit_reads_through("l4", "research_types", "urg_read_39")
_emit_reads_through("l4", "research_types", "urg_read_40")
_emit_reads_through("l4", "research_types", "urg_read_41")
_emit_reads_through("l4", "research_types", "urg_read_42")
_emit_reads_through("l4", "research_types", "urg_read_43")
_emit_reads_through("l4", "research_types", "urg_read_44")
_emit_reads_through("l4", "research_types", "urg_read_45")
_emit_reads_through("l4", "research_types", "urg_read_46")
_emit_reads_through("l4", "research_types", "urg_read_47")
_emit_reads_through("l4", "research_types", "urg_read_48")
_emit_reads_through("l4", "research_types", "urg_read_49")
_emit_reads_through("l4", "research_types", "urg_read_50")
_emit_reads_through("l4", "research_types", "urg_read_51")
_emit_reads_through("l4", "research_types", "urg_read_52")
_emit_reads_through("l4", "research_types", "urg_read_53")
_emit_reads_through("l4", "research_types", "urg_read_54")
_emit_reads_through("l4", "research_types", "urg_read_55")
_emit_reads_through("l4", "research_types", "urg_read_56")
_emit_reads_through("l4", "research_types", "urg_read_57")
_emit_reads_through("l4", "research_types", "urg_read_58")
_emit_reads_through("l4", "research_types", "urg_read_59")
_emit_reads_through("l4", "research_types", "urg_read_60")
_emit_reads_through("l4", "research_types", "urg_read_61")
_emit_reads_through("l4", "research_types", "urg_read_62")
_emit_reads_through("l4", "research_types", "urg_read_63")
_emit_reads_through("l4", "research_types", "urg_read_64")
_emit_reads_through("l4", "research_types", "urg_read_65")
_emit_reads_through("l4", "research_types", "urg_read_66")
_emit_reads_through("l4", "research_types", "urg_read_67")
apps_research domain types — Autonomous Research Engine.

All types are frozen dataclasses. Every artifact carries provenance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResearchStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    GATE_CHECKING = "gate_checking"
    COMPLETE = "complete"
    FAILED = "failed"
    DRY_RUN = "dry_run"


class ArtifactMode(str, Enum):
    BRIEF = "brief"
    COMPARISON = "comparison"
    TREND = "trend"
    POSITION = "position"
    THOUGHT_LEADERSHIP = "thought_leadership"


class ClaimType(str, Enum):
    DIRECT_EVIDENCE = "direct_evidence"
    INTERPRETATION = "interpretation"
    ANALYST_INFERENCE = "analyst_inference"
    ASSUMPTION = "assumption"


class AudienceStyle(str, Enum):
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    MARKET_FACING = "market-facing"


@dataclass(frozen=True)
class SourceEntry:
    """A single entry in the source register."""

    source_id: str
    title: str
    claim_type: ClaimType
    confidence: float
    summary: str = ""
    url: str = ""
    section_id: str = ""


@dataclass(frozen=True)
class ComparisonRow:
    """One row in a comparison matrix."""

    subject: str
    dimensions: dict[str, str]


@dataclass(frozen=True)
class ResearchSection:
    """One section of a research artifact."""

    section_id: str
    heading: str
    body: str
    is_deterministic: bool = True
    claim_type: ClaimType = ClaimType.DIRECT_EVIDENCE
    sources: tuple[str, ...] = field(default_factory=tuple)
    word_count: int = 0


@dataclass
class ResearchRequest:
    """Input contract for a single research run."""

    topic: str
    mode: ArtifactMode = ArtifactMode.BRIEF
    audience_style: AudienceStyle = AudienceStyle.TECHNICAL
    comparison_subjects: list[str] = field(default_factory=list)
    time_horizon: str = ""
    dry_run: bool = False
    trace_id: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchResult:
    """Output contract for a single research run."""

    trace_id: str
    topic: str
    mode: str
    status: ResearchStatus
    sections: list[ResearchSection] = field(default_factory=list)
    comparison_matrix: list[ComparisonRow] = field(default_factory=list)
    source_register: list[SourceEntry] = field(default_factory=list)
    quality_score: float = 0.0
    gate_violations: list[str] = field(default_factory=list)
    artifact_paths: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    run_summary_path: str = ""
    error: str = ""

    @property
    def passed_gate(self) -> bool:
        return len(self.gate_violations) == 0 and self.status == ResearchStatus.COMPLETE


@dataclass
class ResearchRunSummary:
    """Top-level run summary artifact."""

    trace_id: str
    app: str = "apps_research"
    version: str = "1.0.0"
    status: str = "pending"
    topic: str = ""
    mode: str = ""
    sections_generated: int = 0
    sources_registered: int = 0
    quality_score: float = 0.0
    gate_violations: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    dry_run: bool = False
    error: str = ""
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "app": self.app,
            "version": self.version,
            "status": self.status,
            "topic": self.topic,
            "mode": self.mode,
            "sections_generated": self.sections_generated,
            "sources_registered": self.sources_registered,
            "quality_score": self.quality_score,
            "gate_violations": self.gate_violations,
            "artifacts": self.artifacts,
            "dry_run": self.dry_run,
            "error": self.error,
            "provenance": self.provenance,
        }
