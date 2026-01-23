"""
Configuration Schemas.

Defines the Pydantic models for type-safe configuration loading.
"""

from __future__ import annotations
from pydantic import BaseModel, Field


class ArchetypeIndicator(BaseModel):
    """Configuration for identifying specific user archetypes."""

    keywords: list[str]
    confidence: float = Field(..., ge=0.0, le=1.0)


class ProfileAnalysisConfig(BaseModel):
    """Specific settings for the Profile Analysis Agent."""

    archetype_indicators: dict[str, ArchetypeIndicator]
    default_archetype: str
    default_confidence: float
    manual_override_threshold: float


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
