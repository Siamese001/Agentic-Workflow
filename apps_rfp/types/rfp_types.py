"""
apps_rfp domain types — AI Proposal / RFP Generator.

All types are Pydantic models with strict validation.
Every artifact carries provenance. No silent pass — all failures recorded.
"""

from __future__ import annotations

from typing import Literal

try:
    from pydantic import BaseModel, Field, field_validator
except ImportError:  # Pydantic v1 compatibility
    from pydantic import BaseModel, Field, validator as field_validator  # type: ignore[no-redef]

ProposalStatus = Literal["pending", "generating", "gate_checking", "complete", "failed", "dry_run"]

ArchitecturePosture = Literal["cloud-first", "hybrid", "sovereign", "regulated"]

RiskSeverity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class RoadmapPhase(BaseModel):
    """A single phase in the implementation roadmap."""

    phase_id: str = Field(..., min_length=1, description="Unique phase identifier")
    name: str = Field(..., min_length=1, description="Phase name")
    duration_weeks: int = Field(..., ge=1, le=52, description="Duration in weeks")
    objectives: list[str] = Field(default_factory=list, description="Phase objectives")
    deliverables: list[str] = Field(default_factory=list, description="Phase deliverables")
    governance_milestone: str = Field("", description="Governance checkpoint")
    measurement_milestone: str = Field("", description="Success measurement")

    @field_validator("duration_weeks")
    @classmethod
    def validate_duration(cls, v):
        if not 1 <= v <= 52:
            raise ValueError("duration_weeks must be between 1 and 52")
        return v


class RiskItem(BaseModel):
    """A single risk in the risk matrix."""

    risk_id: str = Field(..., min_length=1, description="Unique risk identifier")
    category: str = Field(..., min_length=1, description="Risk category")
    description: str = Field(..., min_length=10, description="Risk description")
    severity: RiskSeverity = Field(..., description="Risk severity level")
    mitigation: str = Field(..., min_length=10, description="Mitigation strategy")
    owner: str = Field("Platform Team", description="Risk owner")

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("description must be at least 10 characters")
        return v.strip()


class AssumptionItem(BaseModel):
    """A labeled assumption in the proposal."""

    assumption_id: str = Field(..., min_length=1, description="Unique assumption ID")
    statement: str = Field(..., min_length=5, description="Assumption statement")
    basis: str = Field("analyst judgment", description="Basis for assumption")
    section_id: str = Field("", description="Related section ID")

    @field_validator("statement")
    @classmethod
    def validate_statement(cls, v):
        if len(v.strip()) < 5:
            raise ValueError("statement must be at least 5 characters")
        return v.strip()


class ProposalSection(BaseModel):
    """One section of a generated proposal."""

    section_id: str = Field(..., min_length=1, description="Unique section ID")
    heading: str = Field(..., min_length=1, description="Section heading")
    body: str = Field(..., min_length=50, description="Section body content")
    is_deterministic: bool = Field(True, description="Whether content is deterministic")
    assumptions: list[AssumptionItem] = Field(default_factory=list, description="Section assumptions")
    evidence: list[str] = Field(default_factory=list, description="Supporting evidence")
    word_count: int = Field(0, ge=0, description="Word count")

    @field_validator("body")
    @classmethod
    def validate_body(cls, v):
        if len(v.strip()) < 50:
            raise ValueError("body must be at least 50 characters")
        return v.strip()


class RfpConfig(BaseModel):
    """RFP generation configuration."""

    min_quality_score: float = Field(0.7, ge=0, le=1, description="Minimum quality threshold")
    max_sections: int = Field(10, ge=1, le=50, description="Maximum sections")
    max_roadmap_phases: int = Field(5, ge=1, le=10, description="Maximum roadmap phases")
    max_risks: int = Field(20, ge=1, le=50, description="Maximum risks")
    require_architecture_review: bool = Field(True, description="Require architecture review")
    require_risk_assessment: bool = Field(True, description="Require risk assessment")


class RfpRequest(BaseModel):
    """Input contract for a single RFP proposal generation run."""

    problem_statement: str = Field(..., min_length=20, description="Problem to solve")
    industry: str = Field("technology", min_length=2, description="Industry sector")
    company_size: str = Field("", description="Company size category")
    security_requirements: list[str] = Field(default_factory=list, description="Security requirements")
    architecture_posture: ArchitecturePosture = Field("cloud-first", description="Architecture approach")
    delivery_timeline_weeks: int = Field(0, ge=0, le=104, description="Delivery timeline")
    existing_tooling: list[str] = Field(default_factory=list, description="Existing tools")
    config: RfpConfig = Field(default_factory=RfpConfig, description="RFP configuration")
    dry_run: bool = Field(False, description="Dry run mode")
    trace_id: str = Field("", description="Trace identifier")

    @field_validator("problem_statement")
    @classmethod
    def validate_problem(cls, v):
        if len(v.strip()) < 20:
            raise ValueError("problem_statement must be at least 20 characters")
        return v.strip()

    @field_validator("delivery_timeline_weeks")
    @classmethod
    def validate_timeline(cls, v):
        if v < 0 or v > 104:
            raise ValueError("delivery_timeline_weeks must be between 0 and 104")
        return v


class RfpResult(BaseModel):
    """Output contract for a single RFP proposal generation run."""

    trace_id: str = Field("", description="Trace identifier")
    industry: str = Field("", description="Industry sector")
    status: ProposalStatus = Field("pending", description="Generation status")
    sections: list[ProposalSection] = Field(default_factory=list, description="Generated sections")
    roadmap: list[RoadmapPhase] = Field(default_factory=list, description="Implementation roadmap")
    risks: list[RiskItem] = Field(default_factory=list, description="Identified risks")
    assumptions: list[AssumptionItem] = Field(default_factory=list, description="Declared assumptions")
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
        """Check if RFP passed all gates."""
        return len(self.gate_violations) == 0 and self.status in ("complete", "dry_run")

    @field_validator("quality_score")
    @classmethod
    def validate_quality(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("quality_score must be between 0.0 and 1.0")
        return v


class RfpRunSummary(BaseModel):
    """Top-level run summary artifact."""

    trace_id: str = Field("", description="Trace identifier")
    app: str = Field("apps_rfp", description="Application name")
    version: str = Field("1.0.0", description="Version")
    status: str = Field("pending", description="Run status")
    industry: str = Field("", description="Industry sector")
    sections_generated: int = Field(0, ge=0, description="Sections generated")
    roadmap_phases: int = Field(0, ge=0, description="Roadmap phases")
    risks_identified: int = Field(0, ge=0, description="Risks identified")
    assumptions_declared: int = Field(0, ge=0, description="Assumptions declared")
    quality_score: float = Field(0.0, ge=0, le=1, description="Overall quality score")
    gate_violations: list[str] = Field(default_factory=list, description="Gate violations")
    artifacts: list[str] = Field(default_factory=list, description="Generated artifacts")
    dry_run: bool = Field(False, description="Dry run mode")
    error: str = Field("", description="Error message")
    provenance: dict = Field(default_factory=dict, description="Provenance metadata")

    def to_dict(self) -> dict:
        """Export as dictionary."""
        return self.dict() if hasattr(self, "dict") and not hasattr(self, "model_dump") else self.model_dump()

    class Config:
        json_schema_extra = {
            "example": {
                "trace_id": "RFP-2024-001",
                "app": "apps_rfp",
                "version": "1.0.0",
                "status": "complete",
                "industry": "technology",
                "sections_generated": 8,
                "roadmap_phases": 4,
                "risks_identified": 12,
                "assumptions_declared": 5,
                "quality_score": 0.85,
            },
        }
