"""CompanyBrief Pydantic types for apps_rg narrative pipeline.

Mirrors apps_rg/schemas/company_research.schema.json. Produced by:
- User upload at apps_rg/scripts/_interactive_brief.json (wizard-managed) or via --manual-brief flag
- apps_research --mode company
- Cross-app facade in apps_shared/adapters/research_facade.py
- Tavily supplement (fills null/stale fields only; never produces from scratch)

Plan: .windsurf/plans/apps-rg-narrative-and-company-research-e3f8c1.md (P1.1).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class CompanyBriefSource(str, Enum):
    USER_UPLOADED = "user_uploaded"
    TAVILY_RESEARCH = "tavily_research"
    APPS_RESEARCH = "apps_research"
    MANUAL = "manual"


class CompanyOverview(BaseModel):
    tagline: str
    founded: Optional[int] = None
    size_band: Optional[str] = None
    ownership: Optional[str] = None
    headquarters: Optional[str] = None
    core_offerings: List[str] = Field(default_factory=list)


class CustomerProfile(BaseModel):
    verticals: List[str] = Field(default_factory=list)
    buyer_titles: List[str] = Field(default_factory=list)
    typical_engagement_size: Optional[str] = None


class LeadershipEntry(BaseModel):
    name: str
    title: str
    background: Optional[str] = None


class RecentMove(BaseModel):
    date: str
    event: str
    signal: str


class CompanyBrief(BaseModel):
    """Structured company intelligence consumed by apps_rg narrative HOPs."""

    company: str
    fetched_at: datetime
    source: CompanyBriefSource
    freshness_ttl_days: int = 30

    overview: CompanyOverview
    strategic_priorities: List[str] = Field(min_length=2)
    customer_profile: CustomerProfile = Field(default_factory=CustomerProfile)
    tech_stack_signals: List[str] = Field(default_factory=list)
    cultural_cues: List[str] = Field(default_factory=list)
    leadership: List[LeadershipEntry] = Field(default_factory=list)
    competitive_set: List[str] = Field(default_factory=list)
    pain_points_inferred: List[str] = Field(default_factory=list)
    recent_moves: List[RecentMove] = Field(default_factory=list)

    # High-leverage narrative inputs.
    language_to_mirror: List[str] = Field(min_length=3)
    language_to_avoid: List[str] = Field(default_factory=list)

    @field_validator("strategic_priorities")
    @classmethod
    def _strip_empty(cls, v: List[str]) -> List[str]:
        cleaned = [s.strip() for s in v if s and s.strip()]
        if len(cleaned) < 2:
            raise ValueError("strategic_priorities must contain at least 2 non-empty entries")
        return cleaned

    @field_validator("language_to_mirror")
    @classmethod
    def _mirror_min(cls, v: List[str]) -> List[str]:
        cleaned = [s.strip() for s in v if s and s.strip()]
        if len(cleaned) < 3:
            raise ValueError("language_to_mirror must contain at least 3 entries")
        return cleaned

    def is_stale(self, *, now: Optional[datetime] = None) -> bool:
        """True when fetched_at is older than freshness_ttl_days."""
        now = now or datetime.now(timezone.utc)
        fetched = self.fetched_at
        if fetched.tzinfo is None:
            fetched = fetched.replace(tzinfo=timezone.utc)
        age_days = (now - fetched).total_seconds() / 86400.0
        return age_days > float(self.freshness_ttl_days)


class CompanyBriefMissingError(RuntimeError):
    """Raised by HOP-0.6-COMPANY-RESEARCH when no brief can be loaded.

    Per locked decision D2: fail loudly. No JD-only fallback.
    """


__all__ = [
    "CompanyBrief",
    "CompanyBriefMissingError",
    "CompanyBriefSource",
    "CompanyOverview",
    "CustomerProfile",
    "LeadershipEntry",
    "RecentMove",
]
