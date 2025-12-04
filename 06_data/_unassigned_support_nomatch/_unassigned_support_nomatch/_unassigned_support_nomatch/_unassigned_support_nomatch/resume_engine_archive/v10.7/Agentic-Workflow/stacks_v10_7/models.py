"""Shared Pydantic data models for stack coordination."""

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class SpecialistDraftPacket(BaseModel):
    """Container for specialist drafting outputs."""

    specialist: str = Field(..., description="Name of the drafting specialist")
    focus_area: str = Field(..., description="Primary responsibility of the specialist")
    sections: Dict[str, Any] = Field(default_factory=dict, description="Section-level draft contributions")
    notes: List[str] = Field(default_factory=list, description="Observations or hand-off notes")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies or follow-up actions")


class EvidenceClarificationRecord(BaseModel):
    """Represents a clarification request raised by the liaison."""

    request_id: str
    recipient: str
    questions: List[str]
    priority: str = "normal"
    context_summary: str = ""


class EvidenceBriefRecord(BaseModel):
    """Structured evidence digest for a section."""

    section: str
    brief: str
    key_points: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    outstanding_questions: List[str] = Field(default_factory=list)


class EvidenceLiaisonPacket(BaseModel):
    """Aggregated liaison output feeding back to the guild."""

    clarifications: List[EvidenceClarificationRecord] = Field(default_factory=list)
    briefs: List[EvidenceBriefRecord] = Field(default_factory=list)


class CritiqueFindingRecord(BaseModel):
    """Single critique finding routed by the panel."""

    critic: str
    severity: str
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)


class CritiquePanelPacket(BaseModel):
    """Aggregated critique findings for the coordinator."""

    findings: List[CritiqueFindingRecord] = Field(default_factory=list)
    overall_status: str = Field(..., description="Coordinator-level status derived from findings")
