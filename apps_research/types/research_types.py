"""
apps_research domain types — Autonomous Research Engine.

All types are Pydantic models with strict validation.
Every artifact carries provenance metadata.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

ResearchStatus = Literal["pending", "generating", "gate_checking", "complete", "failed", "dry_run"]

ArtifactMode = Literal["brief", "comparison", "trend", "position", "thought_leadership"]

ClaimType = Literal["direct_evidence", "interpretation", "analyst_inference", "assumption"]

AudienceStyle = Literal["technical", "executive", "market-facing"]


class SourceEntry(BaseModel):
    """A single entry in the source register."""

    source_id: str = Field(..., min_length=1, description="Unique source ID")
    title: str = Field(..., min_length=1, description="Source title")
    claim_type: ClaimType = Field("direct_evidence", description="Type of claim")
    confidence: float = Field(0.5, ge=0, le=1, description="Confidence level")
    summary: str = Field("", description="Source summary")
    url: str = Field("", description="Source URL")
    section_id: str = Field("", description="Related section ID")


class ComparisonRow(BaseModel):
    """One row in a comparison matrix."""

    subject: str = Field(..., min_length=1, description="Subject being compared")
    dimensions: dict[str, str] = Field(default_factory=dict, description="Comparison dimensions")


class ResearchSection(BaseModel):
    """One section of a research artifact."""

    section_id: str = Field(..., min_length=1, description="Unique section ID")
    heading: str = Field(..., min_length=1, description="Section heading")
    body: str = Field(..., min_length=50, description="Section body content")
    is_deterministic: bool = Field(True, description="Whether content is deterministic")
    claim_type: ClaimType = Field("direct_evidence", description="Claim type")
    sources: list[str] = Field(default_factory=list, description="Source references")
    word_count: int = Field(0, ge=0, description="Word count")

    @field_validator("body")
    @classmethod
    def validate_body(cls, v):
        if len(v.strip()) < 50:
            raise ValueError("body must be at least 50 characters")
        return v.strip()


class ResearchConfig(BaseModel):
    """Research generation configuration."""

    min_quality_score: float = Field(0.7, ge=0, le=1, description="Minimum quality threshold")
    max_sections: int = Field(10, ge=1, le=20, description="Maximum sections")
    min_sources: int = Field(3, ge=0, description="Minimum sources required")
    require_evidence_based: bool = Field(True, description="Require evidence-based claims")
    enforce_claim_type_consistency: bool = Field(True, description="Enforce claim type consistency")


class ResearchRequest(BaseModel):
    """Input contract for a single research run."""

    topic: str = Field(..., min_length=1, description="Research topic")
    mode: ArtifactMode = Field("brief", description="Artifact mode")
    audience_style: AudienceStyle = Field("technical", description="Target audience style")
    comparison_subjects: list[str] = Field(default_factory=list, description="Subjects for comparison mode")
    time_horizon: str = Field("", description="Time horizon for analysis")
    config: ResearchConfig = Field(default_factory=ResearchConfig, description="Research configuration")
    dry_run: bool = Field(False, description="Dry run mode")
    trace_id: str = Field("", description="Trace identifier")

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("topic cannot be empty")
        return v.strip()


class ResearchResult(BaseModel):
    """Output contract for a single research run."""

    trace_id: str = Field("", description="Trace identifier")
    topic: str = Field("", description="Research topic")
    mode: str = Field("", description="Artifact mode")
    status: ResearchStatus = Field("pending", description="Generation status")
    sections: list[ResearchSection] = Field(default_factory=list, description="Generated sections")
    comparison_matrix: list[ComparisonRow] = Field(default_factory=list, description="Comparison matrix")
    source_register: list[SourceEntry] = Field(default_factory=list, description="Registered sources")
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
        """Check if research passed all gates."""
        return len(self.gate_violations) == 0 and self.status in ("complete", "dry_run")

    @field_validator("quality_score")
    @classmethod
    def validate_quality(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("quality_score must be between 0.0 and 1.0")
        return v


class ResearchRunSummary(BaseModel):
    """Top-level run summary artifact."""

    trace_id: str = Field("", description="Trace identifier")
    app: str = Field("apps_research", description="Application name")
    version: str = Field("1.0.0", description="Version")
    status: str = Field("pending", description="Run status")
    topic: str = Field("", description="Research topic")
    mode: str = Field("", description="Artifact mode")
    sections_generated: int = Field(0, ge=0, description="Sections generated")
    sources_registered: int = Field(0, ge=0, description="Sources registered")
    quality_score: float = Field(0.0, ge=0, le=1, description="Overall quality score")
    gate_violations: list[str] = Field(default_factory=list, description="Gate violations")
    artifacts: list[str] = Field(default_factory=list, description="Generated artifacts")
    dry_run: bool = Field(False, description="Dry run mode")
    error: str = Field("", description="Error message")
    provenance: dict = Field(default_factory=dict, description="Provenance metadata")

    def to_dict(self) -> dict:
        """Export as dictionary."""
        return self.model_dump()

    class Config:
        json_schema_extra = {
            "example": {
                "trace_id": "RES-2024-001",
                "app": "apps_research",
                "version": "1.0.0",
                "status": "complete",
                "topic": "AI Governance Trends",
                "mode": "brief",
                "sections_generated": 5,
                "sources_registered": 12,
                "quality_score": 0.82,
            },
        }
