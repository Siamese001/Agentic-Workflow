"""apps_lic.signals.trigger_wake_mapper — W3.P2

Trigger → Wake Mapping

Maps detected signals to wake scheduler requests with:
- Signal confidence → Trigger confidence
- Signal type → Cadence boost (or not)
- Signal priority → Wake priority

Integrates signals with the touch scheduler for resurfacing.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Optional

from apps_lic.signals.types import ResurfacingSignal, SignalType, SignalStrength
from apps_lic.coordination.touch_scheduler import (
    ScheduleTouchRequest,
    TouchCadenceCalculator,
)


@dataclass(frozen=True)
class WakeMappingDecision:
    """Decision for mapping a signal to a wake event.
    
    Fields
    ------
    should_wake : bool
        Whether to schedule a wake
    wake_at : Optional[datetime]
        When to wake (if should_wake)
    priority : int
        Wake priority (lower = higher priority)
    cadence_boost_hours : int
        Hours to reduce from standard cadence
    trigger_confidence : float
        Confidence score (0.0-1.0)
    reason : str
        Human-readable reason for decision
    """
    
    should_wake: bool
    wake_at: Optional[datetime]
    priority: int
    cadence_boost_hours: int
    trigger_confidence: float
    reason: str


class TriggerWakeMapper:
    """Maps signals to wake scheduler requests.
    
    Implements the W3.P2 mapping logic:
    - Strong funding/competitive signals → immediate wake with boost
    - Moderate hiring signals → standard cadence, slight boost
    - Weak/engagement signals → standard cadence, no boost
    - Multiple signals → highest priority wins
    """
    
    # Signal type → base priority (lower = higher priority)
    SIGNAL_PRIORITY: dict[SignalType, int] = {
        SignalType.FUNDING_ROUND: 1,
        SignalType.ACQUISITION: 1,
        SignalType.IPO_ANNOUNCEMENT: 2,
        SignalType.EXEC_ROLE_OPEN: 3,
        SignalType.HIRING_SURGE: 4,
        SignalType.TEAM_EXPANSION: 5,
        SignalType.COMPETITOR_LAUNCH: 6,
        SignalType.MARKET_SHIFT: 7,
        SignalType.REGULATORY_CHANGE: 8,
        SignalType.PROFILE_VIEW: 10,
        SignalType.CONTENT_ENGAGEMENT: 11,
    }
    
    # Signal type → default cadence boost (hours)
    CADENCE_BOOST: dict[SignalType, int] = {
        SignalType.FUNDING_ROUND: 48,      # 2 days sooner
        SignalType.ACQUISITION: 48,
        SignalType.EXEC_ROLE_OPEN: 24,   # 1 day sooner
        SignalType.HIRING_SURGE: 24,
        SignalType.COMPETITOR_LAUNCH: 36,  # 1.5 days sooner
    }
    
    # Minimum confidence threshold for waking
    MIN_WAKE_CONFIDENCE: float = 0.5
    
    def __init__(self) -> None:
        self._cadence_calc = TouchCadenceCalculator()
    
    def map_signal_to_wake(
        self,
        signal: ResurfacingSignal,
        prior_touch_sent_at: Optional[datetime] = None,
        touch_sequence: int = 1,
        standard_cadence_days: int = 7,
    ) -> WakeMappingDecision:
        """Map a single signal to wake decision.
        
        Parameters
        ----------
        signal : ResurfacingSignal
            Detected signal
        prior_touch_sent_at : Optional[datetime]
            When prior touch was sent
        touch_sequence : int
            Position in sequence (1-indexed)
        standard_cadence_days : int
            Standard delay between touches
        
        Returns
        -------
        WakeMappingDecision
            Wake scheduling decision
        """
        # Get signal confidence
        confidence = signal._strength_to_confidence()
        
        # Check minimum threshold
        if confidence < self.MIN_WAKE_CONFIDENCE:
            return WakeMappingDecision(
                should_wake=False,
                wake_at=None,
                priority=99,
                cadence_boost_hours=0,
                trigger_confidence=confidence,
                reason=f"Signal confidence {confidence:.2f} below threshold {self.MIN_WAKE_CONFIDENCE}",
            )
        
        # Get priority for this signal type
        priority = self.SIGNAL_PRIORITY.get(signal.signal_type, 50)
        
        # Get cadence boost
        base_boost = self.CADENCE_BOOST.get(signal.signal_type, 0)
        
        # Strong signals get extra boost
        if signal.strength == SignalStrength.STRONG:
            boost_hours = base_boost + 12  # Additional 12 hours
        elif signal.strength == SignalStrength.MODERATE:
            boost_hours = base_boost
        else:
            boost_hours = 0
        
        # Calculate wake time
        if prior_touch_sent_at:
            # Normal cadence minus boost
            standard_wake = prior_touch_sent_at + timedelta(days=standard_cadence_days)
            wake_at = standard_wake - timedelta(hours=boost_hours)
            
            # Ensure not in the past
            now = datetime.now(timezone.utc)
            if wake_at < now:
                wake_at = now + timedelta(hours=1)
        else:
            # First touch - schedule soon
            wake_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        return WakeMappingDecision(
            should_wake=True,
            wake_at=wake_at,
            priority=priority,
            cadence_boost_hours=boost_hours,
            trigger_confidence=confidence,
            reason=f"{signal.signal_type.value} ({signal.strength.value}) → wake with {boost_hours}h boost",
        )
    
    def create_schedule_request(
        self,
        signal: ResurfacingSignal,
        touch_id: str,
        recipient_hash: str,
        campaign_id: str,
        touch_sequence: int,
        prior_touch_sent_at: Optional[datetime] = None,
        context_carry_forward: Optional[dict] = None,
        hitl_review_required: bool = False,
    ) -> Optional[ScheduleTouchRequest]:
        """Create a schedule request from signal.
        
        Parameters
        ----------
        signal : ResurfacingSignal
            Detected signal
        touch_id : str
            Touch identifier
        recipient_hash : str
            Hashed recipient
        campaign_id : str
            Campaign ID
        touch_sequence : int
            Position in sequence
        prior_touch_sent_at : Optional[datetime]
            When prior touch sent
        context_carry_forward : Optional[dict]
            Context to propagate
        hitl_review_required : bool
            Whether HITL review needed
        
        Returns
        -------
        Optional[ScheduleTouchRequest]
            Schedule request if signal warrants wake
        """
        decision = self.map_signal_to_wake(
            signal=signal,
            prior_touch_sent_at=prior_touch_sent_at,
            touch_sequence=touch_sequence,
        )
        
        if not decision.should_wake or not decision.wake_at:
            return None
        
        return ScheduleTouchRequest(
            touch_id=touch_id,
            recipient_hash=recipient_hash,
            campaign_id=campaign_id,
            touch_sequence=touch_sequence,
            wake_at=decision.wake_at,
            context_carry_forward=context_carry_forward or {},
            trigger_signal=signal.signal_type.value,
            trigger_confidence=decision.trigger_confidence,
            hitl_review_required=hitl_review_required,
        )
    
    def select_best_signal_for_wake(
        self,
        signals: list[ResurfacingSignal],
    ) -> Optional[ResurfacingSignal]:
        """Select the best signal for wake scheduling.
        
        Prioritizes by:
        1. Signal type priority (funding > hiring > engagement)
        2. Signal strength (strong > moderate > weak)
        3. Recency (newer > older)
        
        Parameters
        ----------
        signals : list[ResurfacingSignal]
            Available signals
        
        Returns
        -------
        Optional[ResurfacingSignal]
            Best signal for wake, or None if no suitable signals
        """
        if not signals:
            return None
        
        # Filter to signals above confidence threshold
        valid_signals = [
            s for s in signals
            if s._strength_to_confidence() >= self.MIN_WAKE_CONFIDENCE
        ]
        
        if not valid_signals:
            return None
        
        # Score each signal
        def score_signal(s: ResurfacingSignal) -> tuple:
            priority = self.SIGNAL_PRIORITY.get(s.signal_type, 50)
            
            strength_order = {
                SignalStrength.STRONG: 3,
                SignalStrength.MODERATE: 2,
                SignalStrength.WEAK: 1,
            }
            strength_score = strength_order.get(s.strength, 0)
            
            # Return tuple for sorting (lower priority first, higher strength first, newer first)
            return (priority, -strength_score, s.detected_at)
        
        scored = [(s, score_signal(s)) for s in valid_signals]
        scored.sort(key=lambda x: x[1])
        
        return scored[0][0]
    
    def calculate_boosted_cadence(
        self,
        base_cadence_days: int,
        signal: ResurfacingSignal,
    ) -> int:
        """Calculate cadence days with signal boost applied.
        
        Parameters
        ----------
        base_cadence_days : int
            Standard days between touches
        signal : ResurfacingSignal
            Detected signal
        
        Returns
        -------
        int
            Boosted cadence days (minimum 1)
        """
        base_boost_hours = self.CADENCE_BOOST.get(signal.signal_type, 0)
        
        if signal.strength == SignalStrength.STRONG:
            boost_hours = base_boost_hours + 12
        else:
            boost_hours = base_boost_hours
        
        # Convert boost to days
        boost_days = boost_hours / 24
        boosted = max(1, base_cadence_days - boost_days)
        
        return int(boosted)


__all__ = [
    "TriggerWakeMapper",
    "WakeMappingDecision",
]
