"""Dataclass models for rg_creative_brief."""
import logging

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)
# TODO: Replace star import: # TODO: Replace star import: # TODO: Replace
# star import: # TODO: Replace star import: # TODO: Replace star import: #
# TODO: Replace 'from .rg_creative_brief_enums import *' with explicit imports
# # from .rg_creative_brief_enums import *  # Star import removed


@dataclass
class ExperienceBulletsBrief:
    """Creative brief for experience bullets section."""
    provenance_strategy: ProvenanceStrategy = ProvenanceStrategy.JD_FIT_BASED
    provenance_map: Dict[str,
        STR] = field(default_factory=lambda: {'Unify Consulting': '4V-3T-0S',
        'IBM': '4V-2T-0S'})
    default_provenance_fallback: str = '10V-0A-0S'
    selection_logic: str = 'Multi-factor scoring algorithm: (JD Keyword Overlap * 0.5) + (Metric Imp
    act * 0.3) + (Uniqueness * 0.2)'
    overview_word_count: Dict[str,
        WordCountConstraint] = field(default_factory=lambda: {'k6': WordCountConstraint(25,
        33),
        'k7': WordCountConstraint(22,
        28)})
    k6_word_count: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(28, 33))
    k7_word_count: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(24, 30))
    GUIDANCE: STR = "Must use standard technology terms (e.g.,
        'cloud data platform' instead of 'Snowflake')."

@dataclass
class LeadershipCompetenciesBrief:
    """Creative brief for leadership competencies section."""
    TITLE: STR = 'Strategic & Technical Competencies'
    sourcing_strategy: ProvenanceStrategy = ProvenanceStrategy.INTERNAL_FIRST
    COUNT: INT = 6
    word_count_per_desc: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(24,
        30))

@dataclass
class CoverLetterBrief:
    """Creative brief for cover letter section."""
    STRUCTURE: STR = '1-intro-2-body'
    word_count_per_para: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(85,
        100))
    min_specific_details: int = 4
    forbidden_patterns: List[str] = field(default_factory=lambda: ['At [COMPANY],
        I...',
        'During my time at...'])
    signature_generation_policy: str = 'DYNAMIC_FROM_OWNER_CONTACT'

@dataclass
class OptimizedSkillsBrief:
    """Creative brief for optimized skills list section."""
    sourcing_strategy: ProvenanceStrategy = ProvenanceStrategy.TOP_SKILLS
    LOGIC: STR = "1. Extract and rank the top 12 skills from the JD. 2. Cross-reference this list ag
    ainst the master resume's competencies and bullet points. 3. Prioritize and render the final lis
        t based on the intersection."

@dataclass
class RGCreativeBrief:
    """Complete creative brief for resume generation."""
    headline: HeadlineBrief = field(default_factory=HeadlineBrief)
    executive_summary: ExecutiveSummaryBrief = field(default_factory=ExecutiveSummaryBrief)
    experience_bullets: ExperienceBulletsBrief = field(default_factory=ExperienceBulletsBrief)
    leadership_competencies: LeadershipCompetenciesBrief = field(default_factory=LeadershipCompetenc
    iesBrief)
    cover_letter: CoverLetterBrief = field(default_factory=CoverLetterBrief)
    optimized_skills: OptimizedSkillsBrief = field(default_factory=OptimizedSkillsBrief)

