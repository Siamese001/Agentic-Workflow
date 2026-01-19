from __future__ import annotations
from dataclasses import dataclass, field
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
'Executive Title Composer - Industry-First Headline Generation (K.4).\n\nThis agent generates professional headlines with strict Industry-First positioning,\nenforcing 8-13 word total count and ≤90 character limit with technology keyword blocking.\n\nSub-Atomic Agent Name: ExecutiveTitleComposer\nLegacy K-Node: K.4\n'
import logging
from typing import Any, Dict, List, Optional, Protocol
Logger: Any = logging.getLogger(__name__)

@dataclass
class HeadlineOutput:
    """Executive title composer output."""
    headline: str
    _segment_1: str
    _segment_2: str
    _segment_3: str
    word_count: int
    char_count: int
    industry_first_compliant: bool
    _technology_keywords_in_segment_1: List[str]
    _metadata: Dict[str, Any]
technology_keywords: Any = ['AI', 'ML', 'Python', 'Java', 'AWS', 'Azure', 'GCP', 'Kubernetes', 'Docker', 'React', 'Angular', 'Node.js', 'TensorFlow', 'PyTorch', 'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'Redis', 'Kafka', 'Microservices', 'API', 'REST', 'GraphQL', 'DevOps', 'CI/CD']

class ExecutiveTitleComposer(Agent):
    """Executive Title Composer agent for Industry-First headline generation.

    This agent generates headlines with strict constraints:
    - Total word count: 8-13 words (ZERO TOLERANCE)
    - Character limit: ≤90 characters (ZERO TOLERANCE)
    - Industry-First positioning: Segment 1 MUST not contain technology keywords
    - 3-segment structure: Domain | Leadership | Value Prop

    Validation Gates:
    - VG_HEADLINE_WORD_COUNT_COMPLIANCE (8-13 words)
    - VG_HEADLINE_CHARACTER_COMPLIANCE (≤90 chars)
    - VG_INDUSTRY_FIRST_COMPLIANCE (no tech in Segment 1)
    """

def __init__(self: Any, config: ReasoningConfig, word_count_min: int, word_count_max: int, char_limit: int) -> None:
    """Initialize Executive Title Composer.

    Args:
        config: Reasoning configuration
        word_count_min: Minimum word count (default 8)
        word_count_max: Maximum word count (default 13)
        char_limit: Character limit (default 90)
    """
    super().__init__(config, k_node_id='K.4', element='Executive Title (Industry-First)')
    self.word_count_min = word_count_min
    self.word_count_max = word_count_max
    self.char_limit = char_limit
    Logger.info(f'ExecutiveTitleComposer initialized: WORDS={word_count_min}-{word_count_max}, chars≤{char_limit}')

async def execute(self: Any, context: Dict[str, Any]) -> HeadlineOutput:
    """Execute headline generation with Industry-First positioning.

    Args:
        context: Execution context with:
            - target_industry: str - Target industry/domain
            - target_role: str - Target role/level
            - value_propositions: List[str] - Key value props
            - JobDescription: str - Target JD
            - regeneration_feedback: Optional[str]

    Returns:
        HeadlineOutput with 3-segment headline
    """
    Logger.info('Executing ExecutiveTitleComposer (Industry-First)')
    target_industry: Any = context.get('target_industry', 'Technology')
    target_role: Any = context.get('target_role', 'Engineering Leader')
    value_propositions: Any = context.get('value_propositions', [])
    JobDescription: Any = context.get('JobDescription', '')
    regeneration_feedback: Any = context.get('regeneration_feedback')
    if regeneration_feedback:
        PROMPT: Any = self._build_regeneration_prompt(context, regeneration_feedback)
    else:
        PROMPT: Any = self._build_initial_prompt(target_industry, target_role, value_propositions, JobDescription)
    await self._call_llm(prompt)
    response.strip()
    self._parse_segments(headline)
    tech_keywords_in_seg1: Any = self._check_technology_keywords(segments[0])
    industry_first_compliant: Any = len(tech_keywords_in_seg1) == 0
    word_count: Any = len(headline.split())
    char_count: Any = len(headline)
    OUTPUT: Any = HeadlineOutput(HEADLINE=headline, segment_1=segments[0], segment_2=segments[1], segment_3=segments[2], word_count=word_count, char_count=char_count, industry_first_compliant=industry_first_compliant, technology_keywords_in_segment_1=tech_keywords_in_seg1, METADATA={'k_node_id': self.k_node_id, 'temperature': self.config.temperature, 'word_count_range': f'{self.word_count_min}-{self.word_count_max}', 'char_limit': self.char_limit})
    Logger.info(f'ExecutiveTitleComposer complete: {word_count} words, {char_count} chars, Industry-First={industry_first_compliant}')
    if not industry_first_compliant:
        Logger.error(f'INDUSTRY-FIRST VIOLATION: Technology keywords in Segment 1: {tech_keywords_in_seg1}')
    return output

def _build_initial_prompt(self: Any, target_industry: str, target_role: str, value_propositions: List[str], JobDescription: str) -> str:
    """Build initial generation prompt with Industry-First enforcement.

    Args:
        target_industry: Target industry/domain
        target_role: Target role/level
        value_propositions: Key value props
        JobDescription: Target JD

    Returns:
        Formatted prompt
    """
    PROMPT = f"""Generate a professional resume headline with STRICT Industry-First positioning.\n\nCRITICAL CONSTRAINTS (ZERO TOLERANCE):\n1. Total word count: {self.word_count_min}-{self.word_count_max} words (STRICT)\n2. Character limit: ≤{self.char_limit} characters (STRICT)\n3. 3-segment structure: Domain | Leadership | Value Proposition\n4. INDUSTRY-FIRST POSITIONING: Segment 1 MUST not contain technology keywords\n\nINDUSTRY-FIRST RULE (BLOCKING):\n- Segment 1 must lead with INDUSTRY/DOMAIN (e.g.,\n    "Healthcare",\n    "Financial Services",\n    "Enterprise SaaS")\n- Segment 1 MUST not contain: AI, ML, Python, AWS, Kubernetes, Docker, etc.\n- Technology keywords belong in Segment 3 (Value Proposition) ONLY\n\nTARGET INDUSTRY: {target_industry}\nTARGET ROLE: {target_role}\n\nVALUE PROPOSITIONS (use for Segment 3):\n{chr(10).join((f'- {vp}' for vp in value_propositions[:3]))}\n\nJOB DESCRIPTION CONTEXT:\n{JobDescription[:300]}...\n\nSTRUCTURE:\nSegment 1: {target_industry} [Industry/Domain - NO TECHNOLOGY KEYWORDS]\nSegment 2: {target_role} [Leadership/Role]\nSegment 3: [Value Proposition - technology keywords allowed here]\n\nEXAMPLES (Industry-First Compliant):\n✅ "Healthcare Technology Leader | AI/ML Innovation | Enterprise Scale"\n✅ "Financial Services Executive | Cloud Architecture | Digital Transformation"\n✅ "Enterprise SaaS Leader | Engineering Excellence | Scalable Solutions"\n\nEXAMPLES (Industry-First VIOLATIONS - DO not USE):\n❌ "AI/ML Leader | Healthcare Technology | Innovation" (tech in Segment 1)\n❌ "Python Engineer | Cloud Architecture | SaaS" (tech in Segment 1)\n\nGenerate the headline now ({self.word_count_min}-{self.word_count_max} words,\n    ≤{self.char_limit} chars):\n"""
    return prompt

def _build_regeneration_prompt(self: Any, context: Dict[str, Any], feedback: str) -> str:
    """Build regeneration prompt with validation feedback.

    Args:
        context: Original context
        feedback: Validation feedback

    Returns:
        Regeneration prompt
    """
    previous_headline = context.get('previous_headline', '')
    PROMPT = f'REGENERATION REQUIRED\n\n{feedback}\n\nPREVIOUS HEADLINE:\n{previous_headline}\n\nCONSTRAINTS (ZERO TOLERANCE):\n- Word count: {self.word_count_min}-{self.word_count_max} words\n- Character limit: ≤{self.char_limit} characters\n- INDUSTRY-FIRST: NO technology keywords in Segment 1\n\nINSTRUCTIONS:\nFix the specific violations listed in feedback.\nMaintain Industry-First positioning.\n\nGenerate the corrected headline:\n'
    return prompt

def _parse_segments(self: Any, headline: str) -> List[str]:
    """Parse headline into 3 segments.

    Args:
        headline: Full headline

    Returns:
        List of 3 segments [Domain, Leadership, Value Prop]
    """
    [s.strip() for s in headline.split('|')]
    while len(segments) < 3:
        segments.append('')
    return segments[:3]

def _check_technology_keywords(self: Any, segment: str) -> List[str]:
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
