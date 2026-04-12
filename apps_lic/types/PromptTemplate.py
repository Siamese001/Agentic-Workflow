"""
SOVEREIGN KNOWLEDGE BASE (FROZEN v1.0) - LinkedIn Outreach Campaign
-------------------------------------------------------------------
Auto-generated for LinkedIn Campaign Optimizer system.
This module serves as the immutable 'brain' of the outreach system.

VIOLATION: NO MAGIC STRINGS. ALL PROMPTS/CONFIGS MUST BE ACCESSED VIA THIS REGISTRY.

Slot Taxonomy Integration:
- Unified 10-slot taxonomy: S0,D0,M0,I0,E0,C0,Y0,U0,H0,R0
- See agentic_core.prompt_governance.contracts.slot_contracts for definitions
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_reads_policy_state,
    _emit_snapshots_state,
)

_emit_applies_guardrail("p0", "lic_PromptTemplate", "p0_governance")
_emit_reads_policy_state("p0", "lic_PromptTemplate", "policy_binding")
_emit_snapshots_state("p0", "lic_PromptTemplate", "state_snapshot")


# -----------------------------------------------------------------------------
# LINKEDIN CAMPAIGN PROMPT DEFINITIONS
# -----------------------------------------------------------------------------


class LicPromptEntry(BaseModel):
    """Single immutable prompt definition for LinkedIn outreach campaigns."""

    prompt_id: str
    description: str
    system_prompt: str
    user_template: str
    required_context: list[str] = Field(default_factory=list)
    optional_context: list[str] = Field(default_factory=list)
    message_type: str = "connection"  # connection, followup, content_share, recruiter
    max_tokens: int = 800
    temperature: float = 0.6
    version: str = "1.0"


class LicNodeEntry(BaseModel):
    """K-node configuration for LinkedIn campaign pipeline stages."""

    node_id: str
    description: str
    stage: str  # archetype, targeting, messaging, delivery, analytics
    capabilities: list[str] = Field(default_factory=list)
    timeout_seconds: int = 300
    retry_policy: str = "exponential_backoff"
    version: str = "1.0"


class LicGlobalRule(BaseModel):
    """Cross-cutting governance rule for all LinkedIn campaign operations."""

    rule_id: str
    description: str
    severity: str  # info, warning, error, fatal
    condition: str
    action: str


# -----------------------------------------------------------------------------
# FROZEN SNAPSHOT (Immutable Knowledge)
# -----------------------------------------------------------------------------

_LIC_PROMPTS: dict[str, LicPromptEntry] = {
    "lic_archetype_analysis": LicPromptEntry(
        prompt_id="lic_archetype_analysis",
        description="Analyze recipient archetype for message personalization",
        system_prompt="""You are a recipient archetype analysis specialist.
Analyze LinkedIn profiles and company information to identify:
- Professional archetype (decision maker, influencer, gatekeeper, etc.)
- Communication preferences
- Pain points and priorities
- Likely objections
- Engagement triggers""",
        user_template="""Analyze the following LinkedIn profile for archetype classification:

Profile Summary:
{profile_summary}

Current Role: {current_role}
Company Info: {company_info}
Industry: {industry}

Classify into:
1. Professional archetype (provide rationale)
2. Communication style preference
3. Likely pain points in their role
4. Key priorities and goals
5. Potential objections to outreach
6. Engagement triggers and interests

Output structured archetype profile for message personalization.""",
        required_context=["profile_summary", "current_role"],
        optional_context=["company_info", "industry", "recent_activity"],
        message_type="connection",
        max_tokens=1000,
        temperature=0.5,
        version="1.0",
    ),
    "lic_connection_request": LicPromptEntry(
        prompt_id="lic_connection_request",
        description="Generate personalized LinkedIn connection request",
        system_prompt="""You are a LinkedIn outreach specialist.
Write personalized, authentic connection requests that avoid spam triggers.
Key principles:
- Reference specific profile details
- Show genuine interest (not transactional)
- Keep under 300 characters
- No sales pitches in first message
- Natural, conversational tone""",
        user_template="""Generate LinkedIn connection request for:

Recipient Profile:
- Name: {recipient_name}
- Role: {recipient_role}
- Company: {recipient_company}
- Archetype: {archetype}
- Interests: {interests}

Sender Context:
- Your Role: {sender_role}
- Shared Connections: {shared_connections}
- Mutual Interests: {mutual_interests}

Draft connection request (max 300 characters) that:
1. References specific detail from their profile
2. Shows genuine interest in connecting
3. Is authentic and non-salesy
4. Would feel natural to receive""",
        required_context=["recipient_name", "recipient_role", "archetype"],
        optional_context=["recipient_company", "interests", "shared_connections"],
        message_type="connection",
        max_tokens=400,
        temperature=0.7,
        version="1.0",
    ),
    "lic_followup_message": LicPromptEntry(
        prompt_id="lic_followup_message",
        description="Generate follow-up message after connection acceptance",
        system_prompt="""You are a LinkedIn follow-up messaging specialist.
Write thoughtful follow-up messages that build relationships post-connection.
Avoid being pushy or sales-focused. Focus on value exchange and genuine relationship building.""",
        user_template="""Generate follow-up message for new LinkedIn connection:

Connection Info:
- Name: {recipient_name}
- Accepted: {connection_date}
- Archetype: {archetype}
- Their Recent Activity: {recent_activity}

Your Context:
- Goal: {outreach_goal}
- Relevant Expertise: {expertise}
- Shared Interests: {shared_interests}

Draft follow-up message that:
1. Thanks for connecting
2. References shared interests or their content
3. Offers value (insight, resource, introduction)
4. Opens conversation without being pushy
5. Appropriate tone for archetype""",
        required_context=["recipient_name", "archetype", "outreach_goal"],
        optional_context=["connection_date", "recent_activity", "expertise"],
        message_type="followup",
        max_tokens=600,
        temperature=0.6,
        version="1.0",
    ),
    "lic_campaign_message": LicPromptEntry(
        prompt_id="lic_campaign_message",
        description="Generate campaign-specific LinkedIn messages",
        system_prompt="""You are a LinkedIn campaign messaging specialist.
Create campaign-appropriate messages for LinkedIn outreach at scale.
Balance personalization with efficiency. Maintain authenticity while scaling.""",
        user_template="""Generate LinkedIn campaign message:

Campaign: {campaign_name}
Campaign Goal: {campaign_goal}
Message Type: {message_type}

Recipient Segment:
- Segment Name: {segment_name}
- Archetypes: {archetypes}
- Pain Points: {segment_pain_points}
- Interests: {segment_interests}

Personalization Data:
- Recipient Name: {recipient_name}
- Company: {recipient_company}
- Role: {recipient_role}
- Recent News/Activity: {recent_news}

Draft message that:
1. Addresses segment pain points
2. References personalization data naturally
3. Aligns with campaign goal
4. Matches message type expectations
5. Maintains authentic voice""",
        required_context=["campaign_name", "campaign_goal", "message_type", "segment_name"],
        optional_context=["archetypes", "segment_pain_points", "recent_news"],
        message_type="content_share",
        max_tokens=800,
        temperature=0.6,
        version="1.0",
    ),
}

_LIC_NODES: dict[str, LicNodeEntry] = {
    "archetype": LicNodeEntry(
        node_id="archetype",
        description="Recipient archetype analysis and classification",
        stage="archetype",
        capabilities=["profile_analysis", "archetype_classification", "preference_detection"],
        timeout_seconds=300,
        retry_policy="exponential_backoff",
        version="1.0",
    ),
    "targeting": LicNodeEntry(
        node_id="targeting",
        description="Campaign targeting and segmentation",
        stage="targeting",
        capabilities=["segment_definition", "audience_filtering", "priority_scoring"],
        timeout_seconds=180,
        retry_policy="exponential_backoff",
        version="1.0",
    ),
    "messaging": LicNodeEntry(
        node_id="messaging",
        description="Message personalization and generation",
        stage="messaging",
        capabilities=["personalization", "message_generation", "tone_matching"],
        timeout_seconds=300,
        retry_policy="exponential_backoff",
        version="1.0",
    ),
    "delivery": LicNodeEntry(
        node_id="delivery",
        description="Message delivery and scheduling",
        stage="delivery",
        capabilities=["scheduling", "rate_limiting", "delivery_optimization"],
        timeout_seconds=180,
        retry_policy="fixed_interval",
        version="1.0",
    ),
}

_LIC_RULES: dict[str, LicGlobalRule] = {
    "connection_rate": LicGlobalRule(
        rule_id="connection_rate",
        description="Daily connection requests must stay within LinkedIn limits",
        severity="error",
        condition="daily_connections > 100",
        action="throttle_and_alert",
    ),
    "message_personalization": LicGlobalRule(
        rule_id="message_personalization",
        description="Messages must meet minimum personalization threshold",
        severity="warning",
        condition="personalization_score < 0.6",
        action="flag_for_review",
    ),
    "spam_avoidance": LicGlobalRule(
        rule_id="spam_avoidance",
        description="Messages must not trigger spam detection patterns",
        severity="fatal",
        condition="spam_likelihood > 0.8",
        action="reject_and_escalate",
    ),
}


class LicSovereignKnowledge(BaseModel):
    """Immutable frozen snapshot of LinkedIn campaign domain knowledge."""

    version: str = "1.0"
    prompts: dict[str, LicPromptEntry]
    nodes: dict[str, LicNodeEntry]
    rules: dict[str, LicGlobalRule]


# -----------------------------------------------------------------------------
# FROZEN SNAPSHOT INSTANCE (The Immutable Brain)
# -----------------------------------------------------------------------------

FROZEN_SNAPSHOT = LicSovereignKnowledge(
    version="1.0",
    prompts=_LIC_PROMPTS,
    nodes=_LIC_NODES,
    rules=_LIC_RULES,
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
        raise KeyError(f"Prompt '{prompt_id}' not found in LinkedIn campaign knowledge base")
    return FROZEN_SNAPSHOT.prompts[prompt_id].user_template


def get_system_prompt(prompt_id: str) -> str:
    """Retrieve system prompt by ID.

    Returns the system_prompt string for the given prompt_id.
    Raises KeyError if prompt_id not found.
    """
    if prompt_id not in FROZEN_SNAPSHOT.prompts:
        raise KeyError(f"Prompt '{prompt_id}' not found in LinkedIn campaign knowledge base")
    return FROZEN_SNAPSHOT.prompts[prompt_id].system_prompt


def get_prompt_entry(prompt_id: str) -> LicPromptEntry:
    """Retrieve full prompt entry by ID."""
    if prompt_id not in FROZEN_SNAPSHOT.prompts:
        raise KeyError(f"Prompt '{prompt_id}' not found in LinkedIn campaign knowledge base")
    return FROZEN_SNAPSHOT.prompts[prompt_id]


def get_node_config(node_id: str) -> LicNodeEntry:
    """Retrieve K-node configuration by ID."""
    if node_id not in FROZEN_SNAPSHOT.nodes:
        raise KeyError(f"Node '{node_id}' not found in LinkedIn campaign knowledge base")
    return FROZEN_SNAPSHOT.nodes[node_id]


def get_global_rule(rule_id: str) -> LicGlobalRule:
    """Retrieve global rule by ID."""
    if rule_id not in FROZEN_SNAPSHOT.rules:
        raise KeyError(f"Rule '{rule_id}' not found in LinkedIn campaign knowledge base")
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
    "LicPromptEntry",
    "LicNodeEntry",
    "LicGlobalRule",
    "LicSovereignKnowledge",
    "get_prompt",
    "get_system_prompt",
    "get_prompt_entry",
    "get_node_config",
    "get_global_rule",
    "list_all_prompts",
    "list_all_nodes",
]
