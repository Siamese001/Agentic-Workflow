from __future__ import annotations
"""
Brief Contracts - SSOT for all brief and template models.
Modularized from core_contracts.py for DDD bounded context isolation.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SubjectLineBrief:
    """Brief for subject line generation."""
    word_count: tuple[int, int]
    tone: str
    forbidden_phrases: List[str] = field(default_factory=list)

# Backward compat alias


@dataclass
class MessageBodyBrief:
    """Brief for message body generation."""
    word_count: tuple[int, int]
    jargon_level: str
    focus: str

# Backward compat alias


@dataclass
class CTABrief:
    """Brief for call-to-action generation."""
    word_count: tuple[int, int]
    tone: str
    strategy: Optional[str] = None

# Backward compat alias


@dataclass
class CreativeBrief:
    """Complete creative brief for message generation."""
    subject_line: SubjectLineBrief
    message_body: MessageBodyBrief
    cta: CTABrief

# Backward compat alias


@dataclass
class ArchetypeTemplate:
    """Complete template for an Archetype."""
    Archetype: str
    system_instructions: str
    tone: str
    approach: str
    avoid: str
    CreativeBrief: CreativeBrief

# Backward compat alias


@dataclass
class SignatureTemplate:
    """Template for message signature."""
    template: str
    use_for: List[str]
    line_count: int

# Backward compat alias


@dataclass
class GreetingTemplate:
    """Template for message greeting."""
    template: str
    note: str

# Backward compat alias


@dataclass
class HeadlineBrief:
    """Brief for headline generation."""
    word_count_min: int
    word_count_max: int
    component_words_min: int
    component_words_max: int

# Backward compat alias


@dataclass
class ExperienceBulletsBrief:
    """Brief for experience bullet generation."""
    word_count_range: tuple[int, int]
    provenance_split: dict
    canonical_verbs: List[str] = field(default_factory=list)

# Backward compat alias


@dataclass
class LeadershipCompetenciesBrief:
    """Brief for leadership competencies section."""
    min_differentiators: int
    focus_areas: List[str] = field(default_factory=list)

# Backward compat alias


@dataclass
class CoverLetterBrief:
    """Brief for cover letter generation."""
    p1_word_count: tuple[int, int]
    p2_word_count: tuple[int, int]
    p3_word_count: tuple[int, int]
    jd_relevance_threshold: float

# Backward compat alias


@dataclass
class OptimizedSkillsBrief:
    """Brief for skills optimization."""
    count_range: tuple[int, int]
    word_count_range: tuple[int, int]

# Backward compat alias


@dataclass
class ExecutiveSummaryBrief:
    """Brief for executive summary generation."""
    sentence_count_range: tuple[int, int]
    word_count_range: tuple[int, int]

# Backward compat alias


# Public exports
__all__ = [
    # Snake case (canonical)
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
