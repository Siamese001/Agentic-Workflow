"""Pydantic v2 typed models for apps_qna.

All models are frozen and forbid extra fields. They form the spine of the
builder: every Jinja template variable must come from a field declared here.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

_FROZEN: ConfigDict = ConfigDict(frozen=True, extra="forbid")


class Interviewer(BaseModel):
    """One interviewer profile.

    Multi-interviewer mode (panel) materializes one Lens card per Interviewer
    in the list.
    """

    model_config = _FROZEN

    name: str
    title: str
    team: str = ""
    public_signals: list[str] = Field(default_factory=list)
    technical_depth: Literal["low", "medium", "high"] = "medium"
    hot_buttons: list[str] = Field(default_factory=list)
    lens: str = ""


class Company(BaseModel):
    """Company-level facts the runtime should anchor on."""

    model_config = _FROZEN

    name: str
    division: str | None = None
    practice: str | None = None
    anchors: list[str] = Field(default_factory=list)
    avoid_phrases: list[str] = Field(default_factory=list)
    overlay_facts: list[str] = Field(default_factory=list)


class Role(BaseModel):
    """Role / position summary."""

    model_config = _FROZEN

    title: str
    level: str
    primary_mandate: str
    success_criteria: list[str] = Field(default_factory=list)


class JDSection(BaseModel):
    """One section of the JD with its extracted keywords."""

    model_config = _FROZEN

    heading: str
    body: str
    extracted_keywords: list[str] = Field(default_factory=list)


class JobDescription(BaseModel):
    """JD as either a raw path or structured sections (or both)."""

    model_config = _FROZEN

    raw_path: Path | None = None
    sections: list[JDSection] = Field(default_factory=list)


class ExperiencePoint(BaseModel):
    """A single bullet of relevant experience."""

    model_config = _FROZEN

    title: str
    one_liner: str
    technical_depth_tags: list[str] = Field(default_factory=list)


class Story(BaseModel):
    """STAR proof story."""

    model_config = _FROZEN

    name: str
    situation: str
    task: str
    action: str
    result: str
    lesson: str
    tags: list[str] = Field(default_factory=list)


class StoryBank(BaseModel):
    """Collection of STAR stories indexed by tag for proof routing."""

    model_config = _FROZEN

    stories: list[Story] = Field(default_factory=list)


class RCAStory(BaseModel):
    """Failure / RCA / lesson-learned story."""

    model_config = _FROZEN

    name: str
    situation: str
    task: str
    root_cause: str
    action: str
    result: str
    operating_model_change: str


class ExperienceLibrary(BaseModel):
    """All of the candidate's experience material."""

    model_config = _FROZEN

    points: list[ExperiencePoint] = Field(default_factory=list)
    star_bank: StoryBank = Field(default_factory=StoryBank)
    rca_bank: list[RCAStory] = Field(default_factory=list)


class ResearchClaim(BaseModel):
    """One claim from a research source register, labeled by claim type."""

    model_config = _FROZEN

    claim: str
    claim_type: Literal[
        "direct_evidence",
        "interpretation",
        "analyst_inference",
        "assumption",
    ]
    source_id: str
    section_id: str = ""


class GlossaryEntry(BaseModel):
    """One company- or role-specific term with definition and usage note."""

    model_config = _FROZEN

    term: str
    definition: str
    synonyms: list[str] = Field(default_factory=list)
    usage_note: str = ""


class LikelyQuestionGroup(BaseModel):
    """A predicted-questions group bound to one route id from the registry."""

    model_config = _FROZEN

    route_id: str
    questions: list[str] = Field(default_factory=list)


class ResearchInputs(BaseModel):
    """Outputs of deep-research feeders (apps_research, manual notes)."""

    model_config = _FROZEN

    company_brief: str | None = None
    role_areas_of_focus: list[str] = Field(default_factory=list)
    industry_trends: list[str] = Field(default_factory=list)
    interviewer_lenses: dict[str, str] = Field(default_factory=dict)
    source_register: list[ResearchClaim] = Field(default_factory=list)
    glossary_entries: list[GlossaryEntry] = Field(default_factory=list)
    likely_questions: list[LikelyQuestionGroup] = Field(default_factory=list)


class BuildMetadata(BaseModel):
    """Metadata about the current build run.

    The only place a real timestamp is allowed; surfaced in pack_manifest.json
    but never embedded in card content (so packs are byte-deterministic).
    """

    model_config = _FROZEN

    interview_slug: str
    built_at: datetime
    builder_version: str
    template_set_version: str
    output_dir: Path


class Interview(BaseModel):
    """Top-level interview-prep input bundle."""

    model_config = _FROZEN

    slug: str
    company: Company
    role: Role
    interviewers: list[Interviewer]
    jd: JobDescription
    experience: ExperienceLibrary
    research: ResearchInputs | None = None
    build_metadata: BuildMetadata


class CardPackManifest(BaseModel):
    """Manifest written alongside a built card pack."""

    model_config = _FROZEN

    interview_slug: str
    built_at: datetime
    builder_version: str
    template_set_version: str
    cards: list[str]  # ordered list of emitted card filenames
    routes_covered: list[str]  # route IDs whose primary card is in the pack
    interviewers: list[str]  # names; for multi-interviewer audit
    # Wave 7 — multi-tier paste optimization (Anthropic Skills/Rules guideline).
    # Subset of `cards` to actually paste into the ChatGPT Project. Excludes:
    #   - load_strategy=post_rehearsal cards (e.g., card 22 Learnings)
    #   - skill cards whose route is not in interview.research.likely_questions
    # Falls back to the full skill set when likely_questions is empty.
    pasted_cards: list[str] = Field(default_factory=list)
    # True when len(pasted_cards) > 25 (ChatGPT 5.5-Thinking project file cap).
    paste_exceeds_chatgpt_limit: bool = False
