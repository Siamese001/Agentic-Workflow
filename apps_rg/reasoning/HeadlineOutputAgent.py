"""Executive Title Composer - Industry-First Headline Generation (K.4).

This agent generates professional headlines with strict Industry-First positioning,
enforcing 8-13 word total count and ≤90 character limit with technology keyword blocking.

Sub-Atomic Agent Name: Executive_Title_Composer
Legacy K-Node: K.4
"""

import logging
from dataclasses import dataclass
from typing import Any

from apps_rg.utils.RGAgentBase import RGAgentBase as Agent

logger = logging.getLogger(__name__)


@dataclass
class HeadlineOutput:
    """Executive title composer output."""

    headline: str
    segment_1: str
    segment_2: str
    segment_3: str
    word_count: int
    char_count: int
    industry_first_compliant: bool
    technology_keywords_in_segment_1: list[str]
    metadata: dict[str, Any]


TECHNOLOGY_KEYWORDS = [
    "AI",
    "ML",
    "Python",
    "Java",
    "AWS",
    "Azure",
    "GCP",
    "Kubernetes",
    "Docker",
    "React",
    "Angular",
    "Node.js",
    "TensorFlow",
    "PyTorch",
    "SQL",
    "NoSQL",
    "MongoDB",
    "PostgreSQL",
    "Redis",
    "Kafka",
    "Microservices",
    "API",
    "REST",
    "GraphQL",
    "DevOps",
    "CI/CD",
]


class Executive_Title_Composer(Agent):
    """Executive Title Composer agent for Industry-First headline generation.

    This agent generates headlines with strict constraints:
    - Total word count: 8-13 words (ZERO TOLERANCE)
    - Character limit: ≤90 characters (ZERO TOLERANCE)
    - Industry-First positioning: Segment 1 MUST NOT contain technology keywords
    - 3-segment structure: Domain | Leadership | Value Prop

    Validation Gates:
    - VG_HEADLINE_WORD_COUNT_COMPLIANCE (8-13 words)
    - VG_HEADLINE_CHARACTER_COMPLIANCE (≤90 chars)
    - VG_INDUSTRY_FIRST_COMPLIANCE (no tech in Segment 1)
    """

    # guardian: allow-magic-config
    def __init__(self, config: Any, word_count_min: int = 8, word_count_max: int = 13, char_limit: int = 90):
        """Initialize Executive Title Composer.

        Args:
            config: Reasoning configuration
            word_count_min: Minimum word count (default 8)
            word_count_max: Maximum word count (default 13)
            char_limit: Character limit (default 90)
        """
        super().__init__(config, k_node_id="K.4", element="Executive Title (Industry-First)")
        self.word_count_min = word_count_min
        self.word_count_max = word_count_max
        self.char_limit = char_limit
        logger.info(
            f"Executive_Title_Composer initialized: words={word_count_min}-{word_count_max}, chars≤{char_limit}"
        )

    async def execute(self, context: dict[str, Any]) -> HeadlineOutput:
        """Execute headline generation with Industry-First positioning.

        Args:
            context: Execution context with:
                - target_industry: str - Target industry/domain
                - target_role: str - Target role/level
                - value_propositions: List[str] - Key value props
                - job_description: str - Target JD
                - regeneration_feedback: Optional[str]

        Returns:
            HeadlineOutput with 3-segment headline
        """
        logger.info("Executing Executive_Title_Composer (Industry-First)")
        target_industry = context.get("target_industry", "Technology")
        target_role = context.get("target_role", "Engineering Leader")
        value_propositions = context.get("value_propositions", [])
        job_description = context.get("job_description", "")
        regeneration_feedback = context.get("regeneration_feedback")
        if regeneration_feedback:
            prompt = self._build_regeneration_prompt(context, regeneration_feedback)
        else:
            prompt = self._build_initial_prompt(
                target_industry, target_role, value_propositions, job_description
            )
        response = await self._call_llm(prompt)
        headline = response.strip()
        segments = self._parse_segments(headline)
        tech_keywords_in_seg1 = self._check_technology_keywords(segments[0])
        industry_first_compliant = len(tech_keywords_in_seg1) == 0
        word_count = len(headline.split())
        char_count = len(headline)
        output = HeadlineOutput(
            headline=headline,
            segment_1=segments[0],
            segment_2=segments[1],
            segment_3=segments[2],
            word_count=word_count,
            char_count=char_count,
            industry_first_compliant=industry_first_compliant,
            technology_keywords_in_segment_1=tech_keywords_in_seg1,
            metadata={
                "k_node_id": self.k_node_id,
                "temperature": self.config.temperature,
                "word_count_range": f"{self.word_count_min}-{self.word_count_max}",
                "char_limit": self.char_limit,
            },
        )
        logger.info(
            f"Executive_Title_Composer complete: {word_count} words, {char_count} chars, Industry-First={industry_first_compliant}"
        )
        if not industry_first_compliant:
            logger.error(
                f"INDUSTRY-FIRST VIOLATION: Technology keywords in Segment 1: {tech_keywords_in_seg1}"
            )
        return output

    def _build_initial_prompt(
        self, target_industry: str, target_role: str, value_propositions: list[str], job_description: str
    ) -> str:
        """Build initial generation prompt with Industry-First enforcement.

        Args:
            target_industry: Target industry/domain
            target_role: Target role/level
            value_propositions: Key value props
            job_description: Target JD

        Returns:
            Formatted prompt
        """
        prompt = f"""Generate a professional resume headline with STRICT Industry-First positioning.\n\nCRITICAL CONSTRAINTS (ZERO TOLERANCE):\n1. Total word count: {self.word_count_min}-{self.word_count_max} words (STRICT)\n2. Character limit: ≤{self.char_limit} characters (STRICT)\n3. 3-segment structure: Domain | Leadership | Value Proposition\n4. INDUSTRY-FIRST POSITIONING: Segment 1 MUST NOT contain technology keywords\n\nINDUSTRY-FIRST RULE (BLOCKING):\n- Segment 1 must lead with INDUSTRY/DOMAIN\n  (e.g., "Healthcare", "Financial Services", "Enterprise SaaS")\n- Segment 1 MUST NOT contain: AI, ML, Python, AWS, Kubernetes, Docker, etc.\n- Technology keywords belong in Segment 3 (Value Proposition)\n\nTARGET INDUSTRY: {target_industry}\nTARGET ROLE: {target_role}\n\nVALUE PROPOSITIONS (use for Segment 3):\n{chr(10).join(f"- {vp}" for vp in value_propositions[:3])}\n\nJOB DESCRIPTION CONTEXT:\n{job_description[:300]}...\n\nSTRUCTURE:\nSegment 1: {target_industry} [Industry/Domain - NO TECHNOLOGY KEYWORDS]\nSegment 2: {target_role} [Leadership/Role]\nSegment 3: [Value Proposition - technology keywords allowed here]\n\nEXAMPLES (Industry-First Compliant):\n✅ "Healthcare Technology Leader | AI/ML Innovation | Enterprise Scale"\n✅ "Financial Services Executive | Cloud Architecture | Digital Transformation"\n✅ "Enterprise SaaS Leader | Engineering Excellence | Scalable Solutions"\n\nEXAMPLES (Industry-First VIOLATIONS - DO NOT USE):\n❌ "AI/ML Leader | Healthcare Technology | Innovation" (tech in Segment 1)\n❌ "Python Engineer | Cloud Architecture | SaaS" (tech in Segment 1)\n\nGenerate the headline now (\n{self.word_count_min}-{self.word_count_max} words, ≤{self.char_limit} chars):\n"""
        return prompt

    def _build_regeneration_prompt(self, context: dict[str, Any], feedback: str) -> str:
        """Build regeneration prompt with validation feedback.

        Args:
            context: Original context
            feedback: Validation feedback

        Returns:
            Regeneration prompt
        """
        previous_headline = context.get("previous_headline", "")
        prompt = f"REGENERATION REQUIRED\n\n{feedback}\n\nPREVIOUS HEADLINE:\n{previous_headline}\n\nCONSTRAINTS (ZERO TOLERANCE):\n- Word count: {self.word_count_min}-{self.word_count_max} words\n- Character limit: ≤{self.char_limit} characters\n- INDUSTRY-FIRST: NO technology keywords in Segment 1\n\nINSTRUCTIONS:\nFix the specific violations listed in feedback.\nMaintain Industry-First positioning.\n\nGenerate the corrected headline:\n"
        return prompt

    def _parse_segments(self, headline: str) -> list[str]:
        """Parse headline into 3 segments.

        Args:
            headline: Full headline

        Returns:
            List of 3 segments [Domain, Leadership, Value Prop]
        """
        segments = [s.strip() for s in headline.split("|")]
        while len(segments) < 3:
            segments.append("")
        return segments[:3]

    def _check_technology_keywords(self, segment: str) -> list[str]:
        """Check for technology keywords in segment.

        Args:
            segment: Segment text

        Returns:
            List of found technology keywords
        """
        segment_upper = segment.upper()
        found_keywords = []
        for keyword in TECHNOLOGY_KEYWORDS:
            if keyword.upper() in segment_upper:
                found_keywords.append(keyword)
        return found_keywords
