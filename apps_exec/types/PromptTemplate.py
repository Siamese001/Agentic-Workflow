"""
SOVEREIGN KNOWLEDGE BASE (FROZEN v1.0) - Executive Brief
--------------------------------------------------------
Auto-generated for Executive Brief Generation system.
This module serves as the immutable 'brain' of the exec brief system.

VIOLATION: NO MAGIC STRINGS. ALL PROMPTS/CONFIGS MUST BE ACCESSED VIA THIS REGISTRY.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Dict, List

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_reads_policy_state,
    _emit_snapshots_state,
)

_emit_applies_guardrail("p0", "exec_PromptTemplate", "p0_governance")
_emit_reads_policy_state("p0", "exec_PromptTemplate", "policy_binding")
_emit_snapshots_state("p0", "exec_PromptTemplate", "state_snapshot")


# -----------------------------------------------------------------------------
# EXEC BRIEF PROMPT DEFINITIONS
# -----------------------------------------------------------------------------

class ExecBriefPromptEntry(BaseModel):
    """Single immutable prompt definition for executive brief generation."""
    prompt_id: str
    description: str
    system_prompt: str
    user_template: str
    required_context: List[str] = Field(default_factory=list)
    optional_context: List[str] = Field(default_factory=list)
    target_audience: str = "executive"
    max_tokens: int = 2000
    temperature: float = 0.3
    version: str = "1.0"


class ExecBriefNodeEntry(BaseModel):
    """K-node configuration for exec brief pipeline stages."""
    node_id: str
    description: str
    stage: str  # ingestion, extraction, synthesis, drafting, review
    capabilities: List[str] = Field(default_factory=list)
    timeout_seconds: int = 300
    retry_policy: str = "exponential_backoff"
    version: str = "1.0"


class ExecBriefGlobalRule(BaseModel):
    """Cross-cutting governance rule for all exec brief operations."""
    rule_id: str
    description: str
    severity: str  # info, warning, error, fatal
    condition: str
    action: str


# -----------------------------------------------------------------------------
# FROZEN SNAPSHOT (Immutable Knowledge)
# -----------------------------------------------------------------------------

_EXEC_BRIEF_PROMPTS: Dict[str, ExecBriefPromptEntry] = {
    "exec_brief_intro": ExecBriefPromptEntry(
        prompt_id="exec_brief_intro",
        description="Generate executive brief introduction",
        system_prompt="""You are an executive brief writer specializing in concise, actionable summaries.
Your task is to create compelling introductions that capture executive attention immediately.
Focus on: key insights, strategic implications, and recommended actions.
Tone: Professional, confident, data-driven.""",
        user_template="""Create an executive brief introduction for:
Topic: {topic}
Key Data Points: {data_points}
Target Audience: {audience_level}
Desired Length: {length_words} words

Context:
{additional_context}""",
        required_context=["topic", "data_points", "audience_level", "length_words"],
        optional_context=["additional_context", "tone_preference"],
        target_audience="executive",
        max_tokens=800,
        temperature=0.3,
        version="1.0",
    ),
    "exec_brief_synthesis": ExecBriefPromptEntry(
        prompt_id="exec_brief_synthesis",
        description="Synthesize multiple sources into executive summary",
        system_prompt="""You are a synthesis expert for executive consumption.
Synthesize complex information into clear, actionable insights.
Structure: Key Findings → Strategic Implications → Recommended Actions.
Avoid jargon. Use bullet points for scanability.""",
        user_template="""Synthesize the following sources into an executive summary:

Sources:
{sources}

Key Questions to Address:
{key_questions}

Constraints:
- Max length: {max_length_words} words
- Focus on: {focus_areas}
- Include data citations: {include_citations}""",
        required_context=["sources", "key_questions", "max_length_words", "focus_areas"],
        optional_context=["include_citations", "priority_topics"],
        target_audience="executive",
        max_tokens=1500,
        temperature=0.3,
        version="1.0",
    ),
    "exec_brief_recommendations": ExecBriefPromptEntry(
        prompt_id="exec_brief_recommendations",
        description="Generate actionable recommendations for executives",
        system_prompt="""You are a strategic advisor to C-suite executives.
Generate clear, prioritized recommendations with:
- Action description
- Expected impact (quantified when possible)
- Resource requirements
- Timeline
- Risk assessment""",
        user_template="""Based on the following analysis, generate executive recommendations:

Analysis Summary:
{analysis_summary}

Business Context:
{business_context}

Constraints:
{constraints}

Format each recommendation as:
1. ACTION: [Clear action statement]
   IMPACT: [Quantified expected outcome]
   RESOURCES: [Required investment]
   TIMELINE: [Delivery timeframe]
   RISK: [Key risk factors]""",
        required_context=["analysis_summary", "business_context"],
        optional_context=["constraints", "budget_limit", "strategic_priorities"],
        target_audience="executive",
        max_tokens=1200,
        temperature=0.3,
        version="1.0",
    ),
    "exec_brief_data_extraction": ExecBriefPromptEntry(
        prompt_id="exec_brief_data_extraction",
        description="Extract key metrics and data points from documents",
        system_prompt="""You are a data extraction specialist for executive briefs.
Extract quantifiable metrics, KPIs, trends, and critical data points.
Preserve data provenance. Flag inconsistencies or gaps.""",
        user_template="""Extract executive-relevant data from the following content:

Content:
{content}

Extraction Focus:
{extraction_categories}

Required Outputs:
- Key metrics with values and units
- Trends (increasing/decreasing/stable)
- Benchmarks or comparisons
- Data quality notes

Format: Structured bullet points with source citations.""",
        required_context=["content", "extraction_categories"],
        optional_context=["data_quality_threshold", "time_period_focus"],
        target_audience="data_analyst",
        max_tokens=1000,
        temperature=0.2,
        version="1.0",
    ),
}

_EXEC_BRIEF_NODES: Dict[str, ExecBriefNodeEntry] = {
    "ingestion": ExecBriefNodeEntry(
        node_id="ingestion",
        description="Document ingestion and preprocessing",
        stage="ingestion",
        capabilities=["document_parsing", "format_conversion", "chunking"],
        timeout_seconds=120,
        retry_policy="exponential_backoff",
        version="1.0",
    ),
    "extraction": ExecBriefNodeEntry(
        node_id="extraction",
        description="Key information extraction from documents",
        stage="extraction",
        capabilities=["entity_extraction", "metric_extraction", "sentiment_analysis"],
        timeout_seconds=300,
        retry_policy="exponential_backoff",
        version="1.0",
    ),
    "synthesis": ExecBriefNodeEntry(
        node_id="synthesis",
        description="Multi-source synthesis and pattern detection",
        stage="synthesis",
        capabilities=["cross_reference", "conflict_detection", "insight_generation"],
        timeout_seconds=600,
        retry_policy="exponential_backoff",
        version="1.0",
    ),
    "drafting": ExecBriefNodeEntry(
        node_id="drafting",
        description="Executive brief draft generation",
        stage="drafting",
        capabilities=["content_generation", "structure_optimization", "tone_adjustment"],
        timeout_seconds=300,
        retry_policy="exponential_backoff",
        version="1.0",
    ),
    "review": ExecBriefNodeEntry(
        node_id="review",
        description="Quality assurance and policy compliance",
        stage="review",
        capabilities=["fact_check", "policy_check", "quality_score"],
        timeout_seconds=180,
        retry_policy="fixed_interval",
        version="1.0",
    ),
}

_EXEC_BRIEF_RULES: Dict[str, ExecBriefGlobalRule] = {
    "max_length": ExecBriefGlobalRule(
        rule_id="max_length",
        description="Executive brief must not exceed 2 pages",
        severity="warning",
        condition="output_length > 2000_words",
        action="trigger_compression_pipeline",
    ),
    "data_provenance": ExecBriefGlobalRule(
        rule_id="data_provenance",
        description="All data points must have source attribution",
        severity="error",
        condition="missing_citation_count > 0",
        action="flag_for_manual_review",
    ),
    "executive_tone": ExecBriefGlobalRule(
        rule_id="executive_tone",
        description="Content must be appropriate for C-suite audience",
        severity="fatal",
        condition="inappropriate_language_detected",
        action="halt_and_escalate",
    ),
}


class ExecSovereignKnowledge(BaseModel):
    """Immutable frozen snapshot of exec brief domain knowledge."""
    version: str = "1.0"
    prompts: Dict[str, ExecBriefPromptEntry]
    nodes: Dict[str, ExecBriefNodeEntry]
    rules: Dict[str, ExecBriefGlobalRule]


# -----------------------------------------------------------------------------
# FROZEN SNAPSHOT INSTANCE (The Immutable Brain)
# -----------------------------------------------------------------------------

FROZEN_SNAPSHOT = ExecSovereignKnowledge(
    version="1.0",
    prompts=_EXEC_BRIEF_PROMPTS,
    nodes=_EXEC_BRIEF_NODES,
    rules=_EXEC_BRIEF_RULES,
)


# -----------------------------------------------------------------------------
# PUBLIC API (Read-Only Access)
# -----------------------------------------------------------------------------

def get_prompt(prompt_id: str) -> str:
    """Retrieve prompt template by ID.

    Returns the user_template string for the given prompt_id.
    Raises KeyError if prompt_id not found.
    """
    if prompt_id not in FROZEN_SNAPSHOT.prompts:
        raise KeyError(f"Prompt '{prompt_id}' not found in exec brief knowledge base")
    return FROZEN_SNAPSHOT.prompts[prompt_id].user_template


def get_system_prompt(prompt_id: str) -> str:
    """Retrieve system prompt by ID.

    Returns the system_prompt string for the given prompt_id.
    Raises KeyError if prompt_id not found.
    """
    if prompt_id not in FROZEN_SNAPSHOT.prompts:
        raise KeyError(f"Prompt '{prompt_id}' not found in exec brief knowledge base")
    return FROZEN_SNAPSHOT.prompts[prompt_id].system_prompt


def get_prompt_entry(prompt_id: str) -> ExecBriefPromptEntry:
    """Retrieve full prompt entry by ID."""
    if prompt_id not in FROZEN_SNAPSHOT.prompts:
        raise KeyError(f"Prompt '{prompt_id}' not found in exec brief knowledge base")
    return FROZEN_SNAPSHOT.prompts[prompt_id]


def get_node_config(node_id: str) -> ExecBriefNodeEntry:
    """Retrieve K-node configuration by ID."""
    if node_id not in FROZEN_SNAPSHOT.nodes:
        raise KeyError(f"Node '{node_id}' not found in exec brief knowledge base")
    return FROZEN_SNAPSHOT.nodes[node_id]


def get_global_rule(rule_id: str) -> ExecBriefGlobalRule:
    """Retrieve global rule by ID."""
    if rule_id not in FROZEN_SNAPSHOT.rules:
        raise KeyError(f"Rule '{rule_id}' not found in exec brief knowledge base")
    return FROZEN_SNAPSHOT.rules[rule_id]


def list_all_prompts() -> List[str]:
    """Return list of all available prompt IDs."""
    return list(FROZEN_SNAPSHOT.prompts.keys())


def list_all_nodes() -> List[str]:
    """Return list of all available node IDs."""
    return list(FROZEN_SNAPSHOT.nodes.keys())


# -----------------------------------------------------------------------------
# MODULE EXPORTS
# -----------------------------------------------------------------------------

__all__ = [
    "FROZEN_SNAPSHOT",
    "ExecBriefPromptEntry",
    "ExecBriefNodeEntry",
    "ExecBriefGlobalRule",
    "ExecSovereignKnowledge",
    "get_prompt",
    "get_system_prompt",
    "get_prompt_entry",
    "get_node_config",
    "get_global_rule",
    "list_all_prompts",
    "list_all_nodes",
]
