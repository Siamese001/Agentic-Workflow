"""Executive Title Composer - Industry-First Headline Generation (K.4).

This agent generates professional headlines with strict Industry-First positioning,
enforcing 8-13 word total count and ≤90 character limit with technology keyword blocking.

Sub-Atomic Agent Name: Executive_Title_Composer
Legacy K-Node: K.4
"""

import logging
from dataclasses import dataclass
from typing import Any

from apps_rg.shared.core.RGAgentBase import RGAgentBase as Agent

logger = logging.getLogger(__name__)


@dataclass
class HeadlineOutput:
    """Executive title composer output."""

    headline: str
    segment_1: str  # Industry/Domain
    segment_2: str  # Leadership/Role
    segment_3: str  # Value Proposition
    word_count: int
    char_count: int
    industry_first_compliant: bool
    technology_keywords_in_segment_1: list[str]
    metadata: dict[str, Any]


# Technology keywords that MUST NOT appear in Segment 1 (Industry-First violation)
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

    def __init__(
        self,
        config: Any,
        word_count_min: int = 8,
        word_count_max: int = 13,
        char_limit: int = 90,
    ):
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
            f"Executive_Title_Composer initialized: "
            f"words={word_count_min}-{word_count_max}, chars≤{char_limit}"
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

        # Extract context
        target_industry = context.get("target_industry", "Technology")
        target_role = context.get("target_role", "Engineering Leader")
        value_propositions = context.get("value_propositions", [])
        job_description = context.get("job_description", "")
        regeneration_feedback = context.get("regeneration_feedback")

        # Build prompt
        if regeneration_feedback:
            prompt = self._build_regeneration_prompt(context, regeneration_feedback)
        else:
            prompt = self._build_initial_prompt(
                target_industry, target_role, value_propositions, job_description
            )

        # Generate headline
        response = await self._call_llm(prompt)
        headline = response.strip()

        # Parse segments
        segments = self._parse_segments(headline)

        # Validate Industry-First compliance
        tech_keywords_in_seg1 = self._check_technology_keywords(segments[0])
        industry_first_compliant = len(tech_keywords_in_seg1) == 0

        # Calculate metrics
        word_count = len(headline.split())
        char_count = len(headline)

        # Build output
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
            f"Executive_Title_Composer complete: {word_count} words, {char_count} chars, "
            f"Industry-First={industry_first_compliant}"
        )

        if not industry_first_compliant:
            logger.error(
                f"INDUSTRY-FIRST VIOLATION: Technology keywords in Segment 1: {tech_keywords_in_seg1}"
            )

        return output

    def _build_initial_prompt(
        self,
        target_industry: str,
        target_role: str,
        value_propositions: list[str],
        job_description: str,
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
        prompt = f"""Generate a professional resume headline with STRICT Industry-First positioning.

CRITICAL CONSTRAINTS (ZERO TOLERANCE):
1. Total word count: {self.word_count_min}-{self.word_count_max} words (STRICT)
2. Character limit: ≤{self.char_limit} characters (STRICT)
3. 3-segment structure: Domain | Leadership | Value Proposition
4. INDUSTRY-FIRST POSITIONING: Segment 1 MUST NOT contain technology keywords

INDUSTRY-FIRST RULE (BLOCKING):
- Segment 1 must lead with INDUSTRY/DOMAIN
  (e.g., "Healthcare", "Financial Services", "Enterprise SaaS")
- Segment 1 MUST NOT contain: AI, ML, Python, AWS, Kubernetes, Docker, etc.
- Technology keywords belong in Segment 3 (Value Proposition)

TARGET INDUSTRY: {target_industry}
TARGET ROLE: {target_role}

VALUE PROPOSITIONS (use for Segment 3):
{chr(10).join(f"- {vp}" for vp in value_propositions[:3])}

JOB DESCRIPTION CONTEXT:
{job_description[:300]}...

STRUCTURE:
Segment 1: {target_industry} [Industry/Domain - NO TECHNOLOGY KEYWORDS]
Segment 2: {target_role} [Leadership/Role]
Segment 3: [Value Proposition - technology keywords allowed here]

EXAMPLES (Industry-First Compliant):
✅ "Healthcare Technology Leader | AI/ML Innovation | Enterprise Scale"
✅ "Financial Services Executive | Cloud Architecture | Digital Transformation"
✅ "Enterprise SaaS Leader | Engineering Excellence | Scalable Solutions"

EXAMPLES (Industry-First VIOLATIONS - DO NOT USE):
❌ "AI/ML Leader | Healthcare Technology | Innovation" (tech in Segment 1)
❌ "Python Engineer | Cloud Architecture | SaaS" (tech in Segment 1)

Generate the headline now (
{self.word_count_min}-{self.word_count_max} words, ≤{self.char_limit} chars):
"""

        return prompt

    def _build_regeneration_prompt(
        self,
        context: dict[str, Any],
        feedback: str,
    ) -> str:
        """Build regeneration prompt with validation feedback.

        Args:
            context: Original context
            feedback: Validation feedback

        Returns:
            Regeneration prompt
        """
        previous_headline = context.get("previous_headline", "")

        prompt = f"""REGENERATION REQUIRED

{feedback}

PREVIOUS HEADLINE:
{previous_headline}

CONSTRAINTS (ZERO TOLERANCE):
- Word count: {self.word_count_min}-{self.word_count_max} words
- Character limit: ≤{self.char_limit} characters
- INDUSTRY-FIRST: NO technology keywords in Segment 1

INSTRUCTIONS:
Fix the specific violations listed in feedback.
Maintain Industry-First positioning.

Generate the corrected headline:
"""

        return prompt

    def _parse_segments(self, headline: str) -> list[str]:
        """Parse headline into 3 segments.

        Args:
            headline: Full headline

        Returns:
            List of 3 segments [Domain, Leadership, Value Prop]
        """
        # Split by pipe delimiter
        segments = [s.strip() for s in headline.split("|")]

        # Ensure exactly 3 segments
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
