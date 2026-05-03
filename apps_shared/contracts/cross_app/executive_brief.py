"""ExecutiveBriefEnvelope — apps_exec -> apps_qna.

Plan: apps-cross-app-precursors-c94c71 Wave 2 (GAP-3).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field

from apps_shared.contracts.cross_app.base import CrossAppEnvelope


class ExecutiveBriefPayload(BaseModel):
    """Typed projection of exec_brief_*.md."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    brief_path: str = Field(description="Relative path to the markdown brief.")
    close_patterns: list[str] = Field(default_factory=list)
    thesis_lines: list[str] = Field(default_factory=list)


class ExecutiveBriefEnvelope(CrossAppEnvelope):
    """apps_exec -> apps_qna executive-fit handoff envelope."""

    SCHEMA_NAME: ClassVar[str] = "cross_app.executive_brief"
    COMPATIBLE_MAJOR: ClassVar[int] = 1

    payload: ExecutiveBriefPayload

    @classmethod
    def emit(
        cls,
        *,
        trace_id: str,
        payload: ExecutiveBriefPayload,
        producer_app: str = "apps_exec",
        schema_version: str = "1.0.0",
        ttl_days: int = 30,
        emitted_at: datetime | None = None,
    ) -> "ExecutiveBriefEnvelope":
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
        self, exec_dir: Path = Path("reports/executive")
    ) -> Path:
        return exec_dir / f"exec_brief_{self.trace_id}.envelope.json"
