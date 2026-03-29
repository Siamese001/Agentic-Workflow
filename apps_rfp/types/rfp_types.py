"""
apps_rfp domain types — AI Proposal / RFP Generator.

All types are frozen dataclasses or Pydantic models.
Every artifact carries provenance metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProposalStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    GATE_CHECKING = "gate_checking"
    COMPLETE = "complete"
    FAILED = "failed"
    DRY_RUN = "dry_run"


class ArchitecturePosture(str, Enum):
    CLOUD_FIRST = "cloud-first"
    HYBRID = "hybrid"
    SOVEREIGN = "sovereign"
    REGULATED = "regulated"


class RiskSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RoadmapPhase:
    """A single phase in the implementation roadmap."""

    phase_id: str
    name: str
    duration_weeks: int
    objectives: tuple[str, ...] = field(default_factory=tuple)
    deliverables: tuple[str, ...] = field(default_factory=tuple)
    governance_milestone: str = ""
    measurement_milestone: str = ""


@dataclass(frozen=True)
class RiskItem:
    """A single risk in the risk matrix."""

    risk_id: str
    category: str
    description: str
    severity: RiskSeverity
    mitigation: str
    owner: str = "Platform Team"


@dataclass(frozen=True)
class AssumptionItem:
    """A labeled assumption in the proposal."""

    assumption_id: str
    statement: str
    basis: str = "analyst judgment"
    section_id: str = ""


@dataclass(frozen=True)
class ProposalSection:
    """One section of a generated proposal."""

    section_id: str
    heading: str
    body: str
    is_deterministic: bool = True
    assumptions: tuple[AssumptionItem, ...] = field(default_factory=tuple)
    evidence: tuple[str, ...] = field(default_factory=tuple)
    word_count: int = 0


@dataclass
class RfpRequest:
    """Input contract for a single RFP proposal generation run."""

    problem_statement: str = ""
    industry: str = "technology"
    company_size: str = ""
    security_requirements: list[str] = field(default_factory=list)
    architecture_posture: ArchitecturePosture = ArchitecturePosture.CLOUD_FIRST
    delivery_timeline_weeks: int = 0
    existing_tooling: list[str] = field(default_factory=list)
    dry_run: bool = False
    trace_id: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class RfpResult:
    """Output contract for a single RFP proposal generation run."""

    trace_id: str = ""
    industry: str = ""
    status: ProposalStatus = ProposalStatus.PENDING
    sections: list[ProposalSection] = field(default_factory=list)
    roadmap: list[RoadmapPhase] = field(default_factory=list)
    risks: list[RiskItem] = field(default_factory=list)
    assumptions: list[AssumptionItem] = field(default_factory=list)
    quality_score: float = 0.0
    gate_violations: list[str] = field(default_factory=list)
    artifact_paths: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    run_summary_path: str = ""
    error: str = ""

    @property
    def passed_gate(self) -> bool:
        return len(self.gate_violations) == 0 and self.status == ProposalStatus.COMPLETE


@dataclass
class RfpRunSummary:
    """Top-level run summary artifact."""

    trace_id: str = ""
    app: str = "apps_rfp"
    version: str = "1.0.0"
    status: str = "pending"
    industry: str = ""
    sections_generated: int = 0
    roadmap_phases: int = 0
    risks_identified: int = 0
    assumptions_declared: int = 0
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
            "industry": self.industry,
            "sections_generated": self.sections_generated,
            "roadmap_phases": self.roadmap_phases,
            "risks_identified": self.risks_identified,
            "assumptions_declared": self.assumptions_declared,
            "quality_score": self.quality_score,
            "gate_violations": self.gate_violations,
            "artifacts": self.artifacts,
            "dry_run": self.dry_run,
            "error": self.error,
            "provenance": self.provenance,
        }
