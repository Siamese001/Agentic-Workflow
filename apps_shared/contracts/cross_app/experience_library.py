"""ExperienceLibraryEnvelope — apps_shared master_resume -> apps_qna.

Plan: apps-cross-app-precursors-c94c71 Wave 2 (GAP-2).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from apps_shared.contracts.cross_app.base import CrossAppEnvelope


class ExperienceBullet(BaseModel):
    """One bullet from a professional-experience role."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    label: str = ""
    text: str
    tags: list[str] = Field(default_factory=list)
    role_title: str = ""


class ExperienceLibraryPayload(BaseModel):
    """Typed projection of master_resume.json used by apps_qna."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_file: str = Field(
        description="Relative path of the master_resume.json variant."
    )
    variant: str = Field(
        default="default",
        description="e.g. 'default' or 'svp'; used by consumers that branch.",
    )
    executive_summary: str | None = None
    competency_areas: list[dict[str, Any]] = Field(default_factory=list)
    bullets: list[ExperienceBullet] = Field(default_factory=list)


class ExperienceLibraryEnvelope(CrossAppEnvelope):
    """apps_shared -> apps_qna ExperienceLibrary handoff envelope."""

    SCHEMA_NAME: ClassVar[str] = "cross_app.experience_library"
    COMPATIBLE_MAJOR: ClassVar[int] = 1

    payload: ExperienceLibraryPayload

    @classmethod
    def emit(
        cls,
        *,
        trace_id: str,
        payload: ExperienceLibraryPayload,
        producer_app: str = "apps_shared",
        schema_version: str = "1.0.0",
        ttl_days: int = 90,
        emitted_at: datetime | None = None,
    ) -> "ExperienceLibraryEnvelope":
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
        self, data_dir: Path = Path("apps_shared/data")
    ) -> Path:
        """Canonical sidecar location for this envelope."""
        stem = Path(self.payload.source_file).stem
        return data_dir / f"{stem}.envelope.json"
