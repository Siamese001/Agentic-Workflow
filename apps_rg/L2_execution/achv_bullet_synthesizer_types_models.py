"""Dataclass models for achv_bullet_synthesizer_types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .achv_bullet_synthesizer_types_enums import *

@dataclass
class ProvenancePattern:
    format_type: BulletFormat
    verb_count: int
    tech_count: int
    soft_count: int

    def __str__(self) -> str:
        return f'{self.verb_count}V-{self.tech_count}T-{self.soft_count}S'

@dataclass
class BulletProvenanceLog:
    bullet_text: str
    word_count: int
    provenance_items: Dict[ProvenanceType, List[str]]
    pattern_match: bool
    expected_pattern: str
    actual_pattern: str

@dataclass
class BulletSynthesizerConfig:
    """Configuration for bullet point synthesis.
    
    Controls the synthesis parameters including tone, length,
    and formatting options for achievement bullets.
    """
    format_type: BulletFormat = BulletFormat.UNIFY
    temperature: float = 0.6
    max_attempts: int = 3

    @property
    def min_words(self) -> int:
        return 28 if self.format_type == BulletFormat.UNIFY else 24

    @property
    def max_words(self) -> int:
        return 33 if self.format_type == BulletFormat.UNIFY else 30

    @property
    def bullet_count(self) -> int:
        return 7 if self.format_type == BulletFormat.UNIFY else 6

    @property
    def provenance_pattern(self) -> ProvenancePattern:
        if self.format_type == BulletFormat.UNIFY:
            return ProvenancePattern(BulletFormat.UNIFY, verb_count=3, tech_count=3, soft_count=1)
        else:
            return ProvenancePattern(BulletFormat.IBM, verb_count=2, tech_count=3, soft_count=1)

@dataclass
class BulletSynthesizerResult:
    bullets: List[str]
    provenance_logs: List[BulletProvenanceLog]
    qa_report: Dict[str, Any]
    validation_results: List[ValidationResult]
    temperature_log: List[Dict[str, Any]]
    success: bool
    attempts: int

