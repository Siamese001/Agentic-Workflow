"""
Configuration schemas for LIC agents.

Canonical home for agent config Pydantic models.
Moved from apps_lic/reasoning/ArchetypeIndicatorsAgent.py (2026-03-11, P1-C).
"""

from pydantic import BaseModel, Field


DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants


class ArchetypeIndicators(BaseModel):
    """Configuration for archetype classification indicators."""

    keywords: list[str]
    confidence: float


class ProfileAnalysisAgent(BaseModel):
    """Configuration for HOP1 Profile Analysis Agent."""

    archetype_indicators: dict[str, ArchetypeIndicators]
    default_archetype: str
    default_confidence: float
    manual_override_threshold: float
    cxo_precedence_tokens: list[str] = Field(
        default_factory=lambda: ["ceo", "cto", "cfo", "chief", "president", "founder"],
    )


class VectorStoreQueryParams(BaseModel):
    """Parameters for vector store queries."""

    top_k: float
    similarity_threshold: float


class FallbackRAGParams(BaseModel):
    """Parameters for fallback RAG."""

    max_results: int
    timeout_seconds: int


class ResearchAgent(BaseModel):
    """Configuration for HOP2 Research Agent."""

    vector_store_query_params: VectorStoreQueryParams
    fallback_rag_params: FallbackRAGParams


class SenderGroundingAgent(BaseModel):
    """Configuration for Sender Grounding Agent."""

    source_files: list[str]
    extraction_targets: list[str]


class Conditions(BaseModel):
    """Routing rule conditions."""

    connection_status: str | None = None
    prior_message_count: int | str | None = None
    prior_message_count_gt: int | str | None = None


class Constraints(BaseModel):
    """Routing rule constraints."""

    word_range: list[int] | None = None
    char_limit: int | None = None


class RoutingRule(BaseModel):
    """Individual routing rule configuration."""

    conditions: Conditions
    constraints: Constraints


class RoutingAgent(BaseModel):
    """Configuration for Routing Agent."""

    routing_rules: dict[str, RoutingRule]


class GenerationAgent(BaseModel):
    """Configuration for Generation Agent."""

    base_temperatures: dict[str, float]
    c_level_n_candidates: int


class ValidationAgent(BaseModel):
    """Configuration for Validation Agent."""

    severity_threshold: str
    rule_categories: list[str]


class GateDecisionAgent(BaseModel):
    """Configuration for Gate Decision Agent."""

    factual_failure_rules: list[str]
    max_factual_loops: int
    max_creative_retries: int


class ScoringWeights(BaseModel):
    """QA scoring weights."""

    research: float
    alignment: float
    validation: float
    generation: float


class QAReportAgent(BaseModel):
    """Configuration for QA Report Agent."""

    report_sections: list[str]
    output_directory: str
    scoring_weights: ScoringWeights


class AgentSpecs(BaseModel):
    """Root configuration for all LIC agents."""

    profile_analysis_agent: ProfileAnalysisAgent
    research_agent: ResearchAgent
    sender_grounding_agent: SenderGroundingAgent
    routing_agent: RoutingAgent
    generation_agent: GenerationAgent
    validation_agent: ValidationAgent
    gate_decision_agent: GateDecisionAgent
    qa_report_agent: QAReportAgent
