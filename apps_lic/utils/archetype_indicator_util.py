"""
configuration Schemas.

Defines the Pydantic models for type-safe configuration loading.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# Constants for test compatibility
BATCH_SIZE = 32
BUFFER_SIZE = 8192
DEFAULT_SLEEP = 1.0
MAX_RETRIES = 3
THRESHOLD = 0.95


class ArchetypeIndicator(BaseModel):
    """configuration for identifying specific user archetypes."""

    keywords: list[str]
    confidence: float = Field(..., ge=0.0, le=1.0)


class ProfileAnalysisConfig(BaseModel):
    """Specific settings for the Profile Analysis Agent."""

    archetype_indicators: dict[str, ArchetypeIndicator]
    default_archetype: str
    default_confidence: float
    manual_override_threshold: float
    cxo_precedence_tokens: list[str] = Field(
        default_factory=lambda: ["CEO", "CFO", "COO", "CTO", "CMO", "CIO", "CISO", "CPO", "CRO"]
    )


class ResearchConfig(BaseModel):
    """Settings for the Research Agent."""

    vector_store_query_params: dict[str, float]
    fallback_rag_params: dict[str, int]


class SenderGroundingConfig(BaseModel):
    """Settings for Sender Grounding Agent."""

    source_files: list[str]
    extraction_targets: list[str]


class RouteConditions(BaseModel):
    """Conditions for route matching."""

    connection_status: str | None = None
    prior_message_count: int | None = None
    prior_message_count_gte: int | None = None
    prior_message_count_gt: int | None = None


class RouteConstraints(BaseModel):
    """Constraints for a specific route."""

    word_range: list[int]
    char_limit: int


class RouteDef(BaseModel):
    """Definition of a routing rule."""

    conditions: RouteConditions
    constraints: RouteConstraints


class QAReportConfig(BaseModel):
    """Settings for the QA Report Agent (Chronicler)."""

    report_sections: list[str]
    output_directory: str
    scoring_weights: dict[str, float]


class GateConfig(BaseModel):
    """Settings for the Gate Decision Agent (Governor)."""

    factual_failure_rules: list[str]
    max_factual_loops: int
    max_creative_retries: int


class ValidationConfig(BaseModel):
    """Settings for Validation Agent."""

    severity_threshold: str
    rule_categories: list[str]


class GenerationConfig(BaseModel):
    """Settings for Generation Agent."""

    base_temperatures: dict[str, float]
    c_level_n_candidates: int


class RoutingConfig(BaseModel):
    """Settings for Routing Agent."""

    routing_rules: dict[str, RouteDef]


class AgentSpecs(BaseModel):
    """Root configuration object for all Agent Specifications."""

    profile_analysis_agent: ProfileAnalysisConfig
    research_agent: ResearchConfig
    sender_grounding_agent: SenderGroundingConfig
    routing_agent: RoutingConfig
    generation_agent: GenerationConfig
    validation_agent: ValidationConfig
    gate_decision_agent: GateConfig
    qa_report_agent: QAReportConfig

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AgentSpecs:
        """Strict parsing of dictionary to AgentSpecs schema."""
        pa_data = data.get("profile_analysis_agent", {})
        indicators_data = pa_data.get("archetype_indicators", {})
        indicators = {
            key: ArchetypeIndicator(
                keywords=value.get("keywords", []), confidence=value.get("confidence", 0.0)
            )
            for key, value in indicators_data.items()
        }
        pa_config = ProfileAnalysisConfig(
            cxo_precedence_tokens=pa_data.get(
                "cxo_precedence_tokens", ["CEO", "CFO", "COO", "CTO", "CMO", "CIO", "CISO", "CPO", "CRO"]
            ),
            manual_override_threshold=pa_data.get("manual_override_threshold", 0.8),
            default_archetype=pa_data.get("default_archetype", "UNKNOWN"),
            default_confidence=pa_data.get("default_confidence", 0.0),
            archetype_indicators=indicators,
        )
        ra_data = data.get("research_agent", {})
        ra_config = ResearchConfig(
            vector_store_query_params=ra_data.get("vector_store_query_params", {}),
            fallback_rag_params=ra_data.get("fallback_rag_params", {}),
        )
        remaining = {
            key: value
            for key, value in data.items()
            if key not in {"profile_analysis_agent", "research_agent"}
        }
        return cls(profile_analysis_agent=pa_config, research_agent=ra_config, **remaining)
