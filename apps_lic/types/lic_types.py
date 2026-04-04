"""
apps_lic domain types — Lead Intelligence & Campaign.

All types are Pydantic models with strict validation.
Every artifact carries provenance. No silent pass — all failures recorded.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

CampaignStatus = Literal["draft", "pending", "running", "complete", "failed"]

ValidationVerdict = Literal["PASS", "FAIL", "WARN"]

ComplianceLevel = Literal["strict", "standard", "relaxed"]


class ValidationResult(BaseModel):
    """Outcome of validator execution with full provenance."""

    passed: bool = Field(..., description="Whether validation passed")
    reasons: list[str] = Field(default_factory=list, description="Validation reasons/issues")
    final_draft: str = Field("", description="Final validated draft content")
    attempts: int = Field(1, ge=1, description="Number of validation attempts")
    qa_result: dict = Field(default_factory=dict, description="QA metadata")
    latency_ms: float = Field(0.0, ge=0, description="Validation latency in ms")
    validator_version: str = Field("1.0.0", description="Validator version")

    @field_validator("attempts")
    @classmethod
    def validate_attempts(cls, v):
        if v < 1:
            raise ValueError("attempts must be at least 1")
        return v


class Draft(BaseModel):
    """Campaign draft container with validation metadata."""

    subject: str = Field(..., min_length=1, description="Email subject line")
    body: str = Field(..., min_length=1, description="Email body content")
    tone: str = Field("professional", description="Message tone")
    target_segment: str = Field("", description="Target recipient segment")

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("subject cannot be empty")
        return v.strip()

    @field_validator("body")
    @classmethod
    def validate_body(cls, v):
        if len(v.strip()) == 0:
            raise ValueError("body cannot be empty")
        return v.strip()

    def render(self) -> str:
        """Render draft as formatted string."""
        return f"Subject: {self.subject}\n\n{self.body}"


class DraftPackage(BaseModel):
    """Container for composed draft with supporting evidence."""

    draft: str = Field(..., min_length=1, description="Composed draft content")
    artifacts: dict[str, str] = Field(default_factory=dict, description="Supporting artifacts")
    total_latency_ms: int = Field(0, ge=0, description="Total composition latency")
    draft_version: str = Field("1.0.0", description="Draft schema version")
    trace_id: str = Field("", description="Trace identifier for provenance")

    def with_draft(self, new_draft: str) -> DraftPackage:
        """Create new package with updated draft."""
        return DraftPackage(
            draft=new_draft,
            artifacts=dict(self.artifacts),
            total_latency_ms=self.total_latency_ms,
            draft_version=self.draft_version,
            trace_id=self.trace_id,
        )


class CampaignConfig(BaseModel):
    """Campaign execution configuration."""

    name: str = Field(..., min_length=1, description="Campaign name")
    target_audience: str = Field(..., description="Target audience segment")
    compliance_level: ComplianceLevel = Field("standard", description="Compliance strictness")
    max_recipients: int = Field(1000, ge=1, le=100000, description="Maximum recipients")
    min_quality_score: int = Field(5, ge=1, le=10, description="Minimum quality threshold")
    require_approval: bool = Field(True, description="Require human approval")


class CampaignRequest(BaseModel):
    """Input contract for campaign execution."""

    campaign_id: str = Field(..., min_length=1, description="Unique campaign ID")
    config: CampaignConfig = Field(..., description="Campaign configuration")
    draft_inputs: list[Draft] = Field(default_factory=list, description="Input drafts")
    trace_id: str = Field("", description="Trace identifier")
    dry_run: bool = Field(False, description="Dry run mode")


class CampaignResult(BaseModel):
    """Output contract for campaign execution."""

    campaign_id: str = Field("", description="Campaign ID")
    status: CampaignStatus = Field("draft", description="Campaign status")
    drafts: list[DraftPackage] = Field(default_factory=list, description="Generated drafts")
    validations: list[ValidationResult] = Field(default_factory=list, description="Validation results")
    quality_scores: list[int] = Field(default_factory=list, description="Quality scores per draft")
    overall_score: float = Field(0.0, ge=0, le=10, description="Overall campaign score")
    gate_violations: list[str] = Field(default_factory=list, description="Gate violations")
    trace_id: str = Field("", description="Trace identifier")
    error: str = Field("", description="Error message if failed")

    @property
    def passed_gate(self) -> bool:
        """Check if campaign passed all gates."""
        return len(self.gate_violations) == 0 and self.status in ("complete", "draft")


class CampaignRunSummary(BaseModel):
    """Top-level campaign run summary artifact."""

    trace_id: str = Field("", description="Trace identifier")
    app: str = Field("apps_lic", description="Application name")
    version: str = Field("1.0.0", description="Version")
    campaign_id: str = Field("", description="Campaign ID")
    status: CampaignStatus = Field("draft", description="Run status")
    drafts_generated: int = Field(0, ge=0, description="Number of drafts generated")
    drafts_validated: int = Field(0, ge=0, description="Number of drafts validated")
    overall_score: float = Field(0.0, ge=0, le=10, description="Overall score")
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
                "trace_id": "LIC-2024-001",
                "app": "apps_lic",
                "version": "1.0.0",
                "campaign_id": "campaign-001",
                "status": "complete",
                "drafts_generated": 5,
                "drafts_validated": 5,
                "overall_score": 8.5,
            }
        }
