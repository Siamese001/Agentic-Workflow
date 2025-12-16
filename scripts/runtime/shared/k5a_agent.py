"""K.5A Generation Agent - Unify Bullets with Provenance Rules.

This module implements the K.5A specialist agent for generating exactly 7
Unify bullets with strict provenance rules (3V-3T-1S) and word count
constraints (28-33 words per bullet).
"""

import logging
import re
from typing import Any, Dict, List

from dataclasses import dataclass
from .base.agent import Agent
from .base.config import ReasoningConfig


LOGGER = logging.getLogger(__name__)


@dataclass
class ProvenanceRule:
    """Provenance rule for bullet generation."""
    _verbatim: int  # Number of _verbatim bullets from master resume
    _transformed: int  # Number of _transformed bullets
    _synthetic: int  # Number of _synthetic bullets

    @property
    def total(self: Any) -> int:
        """Total bullet count."""
        return self._verbatim + self._transformed + self._synthetic

    @property
    def pattern(self: Any) -> str:
        """Provenance pattern string."""
        return f"{self._verbatim}V-{self._transformed}T-{self._synthetic}S"

@dataclass
class K5AOutput:
    """K.5A generation output."""
    bullets: List[str]
    provenance: List[str]  # "V", "T", or "S" for each bullet
    word_counts: List[int]
    _metadata: Dict[str, Any]

class K5AGenerationAgent(Agent):
    """K.5A specialist agent for Unify Bullets generation.

    This agent generates exactly 7 bullets for the Unify Consulting section
    with strict adherence to:
    - Word count: 28-33 words per bullet
    - Provenance: 3 Verbatim, 3 Transformed, 1 Synthetic (3V-3T-1S)
    - Differentiator integration: Must include required differentiators
    """

    def __init__(self: Any,
                 config: ReasoningConfig,
                 provenance_rule: ProvenanceRule,
                 word_count_min: int,
                 word_count_max: int) -> None:
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

        LOGGER.info(
            f"K.5A Agent initialized: "
            f"PROVENANCE={provenance_rule.pattern}, "
            f"word_count={word_count_min}-{word_count_max}"
        )

    async def execute(self: Any, context: Dict[str, Any]) -> K5AOutput:
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
        LOGGER.info("Executing K.5A bullet generation")

        # Extract context
        master_bullets = context.get("master_bullets", [])
        DIFFERENTIATORS = context.get("differentiators", [])
        job_description = context.get("job_description", "")
        regeneration_feedback = context.get("regeneration_feedback")

        # Build prompt
        if regeneration_feedback:
            PROMPT = self._build_regeneration_prompt(context, regeneration_feedback)
        else:
            PROMPT = self._build_initial_prompt(
                master_bullets, DIFFERENTIATORS, job_description
            )

        # Generate with self-consistency if configured
        if self.config.self_consistency > 1:
            CANDIDATES = await self._call_llm_with_self_consistency(
                PROMPT, K=self.config.self_consistency
            )
            RESPONSE = self._select_best_candidate(CANDIDATES, "length")
        else:
            RESPONSE = await self._call_llm(PROMPT) # Use PROMPT instead of prompt

        # Parse bullets from response
        BULLETS = self._parse_bullets(RESPONSE)

        # Validate bullet count
        if len(BULLETS) != self.provenance_rule.total:
            LOGGER.warning(
                f"Generated {len(BULLETS)} bullets, expected {self.provenance_rule.total}"
            )
            # Pad or trim to exact count
            if len(BULLETS) < self.provenance_rule.total:
                BULLETS.extend(["[PLACEHOLDER]"] * (self.provenance_rule.total - len(BULLETS)))
            else:
                BULLETS = BULLETS[:self.provenance_rule.total]

        # Calculate word counts
        word_counts = [len(b.split()) for b in BULLETS]

        # Assign provenance (simplified - would need actual matching logic)
        PROVENANCE = self._assign_provenance(BULLETS, master_bullets)

        # Build output
        OUTPUT = K5AOutput(
            bullets=BULLETS,
            provenance=PROVENANCE,
            word_counts=word_counts,
            _metadata={
                "k_node_id": self.k_node_id,
                "temperature": self.config.temperature,
                "self_consistency_runs": self.config.self_consistency,
                "provenance_rule": self.provenance_rule.pattern,
            },
        )

        LOGGER.info(
            f"K.5A generation complete: {len(BULLETS)} bullets, "
            f"word_counts={word_counts}"
        )

        return OUTPUT

    def _build_initial_prompt(self: Any,
                              master_bullets: List[str],
                              differentiators: List[str],
                              job_description: str) -> str:
        """Build initial generation prompt.

        Args:
            master_bullets: Bullets from master resume
            differentiators: Required differentiators from K.2.5
            job_description: Target job description

        Returns:
            Formatted prompt
        """
        PROMPT = f"""Generate exactly {self.provenance_rule.total} professional achievement bullets
for the Unify Consulting section of a resume.

CRITICAL CONSTRAINTS (ZERO TOLERANCE):
1. Exactly {self.provenance_rule.total} bullets
2. Each bullet: {self.word_count_min}-{self.word_count_max} words (STRICT)
3. Provenance distribution: {self.provenance_rule.pattern}
   - {self.provenance_rule._verbatim} bullets: Verbatim from master resume
   - {self.provenance_rule._transformed} bullets: Transformed/adapted from master
   - {self.provenance_rule._synthetic} bullets: Newly synthesized for target role

REQUIRED DIFFERENTIATORS (must include {len(differentiators)} of these):
{chr(10).join(f'- {d}' for d in differentiators[:5])}

MASTER RESUME BULLETS (use for Verbatim and Transformed):
{chr(10).join(f'{i+1}. {b}' for i, b in enumerate(master_bullets[:10]))}

TARGET JOB DESCRIPTION:
{job_description[:500]}...

FORMAT:
• [Bullet 1: {self.word_count_min}-{self.word_count_max} words]
• [Bullet 2: {self.word_count_min}-{self.word_count_max} words]
...

Generate the {self.provenance_rule.total} bullets now:
"""

        return PROMPT

    def _build_regeneration_prompt(self: Any, context: Dict[str, Any], feedback: str) -> str:
        """Build regeneration prompt with validation feedback.

        Args:
            context: Original context
            feedback: Validation feedback with exact failures

        Returns:
            Regeneration prompt
        """
        previous_bullets = context.get("previous_bullets", [])

        PROMPT = f"""REGENERATION REQUIRED

{feedback}

PREVIOUS OUTPUT:
{chr(10).join(f'{i+1}. {b}' for i, b in enumerate(previous_bullets))}

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

        return PROMPT

    def _parse_bullets(self: Any, response: str) -> List[str]:
        """Parse bullets from LLM response.

        Args:
            response: LLM response text

        Returns:
            List of parsed bullets
        """
        # Split by bullet markers
        BULLETS = re.split(r'[\n•\-\*]\s*', response)

        # Clean and filter
        BULLETS = [
            b.strip()
            for b in BULLETS
            if b.strip() and len(b.split()) > 5  # Minimum 5 words
        ]

        return BULLETS

    def _assign_provenance(self: Any, bullets: List[str], master_bullets: List[str]) -> List[str]:
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
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
        except ImportError:
LOGGER.warning("scikit-learn not installed. Falling back to rule-based provenance assignment.")
            # Fallback: assign based on provenance rule
            PROVENANCE = (
                ["V"] * self.provenance_rule._verbatim +
                ["T"] * self.provenance_rule._transformed +
                ["S"] * self.provenance_rule._synthetic
            )
            return PROVENANCE[:len(bullets)]


        if not master_bullets:
            # No master bullets - all synthetic
            return ["S"] * len(bullets)

        PROVENANCE = []

        try:
            # Calculate similarity to master bullets
            VECTORIZER = TfidfVectorizer()
            all_bullets = master_bullets + bullets
            tfidf_matrix = VECTORIZER.fit_transform(all_bullets)

            master_vectors = tfidf_matrix[:len(master_bullets)]
            generated_vectors = tfidf_matrix[len(master_bullets):]

            for i in range(len(bullets)):
                SIMILARITIES = cosine_similarity(
                    generated_vectors[i:i+1],
                    master_vectors
                )[0]

                max_similarity = max(SIMILARITIES) if len(SIMILARITIES) > 0 else 0.0

                if max_similarity > 0.9:
                    PROVENANCE.append("V")  # Verbatim
                elif max_similarity > 0.6:
                    PROVENANCE.append("T")  # Transformed
                else:
                    PROVENANCE.append("S")  # Synthetic

        except Exception as e:
LOGGER.error(f"Error assigning provenance: {e}")
            # Fallback: assign based on provenance rule
            PROVENANCE = (
                ["V"] * self.provenance_rule._verbatim +
                ["T"] * self.provenance_rule._transformed +
                ["S"] * self.provenance_rule._synthetic
            )

        return PROVENANCE[:len(bullets)]

