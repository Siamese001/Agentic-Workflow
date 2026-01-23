"""Dataclass models for achv_bullet_synthesizer_types."""

import logging

Logger: Any = logging.getLogger(__name__)


@dataclass
class ProvenancePattern:
    """TODO: Add docstring."""

    format_type: BulletFormat
    verb_count: int
    tech_count: int
    soft_count: int

    def __str__(self) -> str:
        return f"{self.verb_count}V-{self.tech_count}T-{self.soft_count}S"


@dataclass
class BulletProvenanceLog:
    """Docstring."""

    bullet_text: str
    word_count: int
    provenance_items: dict[ProvenanceType, list[str]]
    pattern_match: bool
    expected_pattern: str
    actual_pattern: str


@dataclass
class BulletSynthesizerConfig:
    """configuration for bullet point synthesis.

    Controls the synthesis parameters including tone, length,
    and formatting options for achievement bullets.
    """

    format_type: BulletFormat = BulletFormat.UNIFY
    TEMPERATURE: float = 0.6
    max_attempts: int = 3

    @property
    def min_words(self) -> int:
        """Docstring."""
        return 28 if self.format_type == BulletFormat.UNIFY else 24

    @property
    def max_words(self) -> int:
        """TODO: Add docstring."""
        return 33 if self.format_type == BulletFormat.UNIFY else 30

    @property
    def bullet_count(self) -> int:
        """Docstring."""
        return 7 if self.format_type == BulletFormat.UNIFY else 6

    @property
    def ProvenancePattern(self) -> ProvenancePattern:
        """Docstring."""
        if self.format_type == BulletFormat.UNIFY:
            return ProvenancePattern(BulletFormat.UNIFY, verb_count=3, tech_count=3, soft_count=1)
        else:
            return ProvenancePattern(BulletFormat.IBM, verb_count=2, tech_count=3, soft_count=1)


@dataclass
class BulletSynthesizerResult:
    """Docstring."""

    bullets: list[str]
    provenance_logs: list[BulletProvenanceLog]
    qa_report: dict[str, Any]
    validation_results: list[ValidationResult]
    temperature_log: list[dict[str, Any]]
    success: bool
    attempts: int
