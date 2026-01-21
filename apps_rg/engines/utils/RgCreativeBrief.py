"""
RG Creative Brief - Constraints for resume generation sections.

Ported from: archives/legacy_resume_gen/Job Workflow - JSON/Job_Workflow_v61.27.json
"""

from dataclasses import dataclass, field
from enum import Enum


class VoiceType(Enum):
    """Voice type for content generation."""

    FIRST_PERSON = "first_person"
    THIRD_PERSON = "third_person"
    THIRD_PERSON_IMPLIED = "third_person_implied"


class ProvenanceStrategy(Enum):
    """Strategy for bullet provenance."""

    JD_FIT_BASED = "JD Fit-Based Dynamic Model"
    INTERNAL_FIRST = "Hybrid 'Internal-First' Model: Map -> Adapt -> Gap-Fill"
    TOP_SKILLS = "Top 12 JD Skills & Cross-Check"


@dataclass
class WordCountConstraint:
    """Word count constraint for a section."""

    min_words: int
    max_words: int

    def validate(self, text: str) -> tuple[bool, str]:
        """Validate text against word count constraint."""
        word_count = len(text.split())
        if word_count < self.min_words:
            return False, f"Word count {word_count} below minimum {self.min_words}"
        if word_count > self.max_words:
            return False, f"Word count {word_count} above maximum {self.max_words}"
        return True, ""


@dataclass
class CharCountConstraint:
    """Character count constraint for a section."""

    max_chars: int

    def validate(self, text: str) -> tuple[bool, str]:
        """Validate text against character count constraint."""
        char_count = len(text)
        if char_count > self.max_chars:
            return False, f"Character count {char_count} above maximum {self.max_chars}"
        return True, ""


@dataclass
class StructureConstraint:
    """Structure constraint for a section."""

    structure: str
    segment_word_limit: int | None = None
    exclusions: list[str] = field(default_factory=list)


@dataclass
class HeadlineBrief:
    """Creative brief for headline section."""

    word_count: WordCountConstraint = field(
        default_factory=lambda: WordCountConstraint(8, 12)
    )
    char_count_max: int = 90
    structure: str = "Domain | Leadership | Value Prop"
    segment_word_limit: int = 3
    exclusions: list[str] = field(
        default_factory=lambda: [
            "and", "a", "an", "the", "in", "on", "at", "for", "to", "of"
        ]
    )
    guidance: str = (
        "Must incorporate differentiator keywords from the Competitive Analysis."
    )


@dataclass
class ExecutiveSummaryBrief:
    """Creative brief for executive summary section."""

    word_count: WordCountConstraint = field(
        default_factory=lambda: WordCountConstraint(120, 140)
    )
    voice: VoiceType = VoiceType.THIRD_PERSON_IMPLIED
    forbidden_patterns: list[str] = field(
        default_factory=lambda: [
            "I have",
            "My expertise",
            "At [COMPANY], I",
        ]
    )
    guidance: str = (
        "Subtly incorporate the 'primary_theme' from the K.0 analysis, "
        "while strictly maintaining the narrative voice of a professional "
        "executive biography. Do not use phrasing from the job posting."
    )


@dataclass
class ExperienceBulletsBrief:
    """Creative brief for experience bullets section."""

    provenance_strategy: ProvenanceStrategy = ProvenanceStrategy.JD_FIT_BASED
    ProvenanceMap: dict[str, str] = field(
        default_factory=lambda: {
            "Unify Consulting": "4V-3T-0S",
            "IBM": "4V-2T-0S",
        }
    )
    default_provenance_fallback: str = "10V-0A-0S"
    selection_logic: str = (
        "Multi-factor scoring algorithm: "
        "(JD Keyword Overlap * 0.5) + (Metric Impact * 0.3) + (Uniqueness * 0.2)"
    )
    overview_word_count: dict[str, WordCountConstraint] = field(
        default_factory=lambda: {
            "k6": WordCountConstraint(25, 33),
            "k7": WordCountConstraint(22, 28),
        }
    )
    k6_word_count: WordCountConstraint = field(
        default_factory=lambda: WordCountConstraint(28, 33)
    )
    k7_word_count: WordCountConstraint = field(
        default_factory=lambda: WordCountConstraint(24, 30)
    )
    guidance: str = (
        "Must use standard technology terms "
        "(e.g., 'cloud data platform' instead of 'Snowflake')."
    )


@dataclass
class LeadershipCompetenciesBrief:
    """Creative brief for leadership competencies section."""

    title: str = "Strategic & Technical Competencies"
    sourcing_strategy: ProvenanceStrategy = ProvenanceStrategy.INTERNAL_FIRST
    count: int = 6
    word_count_per_desc: WordCountConstraint = field(
        default_factory=lambda: WordCountConstraint(24, 30)
    )


@dataclass
class CoverLetterBrief:
    """Creative brief for cover letter section."""

    structure: str = "1-intro-2-body"
    word_count_per_para: WordCountConstraint = field(
        default_factory=lambda: WordCountConstraint(85, 100)
    )
    min_specific_details: int = 4
    forbidden_patterns: list[str] = field(
        default_factory=lambda: [
            "At [COMPANY], I...",
            "During my time at...",
        ]
    )
    signature_generation_policy: str = "DYNAMIC_FROM_OWNER_CONTACT"


@dataclass
class OptimizedSkillsBrief:
    """Creative brief for optimized skills list section."""

    sourcing_strategy: ProvenanceStrategy = ProvenanceStrategy.TOP_SKILLS
    logic: str = (
        "1. Extract and rank the top 12 skills from the JD. "
        "2. Cross-reference this list against the master resume's "
        "competencies and bullet points. "
        "3. Prioritize and render the final list based on the intersection."
    )


@dataclass
class RGCreativeBrief:
    """Complete creative brief for resume generation."""

    headline: HeadlineBrief = field(default_factory=HeadlineBrief)
    executive_summary: ExecutiveSummaryBrief = field(
        default_factory=ExecutiveSummaryBrief
    )
    experience_bullets: ExperienceBulletsBrief = field(
        default_factory=ExperienceBulletsBrief
    )
    leadership_competencies: LeadershipCompetenciesBrief = field(
        default_factory=LeadershipCompetenciesBrief
    )
    cover_letter: CoverLetterBrief = field(default_factory=CoverLetterBrief)
    optimized_skills: OptimizedSkillsBrief = field(default_factory=OptimizedSkillsBrief)


class CreativeBriefValidator:
    """Validator for creative brief compliance."""

    def __init__(self, brief: RGCreativeBrief) -> None:
        """Initialize with a creative brief."""
        self.brief = brief

    def validate_headline(self, text: str) -> dict[str, object]:
        """Validate headline against brief."""
        result: dict[str, object] = {
            "is_valid": True,
            "violations": [],
            "metrics": {},
        }

        # Word count
        is_valid, message = self.brief.headline.word_count.validate(text)
        result["metrics"]["word_count"] = len(text.split())
        if not is_valid:
            result["is_valid"] = False
            result["violations"].append(message)

        # Character count
        if len(text) > self.brief.headline.char_count_max:
            result["is_valid"] = False
            result["violations"].append(
                f"Character count {len(text)} exceeds max "
                f"{self.brief.headline.char_count_max}"
            )
        result["metrics"]["char_count"] = len(text)

        # Structure check (should have pipe separators)
        if "|" not in text:
            result["violations"].append(
                f"Missing structure separators. Expected: {self.brief.headline.structure}"
            )

        return result

    def validate_executive_summary(self, text: str) -> dict[str, object]:
        """Validate executive summary against brief."""
        result: dict[str, object] = {
            "is_valid": True,
            "violations": [],
            "metrics": {},
        }

        # Word count
        is_valid, message = self.brief.executive_summary.word_count.validate(text)
        result["metrics"]["word_count"] = len(text.split())
        if not is_valid:
            result["is_valid"] = False
            result["violations"].append(message)

        # Forbidden patterns
        for pattern in self.brief.executive_summary.forbidden_patterns:
            if pattern.lower() in text.lower():
                result["is_valid"] = False
                result["violations"].append(f"Forbidden pattern found: {pattern}")

        # Voice check (no first person)
        if self.brief.executive_summary.voice == VoiceType.THIRD_PERSON_IMPLIED:
            first_person_markers = ["I ", "I'm", "I've", "my ", "me "]
            for marker in first_person_markers:
                if marker.lower() in text.lower():
                    result["violations"].append(
                        f"First person marker found: {marker.strip()}"
                    )

        return result

    def validate_bullet(
        self,
        text: str,
        section_key: str = "k6",
    ) -> dict[str, object]:
        """Validate a bullet against brief."""
        result: dict[str, object] = {
            "is_valid": True,
            "violations": [],
            "metrics": {},
        }

        # Get word count constraint for section
        if section_key == "k6":
            constraint = self.brief.experience_bullets.k6_word_count
        else:
            constraint = self.brief.experience_bullets.k7_word_count

        is_valid, message = constraint.validate(text)
        result["metrics"]["word_count"] = len(text.split())
        if not is_valid:
            result["is_valid"] = False
            result["violations"].append(message)

        return result

    def validate_cover_letter_paragraph(self, text: str) -> dict[str, object]:
        """Validate a cover letter paragraph against brief."""
        result: dict[str, object] = {
            "is_valid": True,
            "violations": [],
            "metrics": {},
        }

        # Word count
        is_valid, message = self.brief.cover_letter.word_count_per_para.validate(text)
        result["metrics"]["word_count"] = len(text.split())
        if not is_valid:
            result["is_valid"] = False
            result["violations"].append(message)

        # Forbidden patterns
        for pattern in self.brief.cover_letter.forbidden_patterns:
            if pattern.lower() in text.lower():
                result["is_valid"] = False
                result["violations"].append(f"Forbidden pattern found: {pattern}")

        return result

    def validate_competency(self, text: str) -> dict[str, object]:
        """Validate a competency description against brief."""
        result: dict[str, object] = {
            "is_valid": True,
            "violations": [],
            "metrics": {},
        }

        is_valid, message = self.brief.leadership_competencies.word_count_per_desc.validate(
            text
        )
        result["metrics"]["word_count"] = len(text.split())
        if not is_valid:
            result["is_valid"] = False
            result["violations"].append(message)

        return result


def create_creative_brief() -> RGCreativeBrief:
    """builder function to create a default creative brief."""
    return RGCreativeBrief()


def create_brief_validator(
    brief: RGCreativeBrief | None = None,
) -> CreativeBriefValidator:
    """builder function to create a brief validator."""
    if brief is None:
        brief = RGCreativeBrief()
    return CreativeBriefValidator(brief)


def get_headline_brief() -> HeadlineBrief:
    """Get default headline brief."""
    return HeadlineBrief()


def get_executive_summary_brief() -> ExecutiveSummaryBrief:
    """Get default executive summary brief."""
    return ExecutiveSummaryBrief()


def get_experience_bullets_brief() -> ExperienceBulletsBrief:
    """Get default experience bullets brief."""
    return ExperienceBulletsBrief()
