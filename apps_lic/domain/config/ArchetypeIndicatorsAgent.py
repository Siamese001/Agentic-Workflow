"""
Configuration schemas for LIC agents.

Defines Pydantic models for type-safe configuration loading.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field


class ArchetypeIndicators(BaseModel):
    """Configuration for archetype classification indicators."""
    keywords: List[str]
    confidence: float


class ProfileAnalysisAgent(BaseModel):
    """Configuration for HOP1 Profile Analysis Agent."""
    archetype_indicators: Dict[str, ArchetypeIndicators]
    default_archetype: str
    default_confidence: float
    manual_override_threshold: float
    cxo_precedence_tokens: List[str] = Field(default_factory=lambda: ["ceo", "cto", "cfo", "chief", "president", "founder"])


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
    source_files: List[str]
    extraction_targets: List[str]


class Conditions(BaseModel):
    """Routing rule conditions."""
    connection_status: Optional[str] = None
    prior_message_count: Optional[Union[int, str]] = None
    prior_message_count_gt: Optional[Union[int, str]] = None


class Constraints(BaseModel):
    """Routing rule constraints."""
    word_range: Optional[List[int]] = None
    char_limit: Optional[int] = None


class RoutingRule(BaseModel):
    """Individual routing rule configuration."""
    conditions: Conditions
    constraints: Constraints


class RoutingAgent(BaseModel):
    """Configuration for Routing Agent."""
    routing_rules: Dict[str, RoutingRule]


class GenerationAgent(BaseModel):
    """Configuration for Generation Agent."""
    base_temperatures: Dict[str, float]
    c_level_n_candidates: int


class ValidationAgent(BaseModel):
    """Configuration for Validation Agent."""
    severity_threshold: str
    rule_categories: List[str]


class GateDecisionAgent(BaseModel):
    """Configuration for Gate Decision Agent."""
    factual_failure_rules: List[str]
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
    report_sections: List[str]
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
