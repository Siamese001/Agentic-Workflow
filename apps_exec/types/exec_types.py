"""
apps_exec domain types — Executive Brief Generator.

All types are Pydantic models with strict validation.
No mutable shared state. Every artifact carries provenance metadata.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

AudiencePersona = Literal["recruiter", "cto", "svp_eng", "board", "head_of_ai"]

BriefTone = Literal["board-ready", "cto-ready", "recruiter-friendly", "technical"]

EmphasisArea = Literal[
    "governance",
    "orchestration",
    "rag",
    "commercialization",
    "safety",
    "observability",
    "determinism",
]

BriefStatus = Literal["pending", "generating", "gate_checking", "complete", "failed", "dry_run"]


class CapabilityEvidence(BaseModel):
    """A single extracted platform capability with its evidence anchor."""

    capability_id: str = Field(..., min_length=1, description="Unique capability ID")
    label: str = Field(..., min_length=1, description="Capability label")
    description: str = Field(..., min_length=10, description="Detailed description")
    evidence_anchors: list[str] = Field(default_factory=list, description="Evidence references")
    layer: str = Field("", description="Architecture layer")
    emphasis_area: str = Field("", description="Related emphasis area")

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("description must be at least 10 characters")
        return v.strip()


class BriefSection(BaseModel):
    """One section of an executive brief."""

    section_id: str = Field(..., min_length=1, description="Unique section ID")
    heading: str = Field(..., min_length=1, description="Section heading")
    body: str = Field(..., min_length=50, description="Section body content")
    is_deterministic: bool = Field(True, description="Whether content is deterministic")
    evidence_anchors: list[str] = Field(default_factory=list, description="Evidence references")
    why_this_matters: str = Field("", description="Business significance")
    word_count: int = Field(0, ge=0, description="Word count")

    @field_validator("body")
    @classmethod
    def validate_body(cls, v):
        if len(v.strip()) < 50:
            raise ValueError("body must be at least 50 characters")
        return v.strip()


class ExecBriefConfig(BaseModel):
    """Executive brief generation configuration."""

    min_quality_score: float = Field(0.7, ge=0, le=1, description="Minimum quality threshold")
    max_sections: int = Field(8, ge=1, le=20, description="Maximum sections")
    min_evidence_anchors: int = Field(2, ge=0, description="Minimum evidence per section")
    require_board_ready: bool = Field(False, description="Require board-ready quality")
    enforce_tone_consistency: bool = Field(True, description="Enforce tone consistency")


class ExecBriefRequest(BaseModel):
    """Input contract for a single executive brief generation run."""

    audience: AudiencePersona = Field("recruiter", description="Target audience")
    source_dirs: list[str] = Field(
        default_factory=lambda: ["docs/architecture"], description="Source directories"
    )
    emphasis_areas: list[EmphasisArea] = Field(default_factory=list, description="Areas to emphasize")
    tone: BriefTone = Field("technical", description="Brief tone")
    industry: str = Field("", description="Industry sector")
    config: ExecBriefConfig = Field(default_factory=ExecBriefConfig, description="Brief configuration")
    dry_run: bool = Field(False, description="Dry run mode")
    trace_id: str = Field("", description="Trace identifier")


class ExecBriefResult(BaseModel):
    """Output contract for a single executive brief generation run."""

    trace_id: str = Field("", description="Trace identifier")
    audience: str = Field("", description="Target audience")
    tone: str = Field("", description="Brief tone")
    status: BriefStatus = Field("pending", description="Generation status")
    sections: list[BriefSection] = Field(default_factory=list, description="Generated sections")
    capabilities_extracted: list[CapabilityEvidence] = Field(
        default_factory=list, description="Extracted capabilities"
    )
    quality_score: float = Field(0.0, ge=0, le=1, description="Overall quality score")
    gate_violations: list[str] = Field(default_factory=list, description="Gate violations")
    artifact_paths: list[str] = Field(default_factory=list, description="Output artifact paths")
    provenance: dict = Field(default_factory=dict, description="Provenance metadata")
    run_summary_path: str = Field("", description="Summary output path")
    error: str = Field("", description="Error message")
    qwen_inference_result: dict | None = Field(
        None, description="Local Qwen vLLM inference result when LOCAL_VLLM routing selected"
    )
    local_first_disposition: dict | None = Field(
        None, description="Current-run routing disposition packet for local-first Qwen lane"
    )

    @property
    def passed_gate(self) -> bool:
        """Check if brief passed all gates."""
        return len(self.gate_violations) == 0 and self.status in ("complete", "dry_run")

    @field_validator("quality_score")
    @classmethod
    def validate_quality(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("quality_score must be between 0.0 and 1.0")
        return v


class StyleViolation(BaseModel):
    """A single style gate violation."""

    rule_id: str = Field(..., min_length=1, description="Rule identifier")
    severity: str = Field(..., description="Violation severity")
    message: str = Field(..., min_length=5, description="Violation message")
    section_id: str = Field("", description="Related section ID")
    evidence: str = Field("", description="Supporting evidence")


class RunSummary(BaseModel):
    """Top-level run summary artifact."""

    trace_id: str = Field("", description="Trace identifier")
    app: str = Field("apps_exec", description="Application name")
    version: str = Field("1.0.0", description="Version")
    status: str = Field("pending", description="Run status")
    audience: str = Field("", description="Target audience")
    tone: str = Field("", description="Brief tone")
    sections_generated: int = Field(0, ge=0, description="Sections generated")
    capabilities_extracted: int = Field(0, ge=0, description="Capabilities extracted")
    quality_score: float = Field(0.0, ge=0, le=1, description="Overall quality score")
    gate_violations: list[str] = Field(default_factory=list, description="Gate violations")
    artifacts: list[str] = Field(default_factory=list, description="Generated artifacts")
    dry_run: bool = Field(False, description="Dry run mode")
    error: str = Field("", description="Error message")
    provenance: dict = Field(default_factory=dict, description="Provenance metadata")

    def to_dict(self) -> dict:
        """Export as dictionary."""
        return self.model_dump()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "trace_id": "EXEC-2024-001",
                "app": "apps_exec",
                "version": "1.0.0",
                "status": "complete",
                "audience": "board",
                "tone": "board-ready",
                "sections_generated": 6,
                "capabilities_extracted": 12,
                "quality_score": 0.85,
            },
        },
    )
