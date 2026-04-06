from __future__ import annotations

"Types and models for CapabilityAnalyzer."
import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

Logger: Any = logging.getLogger(__name__)


class CapabilityGapType(Enum):
    """Types of capability gaps."""

    MISSING_TOOL = "missing_tool"
    INSUFFICIENT_KNOWLEDGE = "insufficient_knowledge"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    REASONING_LIMITATION = "reasoning_limitation"
    INTEGRATION_FAILURE = "integration_failure"


class RecommendationType(Enum):
    """Types of recommendations."""

    ADD_TOOL = "add_tool"
    ADD_SUB_AGENT = "add_sub_agent"
    RETRAIN_AGENT = "retrain_agent"
    UPDATE_KNOWLEDGE = "update_knowledge"
    OPTIMIZE_PERFORMANCE = "optimize_performance"


class CapabilityGap(BaseModel):
    """Identified capability gap."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    gap_id: str = Field(..., description="Unique identifier for the capability gap")
    gap_type: CapabilityGapType = Field(..., description="Type of capability gap")
    description: str = Field(..., description="Description of the capability gap")
    affected_scenarios: list[str] = Field(..., description="Scenarios affected by this gap")
    failure_count: int = Field(..., ge=0, description="Number of failures observed")
    severity: float = Field(..., ge=0.0, le=1.0, description="Severity score (0.0 to 1.0)")
    evidence: list[str] = Field(
        default_factory=list, description="Evidence supporting the gap identification"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "gap_id": self.gap_id,
            "gap_type": self.gap_type.value,
            "description": self.description,
            "affected_scenarios": self.affected_scenarios,
            "failure_count": self.failure_count,
            "severity": self.severity,
            "evidence": self.evidence,
        }


class Recommendation(BaseModel):
    """Improvement Recommendation."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    recommendation_id: str = Field(..., description="Unique identifier for the recommendation")
    recommendation_type: RecommendationType = Field(..., description="Type of recommendation")
    title: str = Field(..., description="Short title of the recommendation")
    description: str = Field(..., description="Detailed description of the recommendation")
    addresses_gaps: list[str] = Field(..., description="List of gap IDs this recommendation addresses")
    priority: float = Field(..., ge=0.0, le=1.0, description="Priority score (0.0 to 1.0)")
    implementation_steps: list[str] = Field(
        default_factory=list, description="Steps to implement the recommendation"
    )
    estimated_impact: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Estimated impact score (0.0 to 1.0)"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "recommendation_id": self.recommendation_id,
            "recommendation_type": self.recommendation_type.value,
            "title": self.title,
            "description": self.description,
            "addresses_gaps": self.addresses_gaps,
            "priority": self.priority,
            "implementation_steps": self.implementation_steps,
            "estimated_impact": self.estimated_impact,
        }


class AnalysisReport(BaseModel):
    """Capability gap analysis report."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    report_id: str = Field(..., description="Unique identifier for the analysis report")
    agent_id: str = Field(..., description="ID of the analyzed agent")
    gaps_identified: list[CapabilityGap] = Field(..., description="List of identified capability gaps")
    recommendations: list[Recommendation] = Field(..., description="List of improvement recommendations")
    overall_health_score: float = Field(..., ge=0.0, le=1.0, description="Overall health score (0.0 to 1.0)")
    analysis_timestamp: float = Field(..., description="Timestamp of the analysis")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "report_id": self.report_id,
            "agent_id": self.agent_id,
            "gaps_identified": [g.to_dict() for g in self.gaps_identified],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "overall_health_score": self.overall_health_score,
            "analysis_timestamp": self.analysis_timestamp,
        }

_emit_reads_through("l4", "capability_gap_types", "urg_read_1")
_emit_reads_through("l4", "capability_gap_types", "urg_read_2")
_emit_reads_through("l4", "capability_gap_types", "urg_read_3")
_emit_reads_through("l4", "capability_gap_types", "urg_read_4")
_emit_reads_through("l4", "capability_gap_types", "urg_read_5")
_emit_reads_through("l4", "capability_gap_types", "urg_read_6")
_emit_reads_through("l4", "capability_gap_types", "urg_read_7")
_emit_reads_through("l4", "capability_gap_types", "urg_read_8")
_emit_reads_through("l4", "capability_gap_types", "urg_read_9")
_emit_reads_through("l4", "capability_gap_types", "urg_read_10")
_emit_reads_through("l4", "capability_gap_types", "urg_read_11")
_emit_reads_through("l4", "capability_gap_types", "urg_read_12")
_emit_reads_through("l4", "capability_gap_types", "urg_read_13")
_emit_reads_through("l4", "capability_gap_types", "urg_read_14")
_emit_reads_through("l4", "capability_gap_types", "urg_read_15")
_emit_reads_through("l4", "capability_gap_types", "urg_read_16")
_emit_reads_through("l4", "capability_gap_types", "urg_read_17")
_emit_reads_through("l4", "capability_gap_types", "urg_read_18")
_emit_reads_through("l4", "capability_gap_types", "urg_read_19")
_emit_reads_through("l4", "capability_gap_types", "urg_read_20")
_emit_reads_through("l4", "capability_gap_types", "urg_read_21")
_emit_reads_through("l4", "capability_gap_types", "urg_read_22")
_emit_reads_through("l4", "capability_gap_types", "urg_read_23")
_emit_reads_through("l4", "capability_gap_types", "urg_read_24")
_emit_reads_through("l4", "capability_gap_types", "urg_read_25")
_emit_reads_through("l4", "capability_gap_types", "urg_read_26")
_emit_reads_through("l4", "capability_gap_types", "urg_read_27")
_emit_reads_through("l4", "capability_gap_types", "urg_read_28")
_emit_reads_through("l4", "capability_gap_types", "urg_read_29")
_emit_reads_through("l4", "capability_gap_types", "urg_read_30")
_emit_reads_through("l4", "capability_gap_types", "urg_read_31")
_emit_reads_through("l4", "capability_gap_types", "urg_read_32")
_emit_reads_through("l4", "capability_gap_types", "urg_read_33")
