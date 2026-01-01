"""
Brief Contracts - SSOT for all brief and template models.
Modularized from core_contracts.py for DDD bounded context isolation.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class subject_line_brief:
    """Brief for subject line generation."""
    word_count: tuple[int, int]
    tone: str
    forbidden_phrases: List[str] = field(default_factory=list)

# Backward compat alias
SubjectLineBrief = subject_line_brief


@dataclass
class message_body_brief:
    """Brief for message body generation."""
    word_count: tuple[int, int]
    jargon_level: str
    focus: str

# Backward compat alias
MessageBodyBrief = message_body_brief


@dataclass
class cta_brief:
    """Brief for call-to-action generation."""
    word_count: tuple[int, int]
    tone: str
    strategy: Optional[str] = None

# Backward compat alias
CTABrief = cta_brief


@dataclass
class creative_brief:
    """Complete creative brief for message generation."""
    subject_line: subject_line_brief
    message_body: message_body_brief
    cta: cta_brief

# Backward compat alias
CreativeBrief = creative_brief


@dataclass
class archetype_template:
    """Complete template for an archetype."""
    archetype: str
    system_instructions: str
    tone: str
    approach: str
    avoid: str
    creative_brief: creative_brief

# Backward compat alias
ArchetypeTemplate = archetype_template


@dataclass
class signature_template:
    """Template for message signature."""
    template: str
    use_for: List[str]
    line_count: int

# Backward compat alias
SignatureTemplate = signature_template


@dataclass
class greeting_template:
    """Template for message greeting."""
    template: str
    note: str

# Backward compat alias
GreetingTemplate = greeting_template


@dataclass
class headline_brief:
    """Brief for headline generation."""
    word_count_min: int
    word_count_max: int
    component_words_min: int
    component_words_max: int

# Backward compat alias
HeadlineBrief = headline_brief


@dataclass
class experience_bullets_brief:
    """Brief for experience bullet generation."""
    word_count_range: tuple[int, int]
    provenance_split: dict
    canonical_verbs: List[str] = field(default_factory=list)

# Backward compat alias
ExperienceBulletsBrief = experience_bullets_brief


@dataclass
class leadership_competencies_brief:
    """Brief for leadership competencies section."""
    min_differentiators: int
    focus_areas: List[str] = field(default_factory=list)

# Backward compat alias
LeadershipCompetenciesBrief = leadership_competencies_brief


@dataclass
class cover_letter_brief:
    """Brief for cover letter generation."""
    p1_word_count: tuple[int, int]
    p2_word_count: tuple[int, int]
    p3_word_count: tuple[int, int]
    jd_relevance_threshold: float

# Backward compat alias
CoverLetterBrief = cover_letter_brief


@dataclass
class optimized_skills_brief:
    """Brief for skills optimization."""
    count_range: tuple[int, int]
    word_count_range: tuple[int, int]

# Backward compat alias
OptimizedSkillsBrief = optimized_skills_brief


@dataclass
class executive_summary_brief:
    """Brief for executive summary generation."""
    sentence_count_range: tuple[int, int]
    word_count_range: tuple[int, int]

# Backward compat alias
ExecutiveSummaryBrief = executive_summary_brief


# Public exports
__all__ = [
    # Snake case (canonical)
    "subject_line_brief",
    "message_body_brief",
    "cta_brief",
    "creative_brief",
    "archetype_template",
    "signature_template",
    "greeting_template",
    "headline_brief",
    "experience_bullets_brief",
    "leadership_competencies_brief",
    "cover_letter_brief",
    "optimized_skills_brief",
    "executive_summary_brief",
    # PascalCase aliases (backward compat)
    "SubjectLineBrief",
    "MessageBodyBrief",
    "CTABrief",
    "CreativeBrief",
    "ArchetypeTemplate",
    "SignatureTemplate",
    "GreetingTemplate",
    "HeadlineBrief",
    "ExperienceBulletsBrief",
    "LeadershipCompetenciesBrief",
    "CoverLetterBrief",
    "OptimizedSkillsBrief",
    "ExecutiveSummaryBrief",
]
