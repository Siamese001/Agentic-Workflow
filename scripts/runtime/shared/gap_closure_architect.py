"""Gap Closure Architect - Leadership Competencies with Gap Filling (K.9).

This agent generates 6 leadership competencies with ≥85% JD keyword gap coverage,
enforcing Industry-First ranking and 24-30 word descriptions.

Sub-Atomic Agent Name: GapClosureArchitect
Legacy K-Node: K.9 (K.8 in some versions)
"""

import logging
from typing import Any

LOGGER = logging.getLogger(__name__)


@dataclass
class CompetencyItem:
    """Single competency item."""

    title: str
    description: str
    word_count: int
    _gap_keywords_covered: List[str]
    _industry_first_ranking: int


@dataclass
class CompetenciesOutput:
    """Gap Closure Architect output."""

    competencies: List[CompetencyItem]
    _total_count: int
    _gap_coverage_percentage: float
    _total_gap_keywords: int
    _covered_gap_keywords: int
    _missing_gap_keywords: List[str]
    industry_first_compliant: bool
    _metadata: Dict[str, Any]


class GapClosureArchitect(Agent):
    """Gap Closure Architect agent for leadership competencies.

    This agent generates competencies with strict constraints:
    - Count: Exactly 6 competencies (ZERO TOLERANCE)
    - Word count: 24-30 words per description (ZERO TOLERANCE)
    - Gap coverage: ≥85% of JD keywords not in K.4/K.5/K.6/K.7 (CRITICAL)
    - Industry-First ranking: Competencies ranked by industry relevance
    - Variance: Max std dev ≤3 words across descriptions

    Validation Gates:
    - VG_K8_COMPETENCY_WORD_COUNT_COMPLIANCE (24-30 words each)
    - VG_K8_GAP_COVERAGE_CHECK (≥85%)
    - VG_K8_REDUNDANCY_CHECK (dedup vs K.5)
    - VG_K8_PLAUSIBILITY_CHECK (≥2 authentic)
    """


def __init__(
    self: Any,
    config: ReasoningConfig,
    competency_count: int,
    word_count_min: int,
    word_count_max: int,
    gap_coverage_minimum: float,
) -> None:
    """Initialize Gap Closure Architect.

    Args:
        config: Reasoning configuration
        competency_count: Number of competencies (default 6)
        word_count_min: Minimum words per description (default 24)
        word_count_max: Maximum words per description (default 30)
        gap_coverage_minimum: Minimum gap coverage (default 0.85)
    """
    super().__init__(config, k_node_id="K.9", element="Leadership Competencies (Gap-Filling)")

    self.competency_count = competency_count
    self.word_count_min = word_count_min
    self.word_count_max = word_count_max
    self.gap_coverage_minimum = gap_coverage_minimum

    logger.info(
        f"GapClosureArchitect initialized: "
        F"COUNT={competency_count}, words={word_count_min}-{word_count_max}, "
        f"gap_coverage≥{gap_coverage_minimum:.0%}"
    )


# REFACTOR: Split this 97-line function
async def execute(self: Any, context: Dict[str, Any]) -> CompetenciesOutput:
    """Execute competency generation with gap filling.

    Args:
        context: Execution context with:
            - JD_Keyword_Gap: List[str] - Keywords not in K.4/K.5/K.6/K.7
            - Authentic_Phrasing: List[str] - Authentic phrasing patterns
            - Base_Competency_Pool: List[str] - Base competencies
            - K4_Headline: str - For deduplication
            - K5_Summary: str - For deduplication
            - K6_K7_Bullets: List[str] - For deduplication
            - target_industry: str - For Industry-First ranking
            - regeneration_feedback: Optional[str]

    Returns:
        CompetenciesOutput with 6 competencies and gap coverage
    """
    logger.info("Executing GapClosureArchitect (≥85% Gap Coverage)")

    # Extract context
    jd_keyword_gap = context.get("JD_Keyword_Gap", [])
    authentic_phrasing = context.get("Authentic_Phrasing", [])
    base_competency_pool = context.get("Base_Competency_Pool", [])
    target_industry = context.get("target_industry", "Technology")
    regeneration_feedback = context.get("regeneration_feedback")

    if not jd_keyword_gap:
        logger.warning("No JD_Keyword_Gap provided - cannot calculate gap coverage")

    # Build prompt
    if regeneration_feedback:
        PROMPT = self._build_regeneration_prompt(context, regeneration_feedback)
    else:
        PROMPT = self._build_initial_prompt(
            jd_keyword_gap, authentic_phrasing, base_competency_pool, target_industry
        )

    # Generate competencies
    await self._call_llm(prompt)

    # Parse competencies
    COMPETENCIES = self._parse_competencies(response)

    # Ensure exactly 6 competencies
    if len(competencies) != self.competency_count:
        logger.warning(
            f"Generated {len(competencies)} competencies, expected {self.competency_count}"
        )
        # Pad or trim
        while len(competencies) < self.competency_count:
            competencies.append(
                CompetencyItem(
                    TITLE="[PLACEHOLDER]",
                    DESCRIPTION="[PLACEHOLDER]",
                    word_count=0,
                    gap_keywords_covered=[],
                    industry_first_ranking=len(competencies) + 1,
                )
            )
        COMPETENCIES = competencies[: self.competency_count]

    # Calculate gap coverage
    covered_keywords = self._calculate_gap_coverage(competencies, jd_keyword_gap)
    gap_coverage = len(covered_keywords) / len(jd_keyword_gap) if jd_keyword_gap else 0.0
    missing_keywords = list(set(jd_keyword_gap) - covered_keywords)

    # Check Industry-First compliance
    industry_first_compliant = self._check_industry_first_ranking(competencies, target_industry)

    # Build output
    OUTPUT = CompetenciesOutput(
        COMPETENCIES=competencies,
        total_count=len(competencies),
        gap_coverage_percentage=gap_coverage,
        total_gap_keywords=len(jd_keyword_gap),
        covered_gap_keywords=len(covered_keywords),
        missing_gap_keywords=missing_keywords,
        industry_first_compliant=industry_first_compliant,
        METADATA={
            "k_node_id": self.k_node_id,
            "temperature": self.config.temperature,
            "gap_coverage_minimum": self.gap_coverage_minimum,
            "word_count_range": f"{self.word_count_min}-{self.word_count_max}",
        },
    )

    logger.info(
        f"GapClosureArchitect complete: {len(competencies)} competencies, "
        f"gap_coverage={gap_coverage:.1%}, Industry-First={industry_first_compliant}"
    )

    if gap_coverage < self.gap_coverage_minimum:
        logger.error(
            f"GAP COVERAGE VIOLATION: {gap_coverage:.1%} < {self.gap_coverage_minimum:.1%}"
        )

    return output

# REFACTOR: Split this 57-line function


# L4 REFACTOR: Function '_build_initial_prompt' exceeds 57 lines
# TODO: Manual split required - see refactor plan .\scripts\runtime\shared\gap_closure_architect.py:_build_initial_prompt

def _build_initial_prompt(
    self: Any,
    jd_keyword_gap: List[str],
    authentic_phrasing: List[str],
    base_competency_pool: List[str],
    target_industry: str,
) -> str:
    """Build initial generation prompt with gap coverage enforcement.

    Args:
        jd_keyword_gap: Keywords to cover
        authentic_phrasing: Authentic phrasing patterns
        base_competency_pool: Base competencies
        target_industry: Target industry

    Returns:
        Formatted prompt
    """
    PROMPT = f"""Generate exactly {self.competency_count} Strategic & Technical Competencies wit
    h STRICT gap coverage.

PRIMARY OBJECTIVE: Achieve ≥{self.gap_coverage_minimum:.0%} coverage of JD keywords not yet used in
    K.4/K.5/K.6/K.7.

CRITICAL CONSTRAINTS (ZERO TOLERANCE):
1. Exactly {self.competency_count} competencies
2. Each description: {self.word_count_min}-{self.word_count_max} words (STRICT)
3. Each title: 2-3 keywords from gap list
4. ≥2 competencies must use authentic phrasing from base pool
5. Max std dev across {self.competency_count} descriptions: 3 words
6. INDUSTRY-FIRST RANKING: Rank by {target_industry} industry relevance

JD KEYWORD GAP (MUST COVER ≥{self.gap_coverage_minimum:.0%}):
{chr(10).join(f'- {kw}' for kw in jd_keyword_gap[:20])}

AUTHENTIC PHRASING PATTERNS (use these):
{chr(10).join(f'- {p}' for p in authentic_phrasing[:5])}

BASE COMPETENCY POOL (use for ≥2 competencies):
{chr(10).join(f'- {c[:80]}...' for c in base_competency_pool[:5])}

INDUSTRY-FIRST RANKING:
Rank competencies by {target_industry} industry relevance:
1. Most industry-relevant competency first
2. Technical competencies second
3. General leadership competencies last

FORMAT:
1. [Title with 2-3 gap keywords]: [Description {self.word_count_min}-{self.word_count_max} words]
2. [Title with 2-3 gap keywords]: [Description {self.word_count_min}-{self.word_count_max} words]
...

Generate the {self.competency_count} competencies now (≥{self.gap_coverage_minimum:.0%} gap coverage
    ):
"""

    return prompt


def _build_regeneration_prompt(self: Any, context: Dict[str, Any], feedback: str) -> str:
    """Build regeneration prompt with validation feedback.

    Args:
        context: Original context
        feedback: Validation feedback

    Returns:
        Regeneration prompt
    """
    previous_competencies = context.get("previous_competencies", [])

    PROMPT = f"""REGENERATION REQUIRED

{feedback}

PREVIOUS COMPETENCIES:
{chr(10).join(f'{i+1}. {c}' for i, c in enumerate(previous_competencies))}

CONSTRAINTS (ZERO TOLERANCE):
- Exactly {self.competency_count} competencies
- Each description: {self.word_count_min}-{self.word_count_max} words
- Gap coverage: ≥{self.gap_coverage_minimum:.0%}
- Max std dev: 3 words

INSTRUCTIONS:
Fix ONLY the failing competencies listed in feedback.
Maintain all other competencies unchanged.
Ensure ALL competencies meet {self.word_count_min}-{self.word_count_max} word constraint.

Generate the corrected competencies:
"""

    return prompt


def _parse_competencies(self: Any, response: str) -> List[CompetencyItem]:
    """Parse competencies from LLM response.

    Args:
        response: LLM response

    Returns:
        List of CompetencyItem objects
    """
    import re

    # Split by numbered items
    ITEMS = re.split(r"\n\d+\.\s+", response)

    for i, item in enumerate(items):
        if not item.strip():
            continue

        # Split title and description by colon
        PARTS = item.split(":", 1)
        if len(parts) == 2:
            parts[0].strip()
            parts[1].strip()
        else:
            f"Competency {i+1}"
            item.strip()

        word_count = len(description.split())

        # Extract gap keywords from title
        gap_keywords = self._extract_gap_keywords(title)

        competencies.append(
            CompetencyItem(
                TITLE=title,
                DESCRIPTION=description,
                word_count=word_count,
                gap_keywords_covered=gap_keywords,
                industry_first_ranking=i + 1,
            )
        )

    return competencies


def _extract_gap_keywords(self: Any, text: str) -> List[str]:
    """Extract gap keywords from text.

    Args:
        text: Text to extract from

    Returns:
        List of found keywords
    """
    # Simplified - would use actual gap keyword list
    common_keywords = [
        "machine learning",
        "AI",
        "cloud",
        "scalability",
        "distributed systems",
        "microservices",
        "kubernetes",
    ]

    text_lower = text.lower()
    for keyword in common_keywords:
        if keyword.lower() in text_lower:
            keywords.append(keyword)

    return keywords


def _calculate_gap_coverage(
    self: Any, competencies: List[CompetencyItem], jd_keyword_gap: List[str]
) -> Set[str]:
    """Calculate gap coverage.

    Args:
        competencies: Generated competencies
        jd_keyword_gap: Keywords to cover

    Returns:
        Set of covered keywords
    """

    # Combine all competency text
    all_text = " ".join(f"{c.title} {c.description}" for c in competencies).lower()

    # Check which gap keywords are covered
    for keyword in jd_keyword_gap:
        if keyword.lower() in all_text:
            covered.add(keyword)

    return covered


def _check_industry_first_ranking(
    self: Any, competencies: List[CompetencyItem], target_industry: str
) -> bool:
    """Check if competencies follow Industry-First ranking.

    Args:
        competencies: Generated competencies
        target_industry: Target industry

    Returns:
        True if Industry-First compliant
    """
    # Simplified check - first competency should mention industry
    if competencies:
        first_comp_text = f"{competencies[0].title} {competencies[0].description}".lower()
        return target_industry.lower() in first_comp_text

    return False
