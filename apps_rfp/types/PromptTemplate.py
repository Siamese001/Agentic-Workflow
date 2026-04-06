"""
SOVEREIGN KNOWLEDGE BASE (FROZEN v1.0) - RFP/Proposal Generation
---------------------------------------------------------------
Auto-generated for AI Proposal / RFP Generator system.
This module serves as the immutable 'brain' of the proposal system.

VIOLATION: NO MAGIC STRINGS. ALL PROMPTS/CONFIGS MUST BE ACCESSED VIA THIS REGISTRY.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_reads_policy_state,
    _emit_snapshots_state,
)

_emit_applies_guardrail("p0", "rfp_PromptTemplate", "p0_governance")
_emit_reads_policy_state("p0", "rfp_PromptTemplate", "policy_binding")
_emit_snapshots_state("p0", "rfp_PromptTemplate", "state_snapshot")


# -----------------------------------------------------------------------------
# RFP/PROPOSAL PROMPT DEFINITIONS
# -----------------------------------------------------------------------------

class RfpPromptEntry(BaseModel):
    """Single immutable prompt definition for RFP/proposal generation."""
    prompt_id: str
    description: str
    system_prompt: str
    user_template: str
    required_context: list[str] = Field(default_factory=list)
    optional_context: list[str] = Field(default_factory=list)
    proposal_section: str = "general"  # executive_summary, technical_approach, pricing, etc.
    max_tokens: int = 2500
    temperature: float = 0.35
    version: str = "1.0"


class RfpNodeEntry(BaseModel):
    """K-node configuration for RFP pipeline stages."""
    node_id: str
    description: str
    stage: str  # analysis, drafting, review, compliance
    capabilities: list[str] = Field(default_factory=list)
    timeout_seconds: int = 600
    retry_policy: str = "exponential_backoff"
    version: str = "1.0"


class RfpGlobalRule(BaseModel):
    """Cross-cutting governance rule for all RFP operations."""
    rule_id: str
    description: str
    severity: str  # info, warning, error, fatal
    condition: str
    action: str


# -----------------------------------------------------------------------------
# FROZEN SNAPSHOT (Immutable Knowledge)
# -----------------------------------------------------------------------------

_RFP_PROMPTS: dict[str, RfpPromptEntry] = {
    "rfp_requirement_analysis": RfpPromptEntry(
        prompt_id="rfp_requirement_analysis",
        description="Analyze RFP requirements and extract key information",
        system_prompt="""You are an RFP analysis specialist.
Analyze RFP documents to extract: requirements, evaluation criteria, mandatory qualifications, and submission guidelines.
Structure findings for proposal development. Flag ambiguous or conflicting requirements.""",
        user_template="""Analyze the following RFP document:

RFP Content:
{rfp_content}

Client Information:
{client_info}

Extract and structure:
1. Key requirements (functional and technical)
2. Evaluation criteria and weighting
3. Mandatory qualifications and certifications
4. Submission format and deadline
5. Risk factors and red flags
6. Competitive positioning insights""",
        required_context=["rfp_content", "client_info"],
        optional_context=["industry_context", "previous_proposals"],
        proposal_section="analysis",
        max_tokens=2000,
        temperature=0.3,
        version="1.0",
    ),
    "rfp_executive_summary": RfpPromptEntry(
        prompt_id="rfp_executive_summary",
        description="Generate compelling executive summary for proposal",
        system_prompt="""You are an executive summary writer for proposals.
Create compelling executive summaries that capture client attention.
Focus on: understanding of client needs, unique value proposition, key differentiators, and proof of capability.
Tone: Professional, confident, client-centric.""",
        user_template="""Generate executive summary for proposal to:

Client: {client_name}
RFP Title: {rfp_title}
Our Solution: {solution_overview}
Key Differentiators:
{key_differentiators}

Requirements Summary:
{requirements_summary}

Draft executive summary (max 500 words) that:
1. Demonstrates understanding of client needs
2. Presents our solution and value proposition
3. Highlights key differentiators
4. Includes proof of capability
5. Creates confidence in our ability to deliver""",
        required_context=["client_name", "rfp_title", "solution_overview", "key_differentiators"],
        optional_context=["requirements_summary", "client_priorities"],
        proposal_section="executive_summary",
        max_tokens=1000,
        temperature=0.4,
        version="1.0",
    ),
    "rfp_technical_approach": RfpPromptEntry(
        prompt_id="rfp_technical_approach",
        description="Draft technical approach section of proposal",
        system_prompt="""You are a technical proposal writer.
Draft clear, compelling technical approach sections that demonstrate expertise and methodology.
Include: methodology, timeline, deliverables, risk mitigation, and quality assurance.
Use specific examples and avoid generic statements.""",
        user_template="""Draft technical approach section for proposal:

Project Scope:
{project_scope}

Technical Requirements:
{technical_requirements}

Our Methodology:
{methodology}

Team Composition:
{team_composition}

Include:
1. Detailed methodology with phases and milestones
2. Technical architecture overview
3. Implementation timeline
4. Quality assurance processes
5. Risk mitigation strategies
6. Past performance examples""",
        required_context=["project_scope", "technical_requirements", "methodology"],
        optional_context=["team_composition", "similar_projects"],
        proposal_section="technical_approach",
        max_tokens=2500,
        temperature=0.35,
        version="1.0",
    ),
    "rfp_compliance_check": RfpPromptEntry(
        prompt_id="rfp_compliance_check",
        description="Check proposal for RFP compliance requirements",
        system_prompt="""You are a compliance checker for RFP responses.
Verify that proposals meet all mandatory requirements and submission guidelines.
Flag missing elements, formatting issues, and compliance gaps.
Provide actionable remediation steps.""",
        user_template="""Check the following proposal for RFP compliance:

RFP Requirements:
{rfp_requirements}

Proposal Content:
{proposal_content}

Compliance Checklist:
- All mandatory requirements addressed
- Format and structure compliance
- Required certifications included
- Page limits respected
- Submission deadline compliance
- Required forms and attachments

Provide:
1. Compliance score (0-100)
2. Missing mandatory elements
3. Formatting issues
4. Remediation recommendations""",
        required_context=["rfp_requirements", "proposal_content"],
        optional_context=["submission_guidelines", "evaluation_criteria"],
        proposal_section="compliance",
        max_tokens=1500,
        temperature=0.2,
        version="1.0",
    ),
}

_RFP_NODES: dict[str, RfpNodeEntry] = {
    "analysis": RfpNodeEntry(
        node_id="analysis",
        description="RFP requirements analysis and extraction",
        stage="analysis",
        capabilities=["requirement_extraction", "criteria_analysis", "risk_assessment"],
        timeout_seconds=300,
        retry_policy="exponential_backoff",
        version="1.0",
    ),
    "drafting": RfpNodeEntry(
        node_id="drafting",
        description="Proposal content generation",
        stage="drafting",
        capabilities=["content_generation", "section_optimization", "win_theme_integration"],
        timeout_seconds=600,
        retry_policy="exponential_backoff",
        version="1.0",
    ),
    "review": RfpNodeEntry(
        node_id="review",
        description="Proposal review and quality assurance",
        stage="review",
        capabilities=["compliance_check", "quality_score", "consistency_review"],
        timeout_seconds=300,
        retry_policy="fixed_interval",
        version="1.0",
    ),
    "compliance": RfpNodeEntry(
        node_id="compliance",
        description="Final compliance verification",
        stage="compliance",
        capabilities=["mandatory_check", "format_validation", "submission_ready"],
        timeout_seconds=180,
        retry_policy="fixed_interval",
        version="1.0",
    ),
}

_RFP_RULES: dict[str, RfpGlobalRule] = {
    "mandatory_requirements": RfpGlobalRule(
        rule_id="mandatory_requirements",
        description="All mandatory requirements must be addressed",
        severity="fatal",
        condition="mandatory_requirements_missed > 0",
        action="halt_and_require_remediation",
    ),
    "compliance_score": RfpGlobalRule(
        rule_id="compliance_score",
        description="Compliance score must be above threshold",
        severity="error",
        condition="compliance_score < 90",
        action="flag_for_detailed_review",
    ),
    "submission_deadline": RfpGlobalRule(
        rule_id="submission_deadline",
        description="Proposal must be completed before submission deadline",
        severity="fatal",
        condition="completion_time > deadline_time",
        action="escalate_to_project_manager",
    ),
}


class RfpSovereignKnowledge(BaseModel):
    """Immutable frozen snapshot of RFP/proposal domain knowledge."""
    version: str = "1.0"
    prompts: dict[str, RfpPromptEntry]
    nodes: dict[str, RfpNodeEntry]
    rules: dict[str, RfpGlobalRule]


# -----------------------------------------------------------------------------
# FROZEN SNAPSHOT INSTANCE (The Immutable Brain)
# -----------------------------------------------------------------------------

FROZEN_SNAPSHOT = RfpSovereignKnowledge(
    version="1.0",
    prompts=_RFP_PROMPTS,
    nodes=_RFP_NODES,
    rules=_RFP_RULES,
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
        raise KeyError(f"Prompt '{prompt_id}' not found in RFP knowledge base")
    return FROZEN_SNAPSHOT.prompts[prompt_id].user_template


def get_system_prompt(prompt_id: str) -> str:
    """Retrieve system prompt by ID.

    Returns the system_prompt string for the given prompt_id.
    Raises KeyError if prompt_id not found.
    """
    if prompt_id not in FROZEN_SNAPSHOT.prompts:
        raise KeyError(f"Prompt '{prompt_id}' not found in RFP knowledge base")
    return FROZEN_SNAPSHOT.prompts[prompt_id].system_prompt


def get_prompt_entry(prompt_id: str) -> RfpPromptEntry:
    """Retrieve full prompt entry by ID."""
    if prompt_id not in FROZEN_SNAPSHOT.prompts:
        raise KeyError(f"Prompt '{prompt_id}' not found in RFP knowledge base")
    return FROZEN_SNAPSHOT.prompts[prompt_id]


def get_node_config(node_id: str) -> RfpNodeEntry:
    """Retrieve K-node configuration by ID."""
    if node_id not in FROZEN_SNAPSHOT.nodes:
        raise KeyError(f"Node '{node_id}' not found in RFP knowledge base")
    return FROZEN_SNAPSHOT.nodes[node_id]


def get_global_rule(rule_id: str) -> RfpGlobalRule:
    """Retrieve global rule by ID."""
    if rule_id not in FROZEN_SNAPSHOT.rules:
        raise KeyError(f"Rule '{rule_id}' not found in RFP knowledge base")
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
    "RfpPromptEntry",
    "RfpNodeEntry",
    "RfpGlobalRule",
    "RfpSovereignKnowledge",
    "get_prompt",
    "get_system_prompt",
    "get_prompt_entry",
    "get_node_config",
    "get_global_rule",
    "list_all_prompts",
    "list_all_nodes",
]
