"""apps_lic.sequences.touch_sequence_definitions — W2.P1

3-Touch Sequence Definitions with content variation and cadence rules.

This module defines the canonical 3-touch outreach sequences for apps_lic:
- Touch 1: Initial outreach (Day 0)
- Touch 2: Soft nudge follow-up (Day 5)  
- Touch 3: Value-add final touch (Day 12)

Each sequence specifies:
- Template selection per touch
- Cadence rules (timing, delays)
- Content variation strategy
- Context carry-forward requirements
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from typing import Optional


class SequenceType(str, Enum):
    """Types of multi-touch sequences."""
    
    STANDARD_3_TOUCH = "standard_3_touch"
    EXECUTIVE_3_TOUCH = "executive_3_touch"
    RECRUITER_COMPACT = "recruiter_compact"


class TouchStrategy(str, Enum):
    """Sequencing strategy for a touch."""
    
    INITIAL = "initial"
    NUDGE = "nudge"
    FRESH_ANGLE = "fresh_angle"
    CLOSE_OR_OPTOUT = "close_or_optout"


@dataclass(frozen=True)
class TouchDefinition:
    """Definition of a single touch in a sequence.
    
    Fields
    ------
    touch_number : int
        1-based position in sequence
    template_id : str
        Template to use (e.g., "outreach_draft_v1")
    strategy : TouchStrategy
        How to approach this touch
    delay_days : int
        Days after previous touch (0 for first touch)
    p2_context_required : list[str]
        Which P2 context slots to populate
    content_variation : str
        How content varies from prior touches
    carry_forward_keys : list[str]
        Context keys to propagate to next touch
    """
    
    touch_number: int
    template_id: str
    strategy: TouchStrategy
    delay_days: int
    p2_context_required: list[str] = field(default_factory=list)
    content_variation: str = ""
    carry_forward_keys: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SequenceDefinition:
    """Definition of a complete multi-touch sequence.
    
    Fields
    ------
    sequence_type : SequenceType
        Type identifier
    name : str
        Human-readable name
    description : str
        What this sequence is for
    touches : list[TouchDefinition]
        Ordered touch definitions
    max_duration_days : int
        Maximum allowed sequence duration
    requires_p2 : bool
        Whether P2 context is required
    """
    
    sequence_type: SequenceType
    name: str
    description: str
    touches: list[TouchDefinition]
    max_duration_days: int
    requires_p2: bool = False


# =============================================================================
# Standard 3-Touch Sequence (Default)
# =============================================================================

STANDARD_3_TOUCH = SequenceDefinition(
    sequence_type=SequenceType.STANDARD_3_TOUCH,
    name="Standard 3-Touch Outreach",
    description="Baseline 3-touch sequence for general outreach",
    touches=[
        TouchDefinition(
            touch_number=1,
            template_id="outreach_draft_v1",
            strategy=TouchStrategy.INITIAL,
            delay_days=0,
            p2_context_required=["N0", "A0", "L0"],
            content_variation="Initial outreach with full context",
            carry_forward_keys=[
                "sent_at",
                "message_body_hash",
                "hook_used",
                "response_received",
            ],
        ),
        TouchDefinition(
            touch_number=2,
            template_id="outreach_draft_v2",
            strategy=TouchStrategy.NUDGE,
            delay_days=5,
            p2_context_required=["A0"],  # Tone consistency important
            content_variation="Soft nudge referencing prior touch",
            carry_forward_keys=[
                "sent_at",
                "message_body_hash",
                "prior_context_summary",
                "response_received",
            ],
        ),
        TouchDefinition(
            touch_number=3,
            template_id="outreach_draft_v2",
            strategy=TouchStrategy.FRESH_ANGLE,
            delay_days=7,
            p2_context_required=["N0", "L0"],  # New angle + competitive
            content_variation="Fresh value-add angle, avoids repetition",
            carry_forward_keys=[
                "sent_at",
                "message_body_hash",
                "angles_used",
                "response_received",
                "sequence_complete",
            ],
        ),
    ],
    max_duration_days=14,
    requires_p2=True,
)


# =============================================================================
# Executive 3-Touch Sequence
# =============================================================================

EXECUTIVE_3_TOUCH = SequenceDefinition(
    sequence_type=SequenceType.EXECUTIVE_3_TOUCH,
    name="Executive 3-Touch Outreach",
    description="Peer-to-peer outreach for C-level and VP executives",
    touches=[
        TouchDefinition(
            touch_number=1,
            template_id="exec_positioning",
            strategy=TouchStrategy.INITIAL,
            delay_days=0,
            p2_context_required=["N0", "A0", "L0"],
            content_variation="Executive-level initial with strategic framing",
            carry_forward_keys=[
                "sent_at",
                "message_body_hash",
                "strategic_hook",
                "exec_archetype_matched",
            ],
        ),
        TouchDefinition(
            touch_number=2,
            template_id="exec_positioning",
            strategy=TouchStrategy.NUDGE,
            delay_days=7,  # Longer delay for executives
            p2_context_required=["A0"],
            content_variation="Respectful follow-up acknowledging time constraints",
            carry_forward_keys=[
                "sent_at",
                "message_body_hash",
                "prior_strategic_hook",
            ],
        ),
        TouchDefinition(
            touch_number=3,
            template_id="exec_positioning",
            strategy=TouchStrategy.CLOSE_OR_OPTOUT,
            delay_days=10,
            p2_context_required=["N0"],
            content_variation="Final attempt with clear opt-out path",
            carry_forward_keys=[
                "sent_at",
                "message_body_hash",
                "final_close_type",
                "sequence_complete",
            ],
        ),
    ],
    max_duration_days=21,
    requires_p2=True,
)


# =============================================================================
# Recruiter Compact Sequence
# =============================================================================

RECRUITER_COMPACT = SequenceDefinition(
    sequence_type=SequenceType.RECRUITER_COMPACT,
    name="Recruiter Compact Sequence",
    description="Short-form sequence optimized for recruiter outreach",
    touches=[
        TouchDefinition(
            touch_number=1,
            template_id="compact_recruiter_arc",
            strategy=TouchStrategy.INITIAL,
            delay_days=0,
            p2_context_required=["N0"],  # Minimal context for recruiters
            content_variation="Compact initial with role-focused hook",
            carry_forward_keys=[
                "sent_at",
                "message_body_hash",
                "role_focus",
            ],
        ),
        TouchDefinition(
            touch_number=2,
            template_id="compact_recruiter_arc",
            strategy=TouchStrategy.NUDGE,
            delay_days=4,  # Shorter for recruiters
            p2_context_required=[],
            content_variation="Brief nudge with salary/role update if available",
            carry_forward_keys=[
                "sent_at",
                "message_body_hash",
                "update_shared",
            ],
        ),
        TouchDefinition(
            touch_number=3,
            template_id="compact_recruiter_arc",
            strategy=TouchStrategy.CLOSE_OR_OPTOUT,
            delay_days=6,
            p2_context_required=[],
            content_variation="Quick close attempt",
            carry_forward_keys=[
                "sent_at",
                "sequence_complete",
            ],
        ),
    ],
    max_duration_days=12,
    requires_p2=False,  # P2 optional for recruiters
)


# =============================================================================
# Registry
# =============================================================================

SEQUENCE_REGISTRY: dict[SequenceType, SequenceDefinition] = {
    SequenceType.STANDARD_3_TOUCH: STANDARD_3_TOUCH,
    SequenceType.EXECUTIVE_3_TOUCH: EXECUTIVE_3_TOUCH,
    SequenceType.RECRUITER_COMPACT: RECRUITER_COMPACT,
}


def get_sequence_definition(sequence_type: SequenceType) -> SequenceDefinition:
    """Get sequence definition by type."""
    if sequence_type not in SEQUENCE_REGISTRY:
        raise ValueError(f"Unknown sequence type: {sequence_type}")
    return SEQUENCE_REGISTRY[sequence_type]


def get_touch_definition(
    sequence_type: SequenceType,
    touch_number: int,
) -> Optional[TouchDefinition]:
    """Get touch definition for a specific position in sequence."""
    seq_def = get_sequence_definition(sequence_type)
    for touch in seq_def.touches:
        if touch.touch_number == touch_number:
            return touch
    return None


def list_sequence_types() -> list[SequenceType]:
    """List all available sequence types."""
    return list(SEQUENCE_REGISTRY.keys())


def calculate_touch_wake_time(
    sequence_type: SequenceType,
    touch_number: int,
    campaign_start: Optional[datetime] = None,
) -> Optional[datetime]:
    """Calculate when a specific touch should wake.
    
    Parameters
    ----------
    sequence_type : SequenceType
        Which sequence
    touch_number : int
        Which touch (1-indexed)
    campaign_start : Optional[datetime]
        When campaign started (default: now)
    
    Returns
    -------
    Optional[datetime]
        UTC wake time, or None if touch not in sequence
    """
    from datetime import datetime, timezone
    
    if campaign_start is None:
        campaign_start = datetime.now(timezone.utc)
    
    touch_def = get_touch_definition(sequence_type, touch_number)
    if touch_def is None:
        return None
    
    # Calculate cumulative delay
    seq_def = get_sequence_definition(sequence_type)
    cumulative_days = 0
    for touch in seq_def.touches:
        if touch.touch_number <= touch_number:
            cumulative_days += touch.delay_days
    
    return campaign_start + timedelta(days=cumulative_days)


__all__ = [
    "SequenceType",
    "TouchStrategy",
    "TouchDefinition",
    "SequenceDefinition",
    "STANDARD_3_TOUCH",
    "EXECUTIVE_3_TOUCH",
    "RECRUITER_COMPACT",
    "SEQUENCE_REGISTRY",
    "get_sequence_definition",
    "get_touch_definition",
    "list_sequence_types",
    "calculate_touch_wake_time",
]
