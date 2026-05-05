"""apps_lic.signals.types — W3.P1

Signal types for resurfacing logic.

Defines the canonical signal taxonomy that can trigger wake events:
- Hiring signals: job posting volume, role seniority changes
- Funding signals: raise announcements, Series progression
- Competitive signals: competitor moves, market shifts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class SignalType(str, Enum):
    """Types of signals that can trigger resurfacing."""
    
    # Hiring signals
    HIRING_SURGE = "hiring_surge"           # Multiple job postings
    EXEC_ROLE_OPEN = "exec_role_open"       # C-level/VP role opened
    TEAM_EXPANSION = "team_expansion"       # Team size growth
    
    # Funding signals
    FUNDING_ROUND = "funding_round"         # Series A/B/C/etc
    IPO_ANNOUNCEMENT = "ipo_announcement"   # IPO filing/pricing
    ACQUISITION = "acquisition"             # M&A event
    
    # Competitive signals
    COMPETITOR_LAUNCH = "competitor_launch" # Competitor product/feature
    MARKET_SHIFT = "market_shift"           # Industry trend change
    REGULATORY_CHANGE = "regulatory_change" # New regulation/policy
    
    # Engagement signals
    PROFILE_VIEW = "profile_view"           # Recipient viewed profile
    CONTENT_ENGAGEMENT = "content_engagement" # Liked/commented on content
    

class SignalStrength(str, Enum):
    """Strength/confidence of a signal."""
    
    STRONG = "strong"       # Multiple corroborating sources
    MODERATE = "moderate"   # Single reliable source
    WEAK = "weak"           # Indication only, needs verification


class SignalSource(str, Enum):
    """Where the signal originated from."""
    
    LINKEDIN = "linkedin"           # LinkedIn activity/posts
    CRUNCHBASE = "crunchbase"       # Funding/hiring data
    NEWS = "news"                   # News articles
    COMPANY_WEBSITE = "company_website"  # Job postings, press releases
    RESEARCH = "research"           # Internal research systems
    MANUAL = "manual"               # Human-entered signal


@dataclass(frozen=True)
class ResurfacingSignal:
    """A detected signal that can trigger touch resurfacing.
    
    Fields
    ------
    signal_id : str
        Unique signal identifier
    signal_type : SignalType
        Type of signal detected
    strength : SignalStrength
        Confidence in the signal
    source : SignalSource
        Where signal originated
    detected_at : datetime
        When signal was detected (UTC)
    company_id : Optional[str]
        Company this signal relates to (if applicable)
    recipient_id : Optional[str]
        Specific recipient (if known)
    raw_text : str
        Raw signal text (up to 500 chars)
    metadata : dict
        Additional signal metadata
    
    Example
    -------
    >>> signal = ResurfacingSignal(
    ...     signal_id="sig-001",
    ...     signal_type=SignalType.FUNDING_ROUND,
    ...     strength=SignalStrength.STRONG,
    ...     source=SignalSource.CRUNCHBASE,
    ...     detected_at=datetime.now(timezone.utc),
    ...     company_id="acme-corp",
    ...     raw_text="Acme Corp raised $50M Series B led by Andreessen Horowitz",
    ...     metadata={"amount": "$50M", "series": "B", "lead_investor": "a16z"},
    ... )
    """
    
    signal_id: str
    signal_type: SignalType
    strength: SignalStrength
    source: SignalSource
    detected_at: datetime
    company_id: Optional[str] = None
    recipient_id: Optional[str] = None
    raw_text: str = ""
    metadata: dict[str, str] = field(default_factory=dict)
    
    def to_wake_trigger(self) -> dict:
        """Convert signal to wake trigger format for scheduler."""
        return {
            "trigger_signal": self.signal_type.value,
            "trigger_confidence": self._strength_to_confidence(),
            "trigger_source": self.source.value,
            "trigger_detected_at": self.detected_at.isoformat(),
            "trigger_metadata": self.metadata,
        }
    
    def _strength_to_confidence(self) -> float:
        """Map signal strength to confidence score (0.0-1.0)."""
        mapping = {
            SignalStrength.STRONG: 0.9,
            SignalStrength.MODERATE: 0.7,
            SignalStrength.WEAK: 0.4,
        }
        return mapping.get(self.strength, 0.5)
    
    def should_boost_cadence(self) -> bool:
        """Whether this signal should accelerate touch timing."""
        # Strong signals from competitive/funding sources boost cadence
        if self.strength != SignalStrength.STRONG:
            return False
        
        boost_triggers = {
            SignalType.FUNDING_ROUND,
            SignalType.EXEC_ROLE_OPEN,
            SignalType.COMPETITOR_LAUNCH,
            SignalType.ACQUISITION,
        }
        return self.signal_type in boost_triggers
    
    def recommended_action(self) -> str:
        """Recommended action based on signal type."""
        actions = {
            SignalType.HIRING_SURGE: "reference_role_expansion",
            SignalType.EXEC_ROLE_OPEN: "reference_leadership_search",
            SignalType.FUNDING_ROUND: "reference_growth_trajectory",
            SignalType.COMPETITOR_LAUNCH: "reference_competitive_differentiation",
            SignalType.PROFILE_VIEW: "light_nudge",
            SignalType.CONTENT_ENGAGEMENT: "value_add_followup",
        }
        return actions.get(self.signal_type, "standard_resurface")


@dataclass(frozen=True)
class SignalDetectionResult:
    """Result of signal detection for a company/recipient.
    
    Fields
    ------
    target_id : str
        Company or recipient that was checked
    signals : list[ResurfacingSignal]
        Signals detected (empty if none)
    checked_at : datetime
        When check occurred
    sources_checked : list[SignalSource]
        Which sources were queried
    error : Optional[str]
        Error message if check failed
    """
    
    target_id: str
    signals: list[ResurfacingSignal] = field(default_factory=list)
    checked_at: datetime = field(default_factory=lambda: datetime.now())
    sources_checked: list[SignalSource] = field(default_factory=list)
    error: Optional[str] = None
    
    @property
    def has_strong_signals(self) -> bool:
        """Whether any strong signals were detected."""
        return any(
            s.strength == SignalStrength.STRONG for s in self.signals
        )
    
    @property
    def strongest_signal(self) -> Optional[ResurfacingSignal]:
        """Get the strongest signal (by strength, then recency)."""
        if not self.signals:
            return None
        
        strength_order = {
            SignalStrength.STRONG: 3,
            SignalStrength.MODERATE: 2,
            SignalStrength.WEAK: 1,
        }
        
        return max(
            self.signals,
            key=lambda s: (strength_order.get(s.strength, 0), s.detected_at),
        )


# Signal priority for ordering when multiple detected
SIGNAL_PRIORITY: dict[SignalType, int] = {
    SignalType.FUNDING_ROUND: 1,
    SignalType.ACQUISITION: 2,
    SignalType.EXEC_ROLE_OPEN: 3,
    SignalType.HIRING_SURGE: 4,
    SignalType.COMPETITOR_LAUNCH: 5,
    SignalType.IPO_ANNOUNCEMENT: 6,
    SignalType.TEAM_EXPANSION: 7,
    SignalType.MARKET_SHIFT: 8,
    SignalType.REGULATORY_CHANGE: 9,
    SignalType.PROFILE_VIEW: 10,
    SignalType.CONTENT_ENGAGEMENT: 11,
}


def sort_signals_by_priority(
    signals: list[ResurfacingSignal],
) -> list[ResurfacingSignal]:
    """Sort signals by priority (high priority first), then recency."""
    return sorted(
        signals,
        key=lambda s: (
            SIGNAL_PRIORITY.get(s.signal_type, 99),
            s.detected_at,  # More recent = higher (descending will flip)
        ),
        reverse=True,
    )


__all__ = [
    "SignalType",
    "SignalStrength",
    "SignalSource",
    "ResurfacingSignal",
    "SignalDetectionResult",
    "SIGNAL_PRIORITY",
    "sort_signals_by_priority",
]
