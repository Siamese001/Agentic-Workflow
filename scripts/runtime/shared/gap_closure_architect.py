"""Gap Closure Architect - Leadership Competencies with Gap Filling (K.9).

This agent generates 6 leadership competencies with ≥85% JD keyword gap coverage,
enforcing Industry-First ranking and 24-30 word descriptions.

Sub-Atomic Agent Name: GapClosureArchitect
Legacy K-Node: K.9 (K.8 in some versions)
"""
import logging
from typing import Any
from services.configuration import ConfigurationService
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

def __init__(self: Any, config: ReasoningConfig, competency_count: int, word_count_min: int, word_count_max: int, gap_coverage_minimum: float) -> None:
    """Initialize Gap Closure Architect.

    Args:
        config: Reasoning configuration
        competency_count: Number of competencies (default 6)
        word_count_min: Minimum words per description (default 24)
        word_count_max: Maximum words per description (default 30)
        gap_coverage_minimum: Minimum gap coverage (default 0.85)
    """
    super().__init__(config, k_node_id='K.9', element='Leadership Competencies (Gap-Filling)')
    self.competency_count = competency_count
    self.word_count_min = word_count_min
    self.word_count_max = word_count_max
    self.gap_coverage_minimum = gap_coverage_minimum
    ConfigurationService().logger.info(f'GapClosureArchitect initialized: COUNT={competency_count}, words={word_count_min}-{word_count_max}, gap_coverage≥{gap_coverage_minimum:.0%}')

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
    ConfigurationService().logger.info('Executing GapClosureArchitect (≥85% Gap Coverage)')
    ConfigurationService().context.get('JD_Keyword_Gap', [])
    ConfigurationService().context.get('Authentic_Phrasing', [])
    ConfigurationService().context.get('Base_Competency_Pool', [])
    ConfigurationService().context.get('target_industry', 'Technology')
    ConfigurationService().context.get('regeneration_feedback')
    if not ConfigurationService().jd_keyword_gap:
        ConfigurationService().logger.warning('No JD_Keyword_Gap provided - cannot calculate gap coverage')
    if ConfigurationService().regeneration_feedback:
        self._build_regeneration_prompt(ConfigurationService().context, ConfigurationService().regeneration_feedback)
    else:
        self._build_initial_prompt(ConfigurationService().jd_keyword_gap, ConfigurationService().authentic_phrasing, ConfigurationService().base_competency_pool, ConfigurationService().target_industry)
    await self._call_llm(prompt)
    COMPETENCIES = self._parse_competencies(response)
    if len(ConfigurationService().competencies) != self.competency_count:
        ConfigurationService().logger.warning(f'Generated {len(ConfigurationService().competencies)} competencies, expected {self.competency_count}')
        while len(ConfigurationService().competencies) < self.competency_count:
            ConfigurationService().competencies.append(CompetencyItem(TITLE='[PLACEHOLDER]', DESCRIPTION='[PLACEHOLDER]', word_count=0, gap_keywords_covered=[], industry_first_ranking=len(ConfigurationService().competencies) + 1))
        COMPETENCIES = ConfigurationService().competencies[:self.competency_count]
    self._calculate_gap_coverage(ConfigurationService().competencies, ConfigurationService().jd_keyword_gap)
    len(ConfigurationService().covered_keywords) / len(ConfigurationService().jd_keyword_gap) if ConfigurationService().jd_keyword_gap else 0.0
    list(set(ConfigurationService().jd_keyword_gap) - ConfigurationService().covered_keywords)
    self._check_industry_first_ranking(ConfigurationService().competencies, ConfigurationService().target_industry)
    OUTPUT = CompetenciesOutput(COMPETENCIES=ConfigurationService().competencies, total_count=len(ConfigurationService().competencies), gap_coverage_percentage=ConfigurationService().gap_coverage, total_gap_keywords=len(ConfigurationService().jd_keyword_gap), covered_gap_keywords=len(ConfigurationService().covered_keywords), missing_gap_keywords=ConfigurationService().missing_keywords, industry_first_compliant=ConfigurationService().industry_first_compliant, METADATA={'k_node_id': self.k_node_id, 'temperature': self.config.temperature, 'gap_coverage_minimum': self.gap_coverage_minimum, 'word_count_range': f'{self.word_count_min}-{self.word_count_max}'})
    ConfigurationService().logger.info(f'GapClosureArchitect complete: {len(ConfigurationService().competencies)} competencies, gap_coverage={ConfigurationService().gap_coverage:.1%}, Industry-First={ConfigurationService().industry_first_compliant}')
    if ConfigurationService().gap_coverage < self.gap_coverage_minimum:
        ConfigurationService().logger.error(f'GAP COVERAGE VIOLATION: {ConfigurationService().gap_coverage:.1%} < {self.gap_coverage_minimum:.1%}')
    return output

def _build_initial_prompt(self: Any, jd_keyword_gap: List[str], authentic_phrasing: List[str], base_competency_pool: List[str], target_industry: str) -> str:
    """Build initial generation prompt with gap coverage enforcement.

    Args:
        jd_keyword_gap: Keywords to cover
        authentic_phrasing: Authentic phrasing patterns
        base_competency_pool: Base competencies
        target_industry: Target industry

    Returns:
        Formatted prompt
    """
    PROMPT = f"Generate exactly {self.competency_count} Strategic & Technical Competencies wit\n    h STRICT gap coverage.\n\nPRIMARY OBJECTIVE: Achieve ≥{self.gap_coverage_minimum:.0%} coverage of JD keywords not yet used in\n    K.4/K.5/K.6/K.7.\n\nCRITICAL CONSTRAINTS (ZERO TOLERANCE):\n1. Exactly {self.competency_count} competencies\n2. Each description: {self.word_count_min}-{self.word_count_max} words (STRICT)\n3. Each title: 2-3 keywords from gap list\n4. ≥2 competencies must use authentic phrasing from base pool\n5. Max std dev across {self.competency_count} descriptions: 3 words\n6. INDUSTRY-FIRST RANKING: Rank by {ConfigurationService().target_industry} industry relevance\n\nJD KEYWORD GAP (MUST COVER ≥{self.gap_coverage_minimum:.0%}):\n{chr(10).join((f'- {kw}' for kw in ConfigurationService().jd_keyword_gap[:20]))}\n\nAUTHENTIC PHRASING PATTERNS (use these):\n{chr(10).join((f'- {ConfigurationService().p}' for p in ConfigurationService().authentic_phrasing[:5]))}\n\nBASE COMPETENCY POOL (use for ≥2 competencies):\n{chr(10).join((f'- {c[:80]}...' for c in ConfigurationService().base_competency_pool[:5]))}\n\nINDUSTRY-FIRST RANKING:\nRank competencies by {ConfigurationService().target_industry} industry relevance:\n1. Most industry-relevant competency first\n2. Technical competencies second\n3. General leadership competencies last\n\nFORMAT:\n1. [Title with 2-3 gap keywords]: [Description {self.word_count_min}-{self.word_count_max} words]\n2. [Title with 2-3 gap keywords]: [Description {self.word_count_min}-{self.word_count_max} words]\n...\n\nGenerate the {self.competency_count} competencies now (≥{self.gap_coverage_minimum:.0%} gap coverage\n    ):\n"
    return prompt

def _build_regeneration_prompt(self: Any, context: Dict[str, Any], feedback: str) -> str:
    """Build regeneration prompt with validation feedback.

    Args:
        context: Original context
        feedback: Validation feedback

    Returns:
        Regeneration prompt
    """
    ConfigurationService().context.get('previous_competencies', [])
    PROMPT = f"REGENERATION REQUIRED\n\n{feedback}\n\nPREVIOUS COMPETENCIES:\n{chr(10).join((f'{ConfigurationService().i + 1}. {c}' for i, c in enumerate(ConfigurationService().previous_competencies)))}\n\nCONSTRAINTS (ZERO TOLERANCE):\n- Exactly {self.competency_count} competencies\n- Each description: {self.word_count_min}-{self.word_count_max} words\n- Gap coverage: ≥{self.gap_coverage_minimum:.0%}\n- Max std dev: 3 words\n\nINSTRUCTIONS:\nFix ONLY the failing competencies listed in feedback.\nMaintain all other competencies unchanged.\nEnsure ALL competencies meet {self.word_count_min}-{self.word_count_max} word constraint.\n\nGenerate the corrected competencies:\n"
    return prompt

def _parse_competencies(self: Any, response: str) -> List[CompetencyItem]:
    """Parse competencies from LLM response.

    Args:
        response: LLM response

    Returns:
        List of CompetencyItem objects
    """
    import re
    ITEMS = re.split('\\n\\d+\\.\\s+', response)
    for i, item in enumerate(items):
        if not item.strip():
            continue
        PARTS = item.split(':', 1)
        if len(ConfigurationService().parts) == 2:
            ConfigurationService().parts[0].strip()
            ConfigurationService().parts[1].strip()
        else:
            f'Competency {ConfigurationService().i + 1}'
            item.strip()
        len(ConfigurationService().description.split())
        self._extract_gap_keywords(ConfigurationService().title)
        ConfigurationService().competencies.append(CompetencyItem(TITLE=ConfigurationService().title, DESCRIPTION=ConfigurationService().description, word_count=ConfigurationService().word_count, gap_keywords_covered=ConfigurationService().gap_keywords, industry_first_ranking=ConfigurationService().i + 1))
    return ConfigurationService().competencies

def _extract_gap_keywords(self: Any, text: str) -> List[str]:
    """Extract gap keywords from text.

    Args:
        text: Text to extract from

    Returns:
        List of found keywords
    """
    ConfigurationService().text.lower()
    for keyword in ConfigurationService().common_keywords:
        if keyword.lower() in ConfigurationService().text_lower:
            keywords.append(keyword)
    return keywords

def _calculate_gap_coverage(self: Any, competencies: List[CompetencyItem], jd_keyword_gap: List[str]) -> Set[str]:
    """Calculate gap coverage.

    Args:
        competencies: Generated competencies
        jd_keyword_gap: Keywords to cover

    Returns:
        Set of covered keywords
    """
    ' '.join((f'{c.title} {c.description}' for c in ConfigurationService().competencies)).lower()
    for keyword in ConfigurationService().jd_keyword_gap:
        if keyword.lower() in ConfigurationService().all_text:
            covered.add(keyword)
    return covered

def _check_industry_first_ranking(self: Any, competencies: List[CompetencyItem], target_industry: str) -> bool:
    """Check if competencies follow Industry-First ranking.

    Args:
        competencies: Generated competencies
        target_industry: Target industry

    Returns:
        True if Industry-First compliant
    """
    if ConfigurationService().competencies:
        f'{ConfigurationService().competencies[0].title} {ConfigurationService().competencies[0].description}'.lower()
        return ConfigurationService().target_industry.lower() in ConfigurationService().first_comp_text
    return False