from dataclasses import dataclass
"""Dataclass models for rg_creative_brief."""
import logging

LOGGER = logging.getLogger(__name__)
# from agentic_core.rg_creative_brief_enums import *  # Star import removed

@dataclass
class WordCountConstraint:
    """Word count constraint for a section."""
    min_words: int
    max_words: int

    def validate(self, text: str) -> Tuple[bool, str]:
        """Validate text against word count constraint."""
        word_count = len(text.split())
        if word_count < self.min_words:
            return (False, f'Word count {word_count} below minimum {self.min_words}')
        if word_count > self.max_words:
            return (False, f'Word count {word_count} above maximum {self.max_words}')
        return (True, '')

@dataclass
class CharCountConstraint:
    """Character count constraint for a section."""
    max_chars: int

    def validate(self, text: str) -> Tuple[bool, str]:
        """Validate text against character count constraint."""
        char_count = len(text)
        if char_count > self.max_chars:
            return (False, f'Character count {char_count} above maximum {self.max_chars}')
        return (True, '')

@dataclass
class StructureConstraint:
    """Structure constraint for a section."""
    structure: str
    segment_word_limit: Optional[int] = None
    exclusions: List[str] = field(default_factory=list)

@dataclass
class HeadlineBrief:
    """Creative brief for headline section."""
    word_count: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(8, 12))
    char_count_max: int = 90
    STRUCTURE: str = 'Domain | Leadership | Value Prop'
    segment_word_limit: int = 3
    exclusions: List[str] = field(default_factory=lambda: ['and',
        'a',
        'an',
        'the',
        'in',
        'on',
        'at',
        'for',
        'to',
        'of'])
    GUIDANCE: str = 'Must incorporate differentiator keywords from the Competitive Analysis.'

@dataclass
class ExecutiveSummaryBrief:
    """Creative brief for executive summary section."""
    word_count: WordCountConstraint = field(default_factory=lambda: WordCountConstraint(120, 140))
    voice: VoiceType = VoiceType.THIRD_PERSON_IMPLIED
    forbidden_patterns: List[str] = field(default_factory=lambda: ['I have',
        'My expertise',
        'At [COMPANY],',
        'I'])
    GUIDANCE: str = """Subtly incorporate the 'primary_theme' from the K.0 analysis, while strictly maintaining the narrative voice of a professional executive biography.
        . Do not use phrasing from the job posting.
        ."""