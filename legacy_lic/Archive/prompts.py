# File: prompts.py
# Description: Prompt templates for the LIC workflow.

__version__ = "11.10"

from models import Route, Archetype

# NEW v11.9: Context-Aware CTA Templates
CTA_TEMPLATES = {
    Route.CONNECTION_REQ: {
        "default": None  # CONNECTION_REQ has no CTA per SPEC 3
    },
    Route.INMAIL: {
        Archetype.C_LEVEL: "Would you be open to a brief conversation about how [TOPIC] might align with your strategic priorities?",
        Archetype.EXECUTIVE: "I'd welcome the chance to discuss how [TOPIC] could support your team's objectives.",
        Archetype.SENIOR_TA: {
            "direct": "Would you have 15 minutes to discuss [TECHNICAL_TOPIC]?",
            "deferential": "If this aligns with your team's direction, I'd appreciate any guidance you could share."
        },
        Archetype.RECRUITER: "Would you be open to a conversation about roles that might match your team's needs?"
    },
    Route.EMAIL: {
        Archetype.C_LEVEL: "I'd value the opportunity to explore how [TOPIC] aligns with your vision for [COMPANY].",
        Archetype.EXECUTIVE: "Would you be open to a brief call to discuss [TOPIC]?",
        Archetype.SENIOR_TA: {
            "direct": "Could we schedule 20 minutes to dive into [TECHNICAL_TOPIC]?",
            "deferential": "If this resonates with your team's roadmap, I'd be grateful for any insights you could offer."
        },
        Archetype.RECRUITER: "I'd welcome a conversation about potential opportunities that could benefit your team."
    },
    Route.FOLLOW_UP: {
        "default": "Following up on my previous message - would you have time for a brief conversation this week?"
    }
}

# NEW v11.9: Archetype-Specific Generation Prompt Templates
ARCHETYPE_PROMPT_TEMPLATES = {
    Archetype.C_LEVEL: """
You are crafting an executive-level message that demonstrates thought leadership and strategic alignment.

TONE: Strategic, confident, focused on business impact and organizational transformation.
APPROACH: Lead with macro trends, demonstrate understanding of strategic challenges, position yourself as a peer with complementary expertise.
AVOID: Tactical details, overt sales language, assumptions about their specific pain points.
    """,
    Archetype.EXECUTIVE: """
You are crafting a professional message that emphasizes collaboration and mutual value.

TONE: Professional, collaborative, focused on team objectives and operational excellence.
APPROACH: Reference their role and responsibilities, demonstrate understanding of their team's challenges, offer concrete value.
AVOID: Overly formal language, generic value propositions, excessive deference.
    """,
    Archetype.SENIOR_TA: """
You are crafting a technical message for a senior technical authority (architect, principal engineer, tech lead).

TONE: Technical peer, respectful but confident, focused on architectural decisions and technical excellence.
APPROACH: Reference specific technologies or patterns, demonstrate technical credibility, respect their authority on technical direction.
AVOID: Marketing language, oversimplification of technical concepts, challenging their technical decisions.
    """,
    Archetype.RECRUITER: """
You are crafting a job-focused message that centers on role fit and candidate qualifications.

TONE: Warm, professional, focused on alignment between candidate skills and role requirements.
APPROACH: Lead with relevant experience, highlight specific skills that match job description, emphasize career growth potential.
AVOID: Generic qualifications, vague interest statements, over-selling unrelated experience.
    """
}