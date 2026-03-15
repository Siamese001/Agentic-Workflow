"""
apps_rfp Configuration Schemas — AI Proposal / RFP Generator.

Pydantic models for type-safe configuration. Aligned with apps_rg pattern.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

_log = logging.getLogger(__name__)


class ProposalSectionConfig(BaseModel):
    """Schema for a single proposal section template."""

    section_id: str
    heading: str
    required: bool = True
    requires_assumptions: bool = False
    requires_evidence: bool = True
    max_words: int = Field(default=500, ge=50)


class IndustryProfileConfig(BaseModel):
    """Industry-specific configuration for proposal generation."""

    industry_id: str
    display_name: str
    regulatory_flags: list[str] = Field(default_factory=list)
    typical_pain_points: list[str] = Field(default_factory=list)
    preferred_architecture: str = "cloud-first"


class RoadmapConfig(BaseModel):
    """Phased roadmap template configuration."""

    phases: list[str] = Field(default_factory=lambda: ["Discovery", "Foundation", "Pilot", "Scale", "Govern"])
    min_phases: int = Field(default=3, ge=1)
    require_governance_phase: bool = True
    require_measurement_phase: bool = True


class RiskMatrixConfig(BaseModel):
    """Risk matrix template configuration."""

    risk_categories: list[str] = Field(
        default_factory=lambda: [
            "technical_complexity",
            "data_quality",
            "regulatory_compliance",
            "change_management",
            "model_drift",
            "integration_risk",
        ]
    )
    severity_levels: list[str] = Field(default_factory=lambda: ["LOW", "MEDIUM", "HIGH", "CRITICAL"])


class ProposalOutputConfig(BaseModel):
    """Output configuration for RFP proposals."""

    output_dir: str = Field(default="rfp")
    artifact_prefix: str = Field(default="proposal")
    emit_run_summary: bool = True
    emit_json_manifest: bool = True
    dry_run: bool = False


class ProposalGateConfig(BaseModel):
    """Quality gates for proposal validation."""

    require_assumptions_labeled: bool = True
    require_governance_section: bool = True
    require_value_rationale: bool = True
    max_empty_sections: int = Field(default=0, ge=0)
    min_quality_score: float = Field(default=0.75, ge=0.0, le=1.0)


class RfpAgentSpecs(BaseModel):
    """Root configuration for all apps_rfp agent specifications."""

    version: str = "1.0.0"
    sections: list[ProposalSectionConfig] = Field(
        default_factory=lambda: [
            ProposalSectionConfig(section_id="executive_summary", heading="Executive Summary", required=True),
            ProposalSectionConfig(
                section_id="current_state",
                heading="Current State and Pain Points",
                required=True,
                requires_assumptions=True,
            ),
            ProposalSectionConfig(
                section_id="future_state",
                heading="Future State Architecture",
                required=True,
                requires_evidence=True,
            ),
            ProposalSectionConfig(
                section_id="implementation_roadmap",
                heading="Implementation Roadmap",
                required=True,
                requires_assumptions=True,
            ),
            ProposalSectionConfig(
                section_id="risk_and_governance", heading="Risk and Governance", required=True
            ),
            ProposalSectionConfig(
                section_id="value_case", heading="Value Case", required=True, requires_evidence=True
            ),
            ProposalSectionConfig(
                section_id="solution_appendix", heading="Solution Appendix", required=False
            ),
        ]
    )
    roadmap: RoadmapConfig = Field(default_factory=RoadmapConfig)
    risk_matrix: RiskMatrixConfig = Field(default_factory=RiskMatrixConfig)
    output: ProposalOutputConfig = Field(default_factory=ProposalOutputConfig)
    gate: ProposalGateConfig = Field(default_factory=ProposalGateConfig)
    industries: dict[str, IndustryProfileConfig] = Field(
        default_factory=lambda: {
            "financial_services": IndustryProfileConfig(
                industry_id="financial_services",
                display_name="Financial Services",
                regulatory_flags=["SOX", "GDPR", "MiFID II"],
                typical_pain_points=[
                    "manual compliance workflows",
                    "model explainability gaps",
                    "data silos",
                ],
                preferred_architecture="sovereign",
            ),
            "healthcare": IndustryProfileConfig(
                industry_id="healthcare",
                display_name="Healthcare",
                regulatory_flags=["HIPAA", "FDA 21 CFR Part 11"],
                typical_pain_points=[
                    "unstructured clinical notes",
                    "care coordination latency",
                    "audit trail gaps",
                ],
                preferred_architecture="hybrid",
            ),
            "technology": IndustryProfileConfig(
                industry_id="technology",
                display_name="Technology",
                regulatory_flags=[],
                typical_pain_points=["engineering velocity", "context switching", "knowledge fragmentation"],
                preferred_architecture="cloud-first",
            ),
            "government": IndustryProfileConfig(
                industry_id="government",
                display_name="Government / Public Sector",
                regulatory_flags=["FedRAMP", "FISMA", "ITAR"],
                typical_pain_points=["legacy system modernization", "data sovereignty", "approval latency"],
                preferred_architecture="sovereign",
            ),
        }
    )
    global_step_limit: int = Field(default=12)
    checkpoint_enabled: bool = True
    trace_persistence: bool = True

    @model_validator(mode="after")
    def validate_required_sections_present(self) -> RfpAgentSpecs:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RfpAgentSpecs.validate_required_sections_present")

        required_ids = {s.section_id for s in self.sections if s.required}
        must_have = {"executive_summary", "implementation_roadmap", "risk_and_governance", "value_case"}
        missing = must_have - required_ids
        if missing:
            raise ValueError(f"Required proposal sections missing: {missing}")
        return self


_SPEC_CACHE: RfpAgentSpecs | None = None


def load_rfp_specs(spec_path: str | None = None) -> RfpAgentSpecs:
    """Load RfpAgentSpecs from JSON file or return defaults."""
    global _SPEC_CACHE
    if _SPEC_CACHE is not None:
        return _SPEC_CACHE

    resolved: Path | None = None
    if spec_path:
        resolved = Path(spec_path)
    else:
        default = Path(__file__).parent / "rfp_agent_specs.json"
        if default.exists():
            resolved = default

    if resolved and resolved.exists():
        try:
            raw: dict[str, Any] = json.loads(resolved.read_text(encoding="utf-8"))
            _SPEC_CACHE = RfpAgentSpecs.model_validate(raw)
            return _SPEC_CACHE
        except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as exc:
            _log.warning("[apps_rfp] Failed to load specs from %s: %s — using defaults", resolved, exc)

    _SPEC_CACHE = RfpAgentSpecs()
    return _SPEC_CACHE
