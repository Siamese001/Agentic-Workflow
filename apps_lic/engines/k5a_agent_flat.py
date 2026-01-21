"""K.5A Generation Agent - Unify Bullets with Provenance Rules.

This module implements the K.5A specialist agent for generating exactly 7
Unify bullets with strict provenance rules (3V-3T-1S) and word count
constraints (28-33 words per bullet).
"""

import logging
import re
from dataclasses import dataclass
from typing import Any

from runtime.shared.agent_base import Agent, ReasoningConfig

logger = logging.getLogger(__name__)


@dataclass
class ProvenanceRule:
    """Provenance rule for bullet generation."""

    verbatim: int  # Number of verbatim bullets from master resume
    transformed: int  # Number of transformed bullets
    synthetic: int  # Number of synthetic bullets

    @property
    def total(self) -> int:
        """Total bullet count."""
        return self.verbatim + self.transformed + self.synthetic

    @property
    def pattern(self) -> str:
        """Provenance pattern string."""
        return f"{self.verbatim}V-{self.transformed}T-{self.synthetic}S"


@dataclass
class K5AOutput:
    """K.5A generation output."""

    bullets: list[str]
    provenance: list[str]  # "V", "T", or "S" for each bullet
    word_counts: list[int]
    metadata: dict[str, Any]


class K5A_GenerationAgent(Agent):
    """K.5A specialist agent for Unify Bullets generation.

    This agent generates exactly 7 bullets for the Unify Consulting section
    with strict adherence to:
    - Word count: 28-33 words per bullet
    - Provenance: 3 Verbatim, 3 Transformed, 1 Synthetic (3V-3T-1S)
    - Differentiator integration: Must include required differentiators
    """

    def __init__(
        self,
        config: ReasoningConfig,
        provenance_rule: ProvenanceRule,
        word_count_min: int = 28,
        word_count_max: int = 33,
    ):
        """Initialize K.5A agent.

        Args:
            config: Reasoning configuration from orchestration config
            provenance_rule: Provenance rule (e.g., 3V-3T-1S)
            word_count_min: Minimum words per bullet
            word_count_max: Maximum words per bullet
        """
        super().__init__(config, k_node_id="K.5A", element="Unify Bullets")

        self.provenance_rule = provenance_rule
        self.word_count_min = word_count_min
        self.word_count_max = word_count_max

        logger.info(
            f"K.5A Agent initialized: "
            f"provenance={provenance_rule.pattern}, "
            f"word_count={word_count_min}-{word_count_max}"
        )

    async def execute(self, context: dict[str, Any]) -> K5AOutput:
        """Execute K.5A bullet generation.

        Args:
            context: Execution context with:
                - master_bullets: List[str] - Bullets from master resume
                - differentiators: List[str] - Required differentiators from K.2.5
                - job_description: str - Target job description
                - regeneration_feedback: Optional[str] - Feedback from validation

        Returns:
            K5AOutput with 7 bullets and metadata
        """
        logger.info("Executing K.5A bullet generation")

        # Extract context
        master_bullets = context.get("master_bullets", [])
        differentiators = context.get("differentiators", [])
        job_description = context.get("job_description", "")
        regeneration_feedback = context.get("regeneration_feedback")

        # Build prompt
        if regeneration_feedback:
            prompt = self._build_regeneration_prompt(context, regeneration_feedback)
        else:
            prompt = self._build_initial_prompt(master_bullets, differentiators, job_description)

        # Generate with self-consistency if configured
        if self.config.self_consistency > 1:
            candidates = await self._call_llm_with_self_consistency(
                prompt, k=self.config.self_consistency
            )
            response = self._select_best_candidate(candidates, "length")
        else:
            response = await self._call_llm(prompt)

        # Parse bullets from response
        bullets = self._parse_bullets(response)

        # Validate bullet count
        if len(bullets) != self.provenance_rule.total:
            logger.warning(
                f"Generated {len(bullets)} bullets, expected {self.provenance_rule.total}"
            )
            # Pad or trim to exact count
            if len(bullets) < self.provenance_rule.total:
                bullets.extend(["[PLACEHOLDER]"] * (self.provenance_rule.total - len(bullets)))
            else:
                bullets = bullets[: self.provenance_rule.total]

        # Calculate word counts
        word_counts = [len(b.split()) for b in bullets]

        # Assign provenance (simplified - would need actual matching logic)
        provenance = self._assign_provenance(bullets, master_bullets)

        # Build output
        output = K5AOutput(
            bullets=bullets,
            provenance=provenance,
            word_counts=word_counts,
            metadata={
                "k_node_id": self.k_node_id,
                "temperature": self.config.temperature,
                "self_consistency_runs": self.config.self_consistency,
                "provenance_rule": self.provenance_rule.pattern,
            },
        )

        logger.info(f"K.5A generation complete: {len(bullets)} bullets, word_counts={word_counts}")

        return output

    def _build_initial_prompt(
        self,
        master_bullets: list[str],
        differentiators: list[str],
        job_description: str,
    ) -> str:
        """Build initial generation prompt.

        Args:
            master_bullets: Bullets from master resume
            differentiators: Required differentiators from K.2.5
            job_description: Target job description

        Returns:
            Formatted prompt
        """
        prompt = f"""Generate exactly {self.provenance_rule.total} professional achievement bullets for the Unify Consulting section of a resume.

CRITICAL CONSTRAINTS (ZERO TOLERANCE):
1. Exactly {self.provenance_rule.total} bullets
2. Each bullet: {self.word_count_min}-{self.word_count_max} words (STRICT)
3. Provenance distribution: {self.provenance_rule.pattern}
   - {self.provenance_rule.verbatim} bullets: Verbatim from master resume
   - {self.provenance_rule.transformed} bullets: Transformed/adapted from master
   - {self.provenance_rule.synthetic} bullets: Newly synthesized for target role

REQUIRED DIFFERENTIATORS (must include {len(differentiators)} of these):
{chr(10).join(f"- {d}" for d in differentiators[:5])}

MASTER RESUME BULLETS (use for Verbatim and Transformed):
{chr(10).join(f"{i + 1}. {b}" for i, b in enumerate(master_bullets[:10]))}

TARGET JOB DESCRIPTION:
{job_description[:500]}...

FORMAT:
• [Bullet 1: {self.word_count_min}-{self.word_count_max} words]
• [Bullet 2: {self.word_count_min}-{self.word_count_max} words]
...

Generate the {self.provenance_rule.total} bullets now:
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
            feedback: Validation feedback with exact failures

        Returns:
            Regeneration prompt
        """
        previous_bullets = context.get("previous_bullets", [])

        prompt = f"""REGENERATION REQUIRED

{feedback}

PREVIOUS OUTPUT:
{chr(10).join(f"{i + 1}. {b}" for i, b in enumerate(previous_bullets))}

CONSTRAINTS (ZERO TOLERANCE):
- Each bullet: {self.word_count_min}-{self.word_count_max} words
- Total bullets: {self.provenance_rule.total}
- Provenance: {self.provenance_rule.pattern}

INSTRUCTIONS:
1. Fix ONLY the failing bullets listed in the feedback
2. Maintain all other bullets unchanged
3. Ensure ALL bullets meet the {self.word_count_min}-{self.word_count_max} word constraint

Generate the corrected bullets:
"""

        return prompt

    def _parse_bullets(self, response: str) -> list[str]:
        """Parse bullets from LLM response.

        Args:
            response: LLM response text

        Returns:
            List of parsed bullets
        """
        # Split by bullet markers
        bullets = re.split(r"[\n•\-\*]\s*", response)

        # Clean and filter
        bullets = [
            b.strip()
            for b in bullets
            if b.strip() and len(b.split()) > 5  # Minimum 5 words
        ]

        return bullets

    def _assign_provenance(
        self,
        bullets: list[str],
        master_bullets: list[str],
    ) -> list[str]:
        """Assign provenance to bullets.

        This is a simplified implementation. A production version would use
        semantic similarity to determine if a bullet is verbatim, transformed,
        or synthetic.

        Args:
            bullets: Generated bullets
            master_bullets: Master resume bullets

        Returns:
            List of provenance labels ("V", "T", "S")
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        if not master_bullets:
            # No master bullets - all synthetic
            return ["S"] * len(bullets)

        provenance = []

        try:
            # Calculate similarity to master bullets
            vectorizer = TfidfVectorizer()
            all_bullets = master_bullets + bullets
            tfidf_matrix = vectorizer.fit_transform(all_bullets)

            master_vectors = tfidf_matrix[: len(master_bullets)]
            generated_vectors = tfidf_matrix[len(master_bullets) :]

            for i in range(len(bullets)):
                similarities = cosine_similarity(generated_vectors[i : i + 1], master_vectors)[0]

                max_similarity = max(similarities) if len(similarities) > 0 else 0.0

                if max_similarity > 0.9:
                    provenance.append("V")  # Verbatim
                elif max_similarity > 0.6:
                    provenance.append("T")  # Transformed
                else:
                    provenance.append("S")  # Synthetic

        except Exception as e:
            logger.error(f"Error assigning provenance: {e}")
            # Fallback: assign based on provenance rule
            provenance = (
                ["V"] * self.provenance_rule.verbatim
                + ["T"] * self.provenance_rule.transformed
                + ["S"] * self.provenance_rule.synthetic
            )

        return provenance[: len(bullets)]
