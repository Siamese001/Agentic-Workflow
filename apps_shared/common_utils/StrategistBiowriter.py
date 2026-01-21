"""Strategist BioWriter - Executive Summary Generation (K.1).

This agent generates executive summaries with strict 3rd-person implied voice,
enforcing 120-140 word count and 3-5 sentence structure with 1st-person blocking.

Sub-Atomic Agent Name: Strategist_BioWriter
Legacy K-Node: K.1
"""

import logging
import re
from dataclasses import dataclass
from typing import Any

from runtime.shared.agent_base import Agent, ReasoningConfig

logger = logging.getLogger(__name__)


@dataclass
class ExecutiveSummaryOutput:
    """Strategist BioWriter output."""
    summary: str
    word_count: int
    sentence_count: int
    first_person_violations: list[str]
    third_person_compliant: bool
    metadata: dict[str, Any]


# First-person patterns that MUST be blocked
FIRST_PERSON_PATTERNS = [
    r'\bI\b', r'\bI\'m\b', r'\bI\'ve\b', r'\bI\'ll\b', r'\bI\'d\b',
    r'\bmy\b', r'\bmine\b', r'\bme\b', r'\bmyself\b',
    r'\bwe\b', r'\bwe\'re\b', r'\bwe\'ve\b', r'\bour\b', r'\bours\b',
]


class Strategist_BioWriter(Agent):
    """Strategist BioWriter agent for executive summary generation.

    This agent generates executive summaries with strict constraints:
    - Word count: 120-140 words (ZERO TOLERANCE)
    - Sentence count: 3-5 sentences (ZERO TOLERANCE)
    - Voice: 3rd-person implied (BLOCK on any 1st-person)
    - Structure: Career arc, expertise, value proposition

    Validation Gates:
    - VG_SUMMARY_WORD_COUNT_COMPLIANCE (120-140 words)
    - VG_SUMMARY_VOICE_TENSE (3rd-person only)
    - VG_SUMMARY_GROUNDING_CHECK (no hallucinations)
    """

    def __init__(
        self,
        config: ReasoningConfig,
        word_count_min: int = 120,
        word_count_max: int = 140,
        sentence_count_min: int = 3,
        sentence_count_max: int = 5,
    ):
        """Initialize Strategist BioWriter.

        Args:
            config: Reasoning configuration
            word_count_min: Minimum word count (default 120)
            word_count_max: Maximum word count (default 140)
            sentence_count_min: Minimum sentence count (default 3)
            sentence_count_max: Maximum sentence count (default 5)
        """
        super().__init__(
            config,
            k_node_id="K.1",
            element="Executive Summary (3rd-Person)"
        )

        self.word_count_min = word_count_min
        self.word_count_max = word_count_max
        self.sentence_count_min = sentence_count_min
        self.sentence_count_max = sentence_count_max

        logger.info(
            f"Strategist_BioWriter initialized: "
            f"words={word_count_min}-{word_count_max}, "
            f"sentences={sentence_count_min}-{sentence_count_max}"
        )

    async def execute(self, context: dict[str, Any]) -> ExecutiveSummaryOutput:
        """Execute executive summary generation with 3rd-person voice.

        Args:
            context: Execution context with:
                - career_highlights: List[str] - Key career achievements
                - expertise_areas: List[str] - Core expertise
                - value_propositions: List[str] - Value props
                - target_role: str - Target role
                - regeneration_feedback: Optional[str]

        Returns:
            ExecutiveSummaryOutput with 3rd-person summary
        """
        logger.info("Executing Strategist_BioWriter (3rd-Person Implied Voice)")

        # Extract context
        career_highlights = context.get("career_highlights", [])
        expertise_areas = context.get("expertise_areas", [])
        value_propositions = context.get("value_propositions", [])
        target_role = context.get("target_role", "Engineering Leader")
        regeneration_feedback = context.get("regeneration_feedback")

        # Build prompt
        if regeneration_feedback:
            prompt = self._build_regeneration_prompt(context, regeneration_feedback)
        else:
            prompt = self._build_initial_prompt(
                career_highlights, expertise_areas, value_propositions, target_role
            )

        # Generate summary
        response = await self._call_llm(prompt)
        summary = response.strip()

        # Validate 3rd-person voice
        first_person_violations = self._check_first_person(summary)
        third_person_compliant = len(first_person_violations) == 0

        # Calculate metrics
        word_count = len(summary.split())
        sentence_count = self._count_sentences(summary)

        # Build output
        output = ExecutiveSummaryOutput(
            summary=summary,
            word_count=word_count,
            sentence_count=sentence_count,
            first_person_violations=first_person_violations,
            third_person_compliant=third_person_compliant,
            metadata={
                "k_node_id": self.k_node_id,
                "temperature": self.config.temperature,
                "word_count_range": f"{self.word_count_min}-{self.word_count_max}",
                "sentence_count_range": f"{self.sentence_count_min}-{self.sentence_count_max}",
            },
        )

        logger.info(
            f"Strategist_BioWriter complete: {word_count} words, {sentence_count} sentences, "
            f"3rd-person={third_person_compliant}"
        )

        if not third_person_compliant:
            logger.error(
                f"1ST-PERSON VOICE VIOLATION: Found {len(first_person_violations)} violations"
            )

        return output

    def _build_initial_prompt(
        self,
        career_highlights: list[str],
        expertise_areas: list[str],
        value_propositions: list[str],
        target_role: str,
    ) -> str:
        """Build initial generation prompt with 3rd-person enforcement.

        Args:
            career_highlights: Key career achievements
            expertise_areas: Core expertise
            value_propositions: Value props
            target_role: Target role

        Returns:
            Formatted prompt
        """
        prompt = f"""Generate a professional executive summary with STRICT 3rd-person implied voice.

CRITICAL CONSTRAINTS (ZERO TOLERANCE):
1. Word count: {self.word_count_min}-{self.word_count_max} words (STRICT)
2. Sentence count: {self.sentence_count_min}-{self.sentence_count_max} sentences (STRICT)
3. Voice: 3rd-person implied (BLOCK on ANY 1st-person: I, my, we, our, etc.)
4. Structure: Career arc → Expertise → Value proposition

3RD-PERSON VOICE RULE (BLOCKING):
- FORBIDDEN: "I", "I'm", "I've", "my", "me", "we", "our"
- REQUIRED: 3rd-person implied (e.g., "Seasoned leader...", "Proven track record...")
- Write as if describing someone else, but without using "he/she"

TARGET ROLE: {target_role}

CAREER HIGHLIGHTS:
{chr(10).join(f'- {h}' for h in career_highlights[:5])}

EXPERTISE AREAS:
{chr(10).join(f'- {e}' for e in expertise_areas[:5])}

VALUE PROPOSITIONS:
{chr(10).join(f'- {v}' for v in value_propositions[:3])}

STRUCTURE:
Sentence 1-2: Career arc and leadership scope
Sentence 3: Core expertise and technical depth
Sentence 4-5: Value proposition and impact

EXAMPLES (3rd-Person Compliant):
✅ "Seasoned engineering leader with 10+ years building scalable ML platforms. Proven track record architecting cloud-native systems serving millions of users. Deep expertise in AI/ML, distributed systems, and team leadership. Drives innovation through technical excellence and strategic vision. Passionate about building high-performing teams that deliver measurable business impact."

EXAMPLES (1st-Person VIOLATIONS - DO NOT USE):
❌ "I am a seasoned engineering leader..." (1st-person)
❌ "My expertise includes..." (1st-person)
❌ "We built scalable systems..." (1st-person)

Generate the executive summary now ({self.word_count_min}-{self.word_count_max} words, {self.sentence_count_min}-{self.sentence_count_max} sentences, 3rd-person ONLY):
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
        previous_summary = context.get("previous_summary", "")

        prompt = f"""REGENERATION REQUIRED

{feedback}

PREVIOUS SUMMARY:
{previous_summary}

CONSTRAINTS (ZERO TOLERANCE):
- Word count: {self.word_count_min}-{self.word_count_max} words
- Sentence count: {self.sentence_count_min}-{self.sentence_count_max} sentences
- Voice: 3rd-person implied (NO "I", "my", "we", "our")

INSTRUCTIONS:
Fix the specific violations listed in feedback.
Maintain 3rd-person implied voice throughout.

Generate the corrected executive summary:
"""

        return prompt

    def _check_first_person(self, text: str) -> list[str]:
        """Check for first-person voice violations.

        Args:
            text: Text to check

        Returns:
            List of found first-person patterns
        """
        violations = []

        for pattern in FIRST_PERSON_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                violations.extend(matches)

        return violations

    def _count_sentences(self, text: str) -> int:
        """Count sentences in text.

        Args:
            text: Text to count

        Returns:
            Number of sentences
        """
        # Split by sentence terminators
        sentences = re.split(r'[.!?]+', text)
        # Filter empty strings
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(sentences)
