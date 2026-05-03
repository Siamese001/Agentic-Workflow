"""ResearchBriefEnvelope — apps_research -> apps_qna.

Plan: apps-cross-app-precursors-c94c71 Wave 2 (GAP-3).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field

from apps_shared.contracts.cross_app.base import CrossAppEnvelope


class ResearchClaimRow(BaseModel):
    """One claim from a research source register (typed projection)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    claim: str
    claim_type: Literal[
        "direct_evidence", "interpretation", "analyst_inference", "assumption"
    ] = "analyst_inference"
    source_id: str = "SRC-000"
    section_id: str = ""


class ResearchBriefPayload(BaseModel):
    """Typed projection of research_brief_<trace>.md + source_register."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    brief_path: str = Field(description="Relative path to the markdown brief.")
    register_path: str | None = None
    company_brief: str | None = None
    role_areas_of_focus: list[str] = Field(default_factory=list)
    industry_trends: list[str] = Field(default_factory=list)
    source_register: list[ResearchClaimRow] = Field(default_factory=list)


class ResearchBriefEnvelope(CrossAppEnvelope):
    """apps_research -> apps_qna research brief handoff envelope."""

    SCHEMA_NAME: ClassVar[str] = "cross_app.research_brief"
    COMPATIBLE_MAJOR: ClassVar[int] = 1

    payload: ResearchBriefPayload

    @classmethod
    def emit(
        cls,
        *,
        trace_id: str,
        payload: ResearchBriefPayload,
        producer_app: str = "apps_research",
        schema_version: str = "1.0.0",
        ttl_days: int = 30,
        emitted_at: datetime | None = None,
    ) -> "ResearchBriefEnvelope":
        fields = cls._envelope_fields(
            trace_id=trace_id,
            producer_app=producer_app,
            payload=payload,
            schema_version=schema_version,
            ttl_days=ttl_days,
            emitted_at=emitted_at,
        )
        return cls(payload=payload, **fields)

    def default_sidecar_path(
        self, research_dir: Path = Path("reports/research")
    ) -> Path:
        return research_dir / f"research_brief_{self.trace_id}.envelope.json"
