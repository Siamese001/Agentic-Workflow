"""
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
