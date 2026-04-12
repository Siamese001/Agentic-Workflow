"""Shared Pydantic data models for stack coordination."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SpecialistDraftPacket(BaseModel):
    """Container for specialist drafting outputs."""

    specialist: str = Field(..., description="Name of the drafting specialist")
    focus_area: str = Field(..., description="Primary responsibility of the specialist")
    sections: dict[str, Any] = Field(default_factory=dict, description="Section-level draft contributions")
    notes: list[str] = Field(default_factory=list, description="Observations or hand-off notes")
    dependencies: list[str] = Field(default_factory=list, description="Dependencies or follow-up actions")


class EvidenceClarificationRecord(BaseModel):
    """Represents a clarification request raised by the liaison."""

    request_id: str
    recipient: str
    questions: list[str]
    priority: str = "normal"
    context_summary: str = ""


class EvidenceBriefRecord(BaseModel):
    """Structured evidence digest for a section."""

    section: str
    brief: str
    key_points: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    outstanding_questions: list[str] = Field(default_factory=list)


class EvidenceLiaisonPacket(BaseModel):
    """Aggregated liaison output feeding back to the guild."""

    clarifications: list[EvidenceClarificationRecord] = Field(default_factory=list)
    briefs: list[EvidenceBriefRecord] = Field(default_factory=list)


class CritiqueFindingRecord(BaseModel):
    """Single critique finding routed by the panel."""

    critic: str
    severity: str
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class CritiquePanelPacket(BaseModel):
    """Aggregated critique findings for the coordinator."""

    findings: list[CritiqueFindingRecord] = Field(default_factory=list)
    overall_status: str = Field(..., description="Coordinator-level status derived from findings")
