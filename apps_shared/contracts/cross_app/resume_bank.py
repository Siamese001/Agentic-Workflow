"""ResumeBankEnvelope — apps_rg -> apps_qna with master_resume lineage.

Plan: apps-cross-app-precursors-c94c71 Wave 2 (GAP-4).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from apps_shared.contracts.cross_app.base import CrossAppEnvelope


class ResumeBankPayload(BaseModel):
    """Typed projection of apps_rg/data/*.yaml with master_resume lineage."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_file: str = Field(description="Relative path to bank YAML/JSON.")
    master_resume_source_sha256: str = Field(
        description="SHA256 of the master_resume JSON the bank was derived from."
    )
    points: list[dict[str, Any]] = Field(default_factory=list)
    star_bank: dict[str, Any] = Field(default_factory=dict)
    rca_bank: list[dict[str, Any]] = Field(default_factory=list)


class ResumeBankEnvelope(CrossAppEnvelope):
    """apps_rg -> apps_qna resume bank handoff envelope."""

    SCHEMA_NAME: ClassVar[str] = "cross_app.resume_bank"
    COMPATIBLE_MAJOR: ClassVar[int] = 1

    payload: ResumeBankPayload

    @classmethod
    def emit(
        cls,
        *,
        trace_id: str,
        payload: ResumeBankPayload,
        producer_app: str = "apps_rg",
        schema_version: str = "1.0.0",
        ttl_days: int = 60,
        emitted_at: datetime | None = None,
    ) -> "ResumeBankEnvelope":
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
        self, data_dir: Path = Path("apps_rg/data")
    ) -> Path:
        stem = Path(self.payload.source_file).stem
        return data_dir / f"{stem}.envelope.json"
