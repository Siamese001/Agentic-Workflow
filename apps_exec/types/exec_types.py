"""
apps_exec domain types — Executive Brief Generator.

All types are frozen dataclasses or Pydantic models.
No mutable shared state. Every artifact carries provenance metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AudiencePersona(str, Enum):
    RECRUITER = "recruiter"
    CTO = "cto"
    SVP_ENG = "svp_eng"
    BOARD = "board"
    HEAD_OF_AI = "head_of_ai"


class BriefTone(str, Enum):
    BOARD_READY = "board-ready"
    CTO_READY = "cto-ready"
    RECRUITER_FRIENDLY = "recruiter-friendly"
    TECHNICAL = "technical"


class EmphasisArea(str, Enum):
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"
    RAG = "rag"
    COMMERCIALIZATION = "commercialization"
    SAFETY = "safety"
    OBSERVABILITY = "observability"
    DETERMINISM = "determinism"


class BriefStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    GATE_CHECKING = "gate_checking"
    COMPLETE = "complete"
    FAILED = "failed"
    DRY_RUN = "dry_run"


@dataclass(frozen=True)
class CapabilityEvidence:
    """A single extracted platform capability with its evidence anchor."""

    capability_id: str
    label: str
    description: str
    evidence_anchors: tuple[str, ...] = field(default_factory=tuple)
    layer: str = ""
    emphasis_area: str = ""


@dataclass(frozen=True)
class BriefSection:
    """One section of an executive brief."""

    section_id: str
    heading: str
    body: str
    is_deterministic: bool = True
    evidence_anchors: tuple[str, ...] = field(default_factory=tuple)
    why_this_matters: str = ""
    word_count: int = 0


@dataclass
class ExecBriefRequest:
    """Input contract for a single executive brief generation run."""

    audience: AudiencePersona
    source_dirs: list[str] = field(default_factory=lambda: ["docs/architecture"])
    emphasis_areas: list[EmphasisArea] = field(default_factory=list)
    tone: BriefTone = BriefTone.TECHNICAL
    industry: str = ""
    dry_run: bool = False
    trace_id: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecBriefResult:
    """Output contract for a single executive brief generation run."""

    trace_id: str
    audience: str
    tone: str
    status: BriefStatus
    sections: list[BriefSection] = field(default_factory=list)
    capabilities_extracted: list[CapabilityEvidence] = field(default_factory=list)
    quality_score: float = 0.0
    gate_violations: list[str] = field(default_factory=list)
    artifact_paths: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    run_summary_path: str = ""
    error: str = ""

    @property
    def passed_gate(self) -> bool:
        return len(self.gate_violations) == 0 and self.status == BriefStatus.COMPLETE


@dataclass(frozen=True)
class StyleViolation:
    """A single style gate violation."""

    rule_id: str
    severity: str
    message: str
    section_id: str = ""
    evidence: str = ""


@dataclass
class RunSummary:
    """Top-level run summary artifact emitted at end of every run."""

    trace_id: str
    app: str = "apps_exec"
    version: str = "1.0.0"
    status: str = "pending"
    audience: str = ""
    tone: str = ""
    sections_generated: int = 0
    capabilities_extracted: int = 0
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
            "audience": self.audience,
            "tone": self.tone,
            "sections_generated": self.sections_generated,
            "capabilities_extracted": self.capabilities_extracted,
            "quality_score": self.quality_score,
            "gate_violations": self.gate_violations,
            "artifacts": self.artifacts,
            "dry_run": self.dry_run,
            "error": self.error,
            "provenance": self.provenance,
        }
