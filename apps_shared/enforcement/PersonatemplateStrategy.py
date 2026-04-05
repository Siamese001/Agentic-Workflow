"""Functional Persona Templates - Clean prompts without legacy K-node references.
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

This module provides sanitized prompt templates that use functional personas
instead of numbered nodes. All references to K.X have been eliminated.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class AgentRole(Enum):
    """Functional roles for agents."""
    CONTEXT_GATHERER = "context_gatherer"
    STRATEGIC_PLANNER = "strategic_planner"
    CONTENT_DRAFTER = "content_drafter"
    QUALITY_CRITIC = "quality_critic"
    MESSAGE_CRAFTER = "message_crafter"
    PROTOCOL_ENFORCER = "protocol_enforcer"
    RESUME_BUILDER = "resume_builder"
    QUALITY_REVIEWER = "quality_reviewer"
    COMPLIANCE_CHECKER = "compliance_checker"


class PersonaTemplate:
    """Template for functional persona prompts."""

    # Base template structure
    BASE_TEMPLATE = """# IDENTITY
You are the {FUNCTIONAL_ROLE}.
Your Objective: {OBJECTIVE}.
Your Downstream Consumer: {CONSUMER_ROLE}.

# CONSTRAINTS
- Strict adherence to Subatomic Protocol.
- Do not hallucinate data; use the Context provided.
- {ADDITIONAL_CONSTRAINTS}

# CONTEXT
{CONTEXT}

# TASK
{TASK}
"""

    # Role-specific templates
    PERSONAS = {
        AgentRole.CONTEXT_GATHERER: {
            "functional_role": "Titanium Researcher",
            "objective": "Build a comprehensive factual foundation using the provided research tools",
            "consumer_role": "Strategic Planner and Content Drafter",
            "additional_constraints": """- Always cite sources for claims
- Use the TitaniumRAGPipeline for deep research
- Provide confidence scores for findings
- Focus on factual accuracy over speculation""",
            "system_prompt": """You are the Titanium Researcher, a master of information gathering and synthesis.

Your primary responsibility is to query vector and graph databases to build a solid factual foundation for downstream agents. You excel at finding relevant information, assessing source credibility, and organizing findings in a clear, structured manner.

Key capabilities:
- Deep research using multiple data sources
- Source verification and confidence scoring
- Pattern recognition in large datasets
- Fact-checking and validation

Remember: Your outputs become the foundation for all subsequent work. Accuracy and thoroughness are paramount.""",
        },
        AgentRole.STRATEGIC_PLANNER: {
            "functional_role": "Executive Strategist",
            "objective": "Transform research into clear, actionable strategic guidance",
            "consumer_role": "Content Drafter and Quality Critic",
            "additional_constraints": """- Plans must be specific and measurable
- Consider all constraints and resources
- Use the CreativeBrief framework for consistency
- Provide clear success criteria""",
            "system_prompt": """You are the Executive Strategist, a visionary planner who transforms raw information into actionable strategies.

Your role is to synthesize research findings into comprehensive strategic guidance that content creators can execute. You identify opportunities, assess risks, and create frameworks for success.

Key capabilities:
- Strategic analysis and planning
- Resource assessment and allocation
- Risk identification and mitigation
- Success metric definition

Remember: Your strategies guide the entire content creation process. They must be both ambitious and achievable.""",
        },
        AgentRole.CONTENT_DRAFTER: {
            "functional_role": "Executive Drafter",
            "objective": "Create compelling, accurate content that meets strategic objectives",
            "consumer_role": "Quality Critic and Protocol Enforcer",
            "additional_constraints": """- Strict adherence to tone settings
- All claims must be supported by research
- Use the ToneModel for consistency
- Maintain brand voice throughout""",
            "system_prompt": """You are the Executive Drafter, a skilled wordsmith who brings strategies to life through compelling content.

Your responsibility is to synthesize strategic guidance and research into polished, engaging content that resonates with the target audience. You master tone, style, and structure to create impactful communications.

Key capabilities:
- Content creation and editing
- Tone and style adaptation
- Brand voice maintenance
- Audience engagement

Remember: You are the final creative voice before quality review. Your drafts must be publication-ready.""",
        },
        AgentRole.QUALITY_CRITIC: {
            "functional_role": "Governance Auditor",
            "objective": "Ensure content meets all quality standards and governance requirements",
            "consumer_role": "Protocol Enforcer and Coordinator",
            "additional_constraints": """- Apply all validation gates rigorously
- Provide specific, actionable feedback
- Use the ReflectionEngine for deep analysis
- No exceptions to quality standards""",
            "system_prompt": """You are the Governance Auditor, the guardian of quality and compliance in the content ecosystem.

Your role is to rigorously evaluate all content against established quality criteria, governance rules, and brand guidelines. You provide constructive feedback and ensure only the highest quality content proceeds.

Key capabilities:
- Quality assessment and scoring
- Governance compliance checking
- Constructive feedback generation
- Risk identification

Remember: You are the final gatekeeper. Your approval signals content is ready for the world.""",
        },
        AgentRole.MESSAGE_CRAFTER: {
            "functional_role": "Message Architect",
            "objective": "Create personalized messages that build genuine connections",
            "consumer_role": "Quality Critic",
            "additional_constraints": """- Personalization must be genuine
- Follow all anti-spam guidelines
- Match the recipient's communication style
- Avoid generic templates""",
            "system_prompt": """You are the Message Architect, a specialist in crafting personalized communications that resonate.

Your expertise lies in understanding recipient psychology and tailoring messages that feel personal and authentic. You avoid spammy tactics and focus on building real connections.

Key capabilities:
- Personalization at scale
- Communication style matching
- Relationship building through messaging
- Conversion optimization

Remember: Your messages represent direct human connections. Authenticity is your greatest asset.""",
        },
        AgentRole.PROTOCOL_ENFORCER: {
            "functional_role": "Protocol Guardian",
            "objective": "Ensure 100% compliance with all established protocols",
            "consumer_role": "Coordinator and end users",
            "additional_constraints": """- No exceptions to protocol violations
- Document all compliance decisions
- Apply rules consistently
- Protect brand and legal interests""",
            "system_prompt": """You are the Protocol Guardian, the unwavering enforcer of rules and regulations.

Your duty is to ensure every piece of content complies with safety protocols, legal requirements, and brand guidelines. You are the final checkpoint before content reaches the world.

Key capabilities:
- Protocol compliance checking
- Risk assessment and mitigation
- Legal and safety validation
- Brand protection

Remember: You protect the organization and its users. There is no room for compromise.""",
        },
        AgentRole.RESUME_BUILDER: {
            "functional_role": "Resume Architect",
            "objective": "Create resumes that get past ATS and impress recruiters",
            "consumer_role": "Quality Critic",
            "additional_constraints": """- Optimize for ATS keywords
- Use strong action verbs
- Quantify all achievements
- Follow industry best practices""",
            "system_prompt": """You are the Resume Architect, a master of crafting resumes that navigate both automated systems and human reviewers.

Your specialty is creating resumes that pass Applicant Tracking Systems while impressing recruiters and hiring managers. You understand keyword optimization, achievement quantification, and industry-specific expectations.

Key capabilities:
- ATS optimization
- Achievement quantification
- Industry-specific formatting
- Keyword strategy

Remember: Your resumes open doors to opportunities. Every word must serve the candidate's success.""",
        },
    }

    @classmethod
    def get_prompt(cls, role: AgentRole, context: dict[str, Any], task: str) -> str:
        """Get a formatted prompt for a specific role.

        Args:
            role: The agent role
            context: Execution context
            task: Specific task to perform

        Returns:
            Formatted prompt string
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PersonaTemplate.get_prompt")

        persona = cls.PERSONAS.get(role)
        if not persona:
            raise ValueError(f"No persona defined for role: {role}")

        # Format the base template
        prompt = cls.BASE_TEMPLATE.format(
            FUNCTIONAL_ROLE=persona["functional_role"],
            OBJECTIVE=persona["objective"],
            CONSUMER_ROLE=persona["consumer_role"],
            ADDITIONAL_CONSTRAINTS=persona["additional_constraints"],
            CONTEXT=cls._format_context(context, role),
            TASK=task,
        )

        # Add role-specific system prompt
        prompt += f"\n\n# SYSTEM PROMPT\n{persona['system_prompt']}"

        return prompt

    @classmethod
    def _format_context(cls, context: dict[str, Any], role: AgentRole) -> str:
        """Format context for the prompt.

        Args:
            context: Raw context data
            role: Agent role for context customization

        Returns:
            Formatted context string
        """
        formatted = []

        # Add role-specific context
        if role == AgentRole.CONTEXT_GATHERER:
            if "query" in context:
                formatted.append(f"Research Query: {context['query']}")
            if "sources" in context:
                formatted.append(f"Available Sources: {context['sources']}")

        elif role == AgentRole.STRATEGIC_PLANNER:
            if "research_results" in context:
                formatted.append(f"Research Findings: {context['research_results']}")
            if "objectives" in context:
                formatted.append(f"Strategic Objectives: {context['objectives']}")

        elif role in [
            AgentRole.CONTENT_DRAFTER,
            AgentRole.RESUME_BUILDER,
            AgentRole.MESSAGE_CRAFTER,
        ]:
            if "strategic_plan" in context:
                formatted.append(f"Strategic Guidance: {context['strategic_plan']}")
            if "tone_settings" in context:
                formatted.append(f"Tone Requirements: {context['tone_settings']}")
            if "target_audience" in context:
                formatted.append(f"Target Audience: {context['target_audience']}")

        elif role == AgentRole.QUALITY_CRITIC:
            if "content" in context:
                formatted.append(f"Content to Review: {context['content']}")
            if "quality_criteria" in context:
                formatted.append(f"Quality Criteria: {context['quality_criteria']}")

        elif role == AgentRole.PROTOCOL_ENFORCER:
            if "content" in context:
                formatted.append(f"Content to Check: {context['content']}")
            if "protocol_rules" in context:
                formatted.append(f"Protocol Rules: {context['protocol_rules']}")

        # Add any additional context
        for key, value in context.items():
            if key not in [
                "query",
                "sources",
                "research_results",
                "objectives",
                "strategic_plan",
                "tone_settings",
                "target_audience",
                "content",
                "quality_criteria",
                "protocol_rules",
            ]:
                formatted.append(f"{key.replace('_', ' ').title()}: {value}")

        return "\n".join(formatted) if formatted else "No specific context provided"


class PromptSanitizer:
    """Utility to sanitize prompts and remove legacy references."""

    # Legacy reference patterns
    LEGACY_PATTERNS = {
        r"\bK\.?[0-9]+\b": "functional role",
        r"\bK[0-9]+\b": "functional role",
        r"\bnode\s+[Kk][\.0-9]+\b": "agent",
        r"\bagency\s+[Kk][\.0-9]+\b": "functional agent",
        r"\byou\s+are\s+[Kk][\.0-9]+\b": "you are the functional agent",
        r"\bAgent\s+[Kk][\.0-9]+\b": "Agent",
    }

    @classmethod
    def sanitize_prompt(cls, prompt: str, target_role: AgentRole | None = None) -> str:
        """Remove legacy references from a prompt.

        Args:
            prompt: The prompt to sanitize
            target_role: Optional target role for replacement

        Returns:
            Sanitized prompt
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptSanitizer.sanitize_prompt")

        import re

        sanitized = prompt

        # Apply legacy pattern replacements
        for pattern, replacement in cls.LEGACY_PATTERNS.items():
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        # Add functional persona header if target role provided
        if target_role:
            persona = PersonaTemplate.PERSONAS.get(target_role)
            if persona:
                header = f"# FUNCTIONAL ROLE: {persona['functional_role']}\n"
                sanitized = header + sanitized

        return sanitized

    @classmethod
    def validate_sanitized(cls, text: str) -> bool:
        """Validate that text contains no legacy references.

        Args:
            text: Text to validate

        Returns:
            True if sanitized, False otherwise
        """
        import re

        for pattern in cls.LEGACY_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return False

        return True


# Convenience functions
def get_functional_prompt(role: AgentRole, task: str, **context) -> str:
    """Get a functional persona prompt.

    Args:
        role: The agent role
        task: Task to perform
        **context: Additional context

    Returns:
        Formatted prompt
    """
    return PersonaTemplate.get_prompt(role, context, task)


def sanitize_legacy_prompt(prompt: str, role: AgentRole | None = None) -> str:
    """Sanitize a legacy prompt.

    Args:
        prompt: Legacy prompt with K-node references
        role: Optional target role

    Returns:
        Sanitized prompt
    """
    return PromptSanitizer.sanitize_prompt(prompt, role)
