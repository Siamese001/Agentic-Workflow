"""LEGACY FILE - Moved to legacy during Terminal Alignment Command
This file has fundamental architectural issues that require complete rewrite.
Status: DEPRECATED - Do not use in production
"""

# LEGACY CODE BELOW - COMMENTED OUT
# """K.3 Message Body Agent - Archetype-Specific Content Generation.

# This agent generates the message body with archetype-specific transition phrases,
# micro-structure enforcement, and placeholder detection blocking.
# """

# from apps_lic.shared.core.agent_base import LICAgentBase as Agent
# from typing import Any, Dict, List, Optional
# from dataclasses import dataclass, field
# import logging

# logger = logging.getLogger(__name__)


# @dataclass
# class K3Output:
#     """K.3 message body output."""

#     body: str
#     archetype: str
#     transition_phrase: str
#     insights_count: int
#     bullets_count: int
#     word_count: int
#     char_count: int
#     metadata: dict[str, Any]


# Archetype-specific transition phrases (from LinkedInCanonical v2.90)
# ARCHETYPE_TRANSITIONS = {
#     "C_LEVEL": "Two strategic insights I have gleaned from my research about {company}:",
#     "EXECUTIVE": "Two strategic insights I have gleaned from my clients about {company}:",
#     "SENIOR_TA": "Two insights from your profile that align with this role:",
#     "RECRUITER": "Two reasons I'm reaching out about this opportunity:",
# }

# Archetype-specific message templates
# ARCHETYPE_TEMPLATES = {
#     "C_LEVEL": {
#         "format": "ANALYST_LEVEL_PITCH",
#         "tone": "thought_leadership",
#         "formality": "high",
#         "insights_required": 2,
#         "bullets_required": 3,
#         "drq_required": True,  # Deep Research Query
#     },
#     "EXECUTIVE": {
#         "format": "EXECUTIVE_PITCH",
#         "tone": "strategic",
#         "formality": "moderate_high",
#         "insights_required": 2,
#         "bullets_required": 3,
#         "drq_required": False,
#     },
#     "SENIOR_TA": {
#         "format": "TA_PITCH",
#         "tone": "professional_warm",
#         "formality": "moderate",
#         "insights_required": 2,
#         "bullets_required": 3,
#         "profile_rag_mandatory": True,
#     },
#     "RECRUITER": {
#         "format": "RECRUITER_PITCH",
#         "tone": "job_focused",
#         "formality": "moderate",
#         "insights_required": 2,
#         "bullets_required": 3,
#     },
# }


# class K3_MessageBodyAgent(Agent):
#     """K.3 specialist agent for message body generation.

#     This agent generates archetype-specific message bodies with:
#     - Mandatory transition phrases
#     - Exactly 2 insights (numbered)
#     - Exactly 3 measurable bullets
#     - Placeholder detection blocking (LIC-QA-001)
#     - Metric source binding enforcement (LIC-QA-041)
#     """

#     def __init__(
#         self,
#         config: ReasoningConfig,
#         archetype: str,
#         route: str,
#         char_limit: int | None = None,
#     ):
#         """Initialize K.3 message body agent.

#         Args:
#             config: Reasoning configuration
#             archetype: Recipient archetype (C_LEVEL, EXECUTIVE, etc.)
#             route: Message route (INMAIL, CONNECTION_REQ, etc.)
#             char_limit: Character limit for route
#         """
#         super().__init__(config, k_node_id="K.3", element="Message Body")

#         self.archetype = archetype
#         self.route = route
#         self.char_limit = char_limit
#         self.template = ARCHETYPE_TEMPLATES.get(archetype, ARCHETYPE_TEMPLATES["EXECUTIVE"])

#         logger.info(
#             f"K.3 Message Body Agent initialized: "
#             f"archetype={archetype}, route={route}, char_limit={char_limit}"
#         )

#     async def execute(self, context: dict[str, Any]) -> K3Output:
#         """Execute K.3 message body generation.

#         Args:
#             context: Execution context with:
#                 - company_name: str
#                 - recipient_name: str
#                 - rag_insights: List[str] - RAG-derived insights
#                 - sender_bullets: List[str] - Sender credential bullets
#                 - metric_source_map: Dict - Metric to source mapping
#                 - regeneration_feedback: Optional[str]

#         Returns:
#             K3Output with message body
#         """
#         logger.info(f"Executing K.3 message body generation for {self.archetype}")

#         # Extract context
#         company_name = context.get("company_name", "the company")
#         recipient_name = context.get("recipient_name", "")
#         rag_insights = context.get("rag_insights", [])
#         sender_bullets = context.get("sender_bullets", [])
#         regeneration_feedback = context.get("regeneration_feedback")

#         # Build prompt
#         if regeneration_feedback:
#             prompt = self._build_regeneration_prompt(context, regeneration_feedback)
#         else:
#             prompt = self._build_initial_prompt(
#                 company_name, recipient_name, rag_insights, sender_bullets
#             )

#         # Generate with self-consistency if configured
#         if self.config.self_consistency > 1:
#             candidates = await self._call_llm_with_self_consistency(
#                 prompt, k=self.config.self_consistency
#             )
#             response = self._select_best_candidate(candidates, "length")
#         else:
#             response = await self._call_llm(prompt)

#         # Parse body components
#         body = response.strip()

#         # Extract transition phrase
#         transition_phrase = self._extract_transition_phrase(body, company_name)

#         # Count insights and bullets
#         insights_count = self._count_insights(body)
#         bullets_count = self._count_bullets(body)

#         # Calculate metrics
#         word_count = len(body.split())
#         char_count = len(body)

#         # Build output
#         output = K3Output(
#             body=body,
#             archetype=self.archetype,
#             transition_phrase=transition_phrase,
#             insights_count=insights_count,
#             bullets_count=bullets_count,
#             word_count=word_count,
#             char_count=char_count,
#             metadata={
#                 "k_node_id": self.k_node_id,
#                 "route": self.route,
#                 "template": self.template["format"],
#                 "temperature": self.config.temperature,
#             },
#         )

#         logger.info(
#             f"K.3 generation complete: {word_count} words, {char_count} chars, "
#             f"{insights_count} insights, {bullets_count} bullets"
#         )

#         return output

#     def _build_initial_prompt(
#         self,
#         company_name: str,
#         recipient_name: str,
#         rag_insights: list[str],
#         sender_bullets: list[str],
#     ) -> str:
#         """Build initial generation prompt.

#         Args:
#             company_name: Target company name
#             recipient_name: Recipient name
#             rag_insights: RAG-derived insights
#             sender_bullets: Sender credential bullets

#         Returns:
#             Formatted prompt
#         """
#         transition_phrase = ARCHETYPE_TRANSITIONS.get(
#             self.archetype, ARCHETYPE_TRANSITIONS["EXECUTIVE"]
#         ).format(company=company_name)

#         prompt = f"""Generate a professional LinkedIn message body for a {self.archetype} recipient.

# CRITICAL CONSTRAINTS (ZERO TOLERANCE):
# 1. Must include EXACT transition phrase: "{transition_phrase}"
# 2. Exactly 2 insights (numbered "1." and "2.")
# 3. Exactly 3 measurable bullets with metrics
# 4. NO placeholders ([NAME], {{company}}, etc.) - BLOCKING violation (LIC-QA-001)
# 5. Character limit: {self.char_limit if self.char_limit else "No limit"}

# ARCHETYPE TEMPLATE: {self.template["format"]}
# - Tone: {self.template["tone"]}
# - Formality: {self.template["formality"]}

# STRUCTURE:
# Hi {recipient_name},

# [Opening hook - 1 sentence]

# {transition_phrase}

# 1. [First insight from RAG - specific to {company_name}]
# 2. [Second insight from RAG - specific to {company_name}]

# [Bridge phrase: "A few highlights from my experience:"]

# • [Bullet 1 with metric and context]
# • [Bullet 2 with metric and context]
# • [Bullet 3 with metric and context]

# RAG INSIGHTS (use these):
# {chr(10).join(f"- {insight}" for insight in rag_insights[:5])}

# SENDER CREDENTIALS (use for bullets):
# {chr(10).join(f"- {bullet}" for bullet in sender_bullets[:5])}

# FORBIDDEN (LIC-QA-001):
# - [NAME], [COMPANY], {{name}}, {{company}}
# - <NAME>, <COMPANY>
# - PLACEHOLDER, TODO

# Generate the message body now:
# """

#         return prompt

#     def _build_regeneration_prompt(
#         self,
#         context: dict[str, Any],
#         feedback: str,
#     ) -> str:
#         """Build regeneration prompt with validation feedback.

#         Args:
#             context: Original context
#             feedback: Validation feedback

#         Returns:
#             Regeneration prompt
#         """
#         previous_body = context.get("previous_body", "")

#         prompt = f"""REGENERATION REQUIRED

# {feedback}

# PREVIOUS OUTPUT:
# {previous_body}

# CONSTRAINTS:
# - Must include exact transition phrase
# - Exactly 2 insights, exactly 3 bullets
# - NO placeholders (BLOCKING)
# - Character limit: {self.char_limit if self.char_limit else "No limit"}

# INSTRUCTIONS:
# Fix ONLY the failing sections listed in feedback.
# Maintain all other content unchanged.

# Generate the corrected message body:
# """

#         return prompt

#     def _extract_transition_phrase(self, body: str, company_name: str) -> str:
#         """Extract transition phrase from body.

#         Args:
#             body: Message body
#             company_name: Company name

#         Returns:
#             Extracted transition phrase or empty string
#         """
#         expected_phrase = ARCHETYPE_TRANSITIONS.get(
#             self.archetype, ARCHETYPE_TRANSITIONS["EXECUTIVE"]
#         ).format(company=company_name)

#         if expected_phrase.lower() in body.lower():
#             return expected_phrase

#         return ""

#     def _count_insights(self, body: str) -> int:
#         """Count numbered insights in body.

#         Args:
#             body: Message body

#         Returns:
#             Number of insights
#         """
#         import re

#         # Count patterns like "1." and "2."
#         insights = re.findall(r"\n\d+\.\s+", body)
#         return len(insights)

#     def _count_bullets(self, body: str) -> int:
#         """Count bullets in body.

#         Args:
#             body: Message body

#         Returns:
#             Number of bullets
#         """
#         import re

#         # Count patterns like "•", "-", "*"
#         bullets = re.findall(r"[\n•\-\*]\s+", body)
#         return len(bullets)
