"""
SOVEREIGN KNOWLEDGE BASE (FROZEN v1.0) - Autonomous Research
------------------------------------------------------------
Auto-generated for Autonomous Research Engine system.
This module serves as the immutable 'brain' of the research system.

VIOLATION: NO MAGIC STRINGS. ALL PROMPTS/CONFIGS MUST BE ACCESSED VIA THIS REGISTRY.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_reads_policy_state,
    _emit_snapshots_state,
)

_emit_applies_guardrail("p0", "research_PromptTemplate", "p0_governance")
_emit_reads_policy_state("p0", "research_PromptTemplate", "policy_binding")
_emit_snapshots_state("p0", "research_PromptTemplate", "state_snapshot")


# -----------------------------------------------------------------------------
# RESEARCH PROMPT DEFINITIONS
# -----------------------------------------------------------------------------

class ResearchPromptEntry(BaseModel):
    """Single immutable prompt definition for autonomous research."""
    prompt_id: str
    description: str
    system_prompt: str
    user_template: str
    required_context: list[str] = Field(default_factory=list)
    optional_context: list[str] = Field(default_factory=list)
    research_depth: str = "standard"  # quick, standard, deep
    max_tokens: int = 3000
    temperature: float = 0.4
    version: str = "1.0"


class ResearchNodeEntry(BaseModel):
    """K-node configuration for research pipeline stages."""
    node_id: str
    description: str
    stage: str  # discovery, analysis, synthesis, validation
    capabilities: list[str] = Field(default_factory=list)
    timeout_seconds: int = 600
    retry_policy: str = "exponential_backoff"
    version: str = "1.0"


class ResearchGlobalRule(BaseModel):
    """Cross-cutting governance rule for all research operations."""
    rule_id: str
    description: str
    severity: str  # info, warning, error, fatal
    condition: str
    action: str


# -----------------------------------------------------------------------------
# FROZEN SNAPSHOT (Immutable Knowledge)
# -----------------------------------------------------------------------------

_RESEARCH_PROMPTS: dict[str, ResearchPromptEntry] = {
    "research_query_expansion": ResearchPromptEntry(
        prompt_id="research_query_expansion",
        description="Expand research queries with related topics and keywords",
        system_prompt="""You are a research query expansion specialist.
Your task is to expand research queries into comprehensive search strategies.
Generate: related topics, alternative phrasings, key domain terms, and search operators.
Focus on maximizing information coverage while maintaining relevance.""",
        user_template="""Expand the following research query into a comprehensive search strategy:

Original Query: {query}
Domain Context: {domain_context}
Research Depth: {research_depth}
Time Range: {time_range}

Generate:
1. Related topics and sub-topics
2. Alternative phrasings and synonyms
3. Key domain terminology
4. Boolean search operators
5. Recommended source types""",
        required_context=["query", "domain_context", "research_depth"],
        optional_context=["time_range", "geographic_focus"],
        research_depth="standard",
        max_tokens=1500,
        temperature=0.4,
        version="1.0",
    ),
    "research_source_evaluation": ResearchPromptEntry(
        prompt_id="research_source_evaluation",
        description="Evaluate research sources for credibility and relevance",
        system_prompt="""You are a research source evaluation specialist.
Evaluate sources based on: credibility, relevance, recency, bias, and methodology.
Provide structured assessment with confidence scores.
Flag potential misinformation or low-quality sources.""",
        user_template="""Evaluate the following research source:

Source URL: {source_url}
Source Content (excerpt): {content_excerpt}
Publication Date: {publication_date}
Author Credentials: {author_info}

Evaluate on:
1. Credibility (author expertise, institutional backing)
2. Relevance to research topic
3. Recency and timeliness
4. Potential bias indicators
5. Methodology quality (if applicable)
6. Citation patterns

Provide overall quality score and recommendation.""",
        required_context=["source_url", "content_excerpt"],
        optional_context=["publication_date", "author_info"],
        research_depth="standard",
        max_tokens=1200,
        temperature=0.3,
        version="1.0",
    ),
    "research_synthesis": ResearchPromptEntry(
        prompt_id="research_synthesis",
        description="Synthesize findings from multiple research sources",
        system_prompt="""You are a research synthesis expert.
Synthesize findings from multiple sources into coherent insights.
Identify: agreements, contradictions, gaps, and emerging patterns.
Structure output for actionable decision-making.""",
        user_template="""Synthesize the following research findings:

Research Question: {research_question}
Sources Summary:
{sources_summary}

Key Findings by Source:
{findings_by_source}

Synthesize into:
1. Consensus points (high confidence)
2. Contested areas (conflicting evidence)
3. Knowledge gaps (limited evidence)
4. Emerging patterns and trends
5. Implications for research question""",
        required_context=["research_question", "sources_summary", "findings_by_source"],
        optional_context=["confidence_threshold", "priority_topics"],
        research_depth="deep",
        max_tokens=2000,
        temperature=0.3,
        version="1.0",
    ),
    "research_fact_extraction": ResearchPromptEntry(
        prompt_id="research_fact_extraction",
        description="Extract factual claims and evidence from research content",
        system_prompt="""You are a fact extraction specialist for research analysis.
Extract factual claims, evidence statements, and quantitative data.
Preserve source attribution. Distinguish facts from opinions.
Flag claims needing verification.""",
        user_template="""Extract factual claims from the following research content:

Content:
{content}

Extraction Requirements:
- Factual claims with confidence markers
- Quantitative data with units
- Evidence statements
- Source citations within content
- Claims requiring external verification

Format as structured list with source references.""",
        required_context=["content"],
        optional_context=["claim_types", "extraction_focus"],
        research_depth="standard",
        max_tokens=1500,
        temperature=0.2,
        version="1.0",
    ),
}

_RESEARCH_NODES: dict[str, ResearchNodeEntry] = {
    "discovery": ResearchNodeEntry(
        node_id="discovery",
        description="Source discovery and initial collection",
        stage="discovery",
        capabilities=["source_discovery", "query_expansion", "initial_collection"],
        timeout_seconds=300,
        retry_policy="exponential_backoff",
        version="1.0",
    ),
    "analysis": ResearchNodeEntry(
        node_id="analysis",
        description="Deep analysis of collected sources",
        stage="analysis",
        capabilities=["fact_extraction", "credibility_assessment", "pattern_detection"],
        timeout_seconds=600,
        retry_policy="exponential_backoff",
        version="1.0",
    ),
    "synthesis": ResearchNodeEntry(
        node_id="synthesis",
        description="Cross-source synthesis and insight generation",
        stage="synthesis",
        capabilities=["cross_reference", "conflict_resolution", "insight_generation"],
        timeout_seconds=600,
        retry_policy="exponential_backoff",
        version="1.0",
    ),
    "validation": ResearchNodeEntry(
        node_id="validation",
        description="Fact-checking and quality assurance",
        stage="validation",
        capabilities=["fact_check", "source_verification", "quality_score"],
        timeout_seconds=300,
        retry_policy="fixed_interval",
        version="1.0",
    ),
}

_RESEARCH_RULES: dict[str, ResearchGlobalRule] = {
    "source_minimum": ResearchGlobalRule(
        rule_id="source_minimum",
        description="Research must include minimum number of credible sources",
        severity="error",
        condition="credible_source_count < 3",
        action="expand_search_and_retry",
    ),
    "fact_verification": ResearchGlobalRule(
        rule_id="fact_verification",
        description="Critical claims must be verified by multiple sources",
        severity="warning",
        condition="unverified_critical_claims > 0",
        action="flag_for_manual_verification",
    ),
    "recency_check": ResearchGlobalRule(
        rule_id="recency_check",
        description="Research should prioritize recent sources when relevant",
        severity="info",
        condition="source_age_average > 2_years",
        action="suggest_fresh_search",
    ),
}


class ResearchSovereignKnowledge(BaseModel):
    """Immutable frozen snapshot of research domain knowledge."""
    version: str = "1.0"
    prompts: dict[str, ResearchPromptEntry]
    nodes: dict[str, ResearchNodeEntry]
    rules: dict[str, ResearchGlobalRule]


# -----------------------------------------------------------------------------
# FROZEN SNAPSHOT INSTANCE (The Immutable Brain)
# -----------------------------------------------------------------------------

FROZEN_SNAPSHOT = ResearchSovereignKnowledge(
    version="1.0",
    prompts=_RESEARCH_PROMPTS,
    nodes=_RESEARCH_NODES,
    rules=_RESEARCH_RULES,
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
        raise KeyError(f"Prompt '{prompt_id}' not found in research knowledge base")
    return FROZEN_SNAPSHOT.prompts[prompt_id].user_template


def get_system_prompt(prompt_id: str) -> str:
    """Retrieve system prompt by ID.

    Returns the system_prompt string for the given prompt_id.
    Raises KeyError if prompt_id not found.
    """
    if prompt_id not in FROZEN_SNAPSHOT.prompts:
        raise KeyError(f"Prompt '{prompt_id}' not found in research knowledge base")
    return FROZEN_SNAPSHOT.prompts[prompt_id].system_prompt


def get_prompt_entry(prompt_id: str) -> ResearchPromptEntry:
    """Retrieve full prompt entry by ID."""
    if prompt_id not in FROZEN_SNAPSHOT.prompts:
        raise KeyError(f"Prompt '{prompt_id}' not found in research knowledge base")
    return FROZEN_SNAPSHOT.prompts[prompt_id]


def get_node_config(node_id: str) -> ResearchNodeEntry:
    """Retrieve K-node configuration by ID."""
    if node_id not in FROZEN_SNAPSHOT.nodes:
        raise KeyError(f"Node '{node_id}' not found in research knowledge base")
    return FROZEN_SNAPSHOT.nodes[node_id]


def get_global_rule(rule_id: str) -> ResearchGlobalRule:
    """Retrieve global rule by ID."""
    if rule_id not in FROZEN_SNAPSHOT.rules:
        raise KeyError(f"Rule '{rule_id}' not found in research knowledge base")
    return FROZEN_SNAPSHOT.rules[rule_id]


def list_all_prompts() -> list[str]:
    """Return list of all available prompt IDs."""
    return list(FROZEN_SNAPSHOT.prompts.keys())


def list_all_nodes() -> list[str]:
    """Return list of all available node IDs."""
    return list(FROZEN_SNAPSHOT.nodes.keys())


# -----------------------------------------------------------------------------
# MODULE EXPORTS
# -----------------------------------------------------------------------------

__all__ = [
    "FROZEN_SNAPSHOT",
    "ResearchPromptEntry",
    "ResearchNodeEntry",
    "ResearchGlobalRule",
    "ResearchSovereignKnowledge",
    "get_prompt",
    "get_system_prompt",
    "get_prompt_entry",
    "get_node_config",
    "get_global_rule",
    "list_all_prompts",
    "list_all_nodes",
]
