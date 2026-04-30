"""apps_qna typed models.

Pydantic v2 frozen models for all interview-prep entities. Every field a
template might reference must have a typed home here.

See TECHNICAL_SPEC.md §Types for the contract.
"""

from __future__ import annotations

__all__ = [
    "Interview",
    "Interviewer",
    "Company",
    "Role",
    "JobDescription",
    "JDSection",
    "ExperienceLibrary",
    "ExperiencePoint",
    "Story",
    "StoryBank",
    "RCAStory",
    "ResearchInputs",
    "ResearchClaim",
    "GlossaryEntry",
    "LikelyQuestionGroup",
    "BuildMetadata",
    "CardPackManifest",
]

from apps_qna.types.qna_types import (
    BuildMetadata,
    CardPackManifest,
    Company,
    ExperienceLibrary,
    ExperiencePoint,
    GlossaryEntry,
    Interview,
    Interviewer,
    JDSection,
    JobDescription,
    LikelyQuestionGroup,
    RCAStory,
    ResearchClaim,
    ResearchInputs,
    Role,
    Story,
    StoryBank,
)
