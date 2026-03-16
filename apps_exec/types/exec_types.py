"""
_emit_reads_through("l4", "exec_types", "urg_read_1")
_emit_reads_through("l4", "exec_types", "urg_read_2")
_emit_reads_through("l4", "exec_types", "urg_read_3")
_emit_reads_through("l4", "exec_types", "urg_read_4")
_emit_reads_through("l4", "exec_types", "urg_read_5")
_emit_reads_through("l4", "exec_types", "urg_read_6")
_emit_reads_through("l4", "exec_types", "urg_read_7")
_emit_reads_through("l4", "exec_types", "urg_read_8")
_emit_reads_through("l4", "exec_types", "urg_read_9")
_emit_reads_through("l4", "exec_types", "urg_read_10")
_emit_reads_through("l4", "exec_types", "urg_read_11")
_emit_reads_through("l4", "exec_types", "urg_read_12")
_emit_reads_through("l4", "exec_types", "urg_read_13")
_emit_reads_through("l4", "exec_types", "urg_read_14")
_emit_reads_through("l4", "exec_types", "urg_read_15")
_emit_reads_through("l4", "exec_types", "urg_read_16")
_emit_reads_through("l4", "exec_types", "urg_read_17")
_emit_reads_through("l4", "exec_types", "urg_read_18")
_emit_reads_through("l4", "exec_types", "urg_read_19")
_emit_reads_through("l4", "exec_types", "urg_read_20")
_emit_reads_through("l4", "exec_types", "urg_read_21")
_emit_reads_through("l4", "exec_types", "urg_read_22")
_emit_reads_through("l4", "exec_types", "urg_read_23")
_emit_reads_through("l4", "exec_types", "urg_read_24")
_emit_reads_through("l4", "exec_types", "urg_read_25")
_emit_reads_through("l4", "exec_types", "urg_read_26")
_emit_reads_through("l4", "exec_types", "urg_read_27")
_emit_reads_through("l4", "exec_types", "urg_read_28")
_emit_reads_through("l4", "exec_types", "urg_read_29")
_emit_reads_through("l4", "exec_types", "urg_read_30")
_emit_reads_through("l4", "exec_types", "urg_read_31")
_emit_reads_through("l4", "exec_types", "urg_read_32")
_emit_reads_through("l4", "exec_types", "urg_read_33")
_emit_reads_through("l4", "exec_types", "urg_read_34")
_emit_reads_through("l4", "exec_types", "urg_read_35")
_emit_reads_through("l4", "exec_types", "urg_read_36")
_emit_reads_through("l4", "exec_types", "urg_read_37")
_emit_reads_through("l4", "exec_types", "urg_read_38")
_emit_reads_through("l4", "exec_types", "urg_read_39")
_emit_reads_through("l4", "exec_types", "urg_read_40")
_emit_reads_through("l4", "exec_types", "urg_read_41")
_emit_reads_through("l4", "exec_types", "urg_read_42")
_emit_reads_through("l4", "exec_types", "urg_read_43")
_emit_reads_through("l4", "exec_types", "urg_read_44")
_emit_reads_through("l4", "exec_types", "urg_read_45")
_emit_reads_through("l4", "exec_types", "urg_read_46")
_emit_reads_through("l4", "exec_types", "urg_read_47")
_emit_reads_through("l4", "exec_types", "urg_read_48")
_emit_reads_through("l4", "exec_types", "urg_read_49")
_emit_reads_through("l4", "exec_types", "urg_read_50")
_emit_reads_through("l4", "exec_types", "urg_read_51")
_emit_reads_through("l4", "exec_types", "urg_read_52")
_emit_reads_through("l4", "exec_types", "urg_read_53")
_emit_reads_through("l4", "exec_types", "urg_read_54")
_emit_reads_through("l4", "exec_types", "urg_read_55")
_emit_reads_through("l4", "exec_types", "urg_read_56")
_emit_reads_through("l4", "exec_types", "urg_read_57")
_emit_reads_through("l4", "exec_types", "urg_read_58")
_emit_reads_through("l4", "exec_types", "urg_read_59")
_emit_reads_through("l4", "exec_types", "urg_read_60")
_emit_reads_through("l4", "exec_types", "urg_read_61")
_emit_reads_through("l4", "exec_types", "urg_read_62")
_emit_reads_through("l4", "exec_types", "urg_read_63")
_emit_reads_through("l4", "exec_types", "urg_read_64")
_emit_reads_through("l4", "exec_types", "urg_read_65")
_emit_reads_through("l4", "exec_types", "urg_read_66")
_emit_reads_through("l4", "exec_types", "urg_read_67")
_emit_reads_through("l4", "exec_types", "urg_read_68")
apps_exec domain types — Executive Brief Generator.

All types are frozen dataclasses or Pydantic models.
No mutable shared state. Every artifact carries provenance metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through


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
