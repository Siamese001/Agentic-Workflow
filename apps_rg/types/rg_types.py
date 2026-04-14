"""
apps_rg domain types — Resume Generation Engine.

All types are Pydantic models with strict validation.
Every artifact carries provenance metadata.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

try:
    from pydantic import field_validator
except ImportError:
    from pydantic import validator as _validator

    def field_validator(*fields, **kwargs):
        kwargs.pop("mode", None)
        return _validator(*fields, **kwargs)


class RGBaseModel(BaseModel):
    """Pydantic v1/v2 compatibility base model."""

    def model_dump(self, *args, **kwargs):
        if hasattr(super(), "model_dump"):
            return super().model_dump(*args, **kwargs)
        return self.dict(*args, **kwargs)


ResumeStatus = Literal["pending", "analyzing", "generating", "reviewing", "complete", "failed"]

ResumeFormat = Literal["standard", "ats_optimized", "executive", "creative"]

TargetIndustry = Literal["tech", "finance", "healthcare", "consulting", "general"]

ExperienceLevel = Literal["entry", "mid", "senior", "executive"]


class SkillMatch(RGBaseModel):
    """A skill match between resume and job requirements."""

    skill_name: str = Field(..., min_length=1, description="Skill name")
    match_score: float = Field(0.0, ge=0, le=1, description="Match confidence")
    evidence: str = Field("", description="Evidence from resume")
    priority: str = Field("medium", description="Skill priority level")


class ExperienceEntry(RGBaseModel):
    """A single work experience entry."""

    company: str = Field(..., min_length=1, description="Company name")
    title: str = Field(..., min_length=1, description="Job title")
    duration_months: int = Field(0, ge=0, description="Duration in months")
    achievements: list[str] = Field(default_factory=list, description="Key achievements")
    technologies: list[str] = Field(default_factory=list, description="Technologies used")


class ResumeSection(RGBaseModel):
    """One section of a resume."""

    section_id: str = Field(..., min_length=1, description="Unique section ID")
    section_type: str = Field(..., description="Type of section (summary, experience, etc)")
    content: str = Field(..., min_length=20, description="Section content")
    word_count: int = Field(0, ge=0, description="Word count")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v):
        if len(v.strip()) < 20:
            raise ValueError("content must be at least 20 characters")
        return v.strip()


class ResumeConfig(RGBaseModel):
    """Resume generation configuration."""

    target_format: ResumeFormat = Field("standard", description="Target resume format")
    max_length_words: int = Field(500, ge=100, le=2000, description="Maximum word count")
    ats_optimization: bool = Field(True, description="Enable ATS optimization")
    highlight_leadership: bool = Field(False, description="Highlight leadership experience")
    min_skill_matches: int = Field(5, ge=0, description="Minimum skill matches to include")


class ResumeRequest(RGBaseModel):
    """Input contract for a single resume generation run."""

    candidate_name: str = Field(..., min_length=1, description="Candidate full name")
    target_role: str = Field(..., min_length=1, description="Target job title/role")
    target_industry: TargetIndustry = Field("general", description="Target industry")
    experience_level: ExperienceLevel = Field("mid", description="Experience level")
    source_resume_text: str = Field("", description="Source resume text")
    job_description: str = Field("", description="Target job description")
    config: ResumeConfig = Field(default_factory=ResumeConfig, description="Resume configuration")
    dry_run: bool = Field(False, description="Dry run mode")
    trace_id: str = Field("", description="Trace identifier")

    @field_validator("candidate_name", "target_role")
    @classmethod
    def validate_required(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("field cannot be empty")
        return v.strip()


class ResumeResult(RGBaseModel):
    """Output contract for a single resume generation run."""

    trace_id: str = Field("", description="Trace identifier")
    candidate_name: str = Field("", description="Candidate name")
    target_role: str = Field("", description="Target role")
    status: ResumeStatus = Field("pending", description="Generation status")
    sections: list[ResumeSection] = Field(default_factory=list, description="Generated sections")
    skill_matches: list[SkillMatch] = Field(default_factory=list, description="Skill matches")
    ats_score: float = Field(0.0, ge=0, le=100, description="ATS compatibility score")
    quality_score: float = Field(0.0, ge=0, le=1, description="Overall quality score")
    gate_violations: list[str] = Field(default_factory=list, description="Gate violations")
    artifact_paths: list[str] = Field(default_factory=list, description="Output artifact paths")
    provenance: dict = Field(default_factory=dict, description="Provenance metadata")
    error: str = Field("", description="Error message")

    @property
    def passed_gate(self) -> bool:
        """Check if resume passed all gates."""
        return len(self.gate_violations) == 0 and self.status in ("complete",)

    @field_validator("quality_score")
    @classmethod
    def validate_quality(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("quality_score must be between 0.0 and 1.0")
        return v


class ResumeRunSummary(RGBaseModel):
    """Top-level run summary artifact."""

    trace_id: str = Field("", description="Trace identifier")
    app: str = Field("apps_rg", description="Application name")
    version: str = Field("1.0.0", description="Version")
    status: str = Field("pending", description="Run status")
    candidate_name: str = Field("", description="Candidate name")
    target_role: str = Field("", description="Target role")
    sections_generated: int = Field(0, ge=0, description="Sections generated")
    skill_matches_found: int = Field(0, ge=0, description="Skill matches found")
    ats_score: float = Field(0.0, ge=0, le=100, description="ATS compatibility score")
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
                "trace_id": "RG-2024-001",
                "app": "apps_rg",
                "version": "1.0.0",
                "status": "complete",
                "candidate_name": "Jane Smith",
                "target_role": "Senior Software Engineer",
                "ats_score": 85.5,
                "quality_score": 0.88,
            },
        }
