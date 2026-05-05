"""Touch Scheduler Service for apps_lic — Coordination Fabric Integration.

Wave 2, Phase 1 of apps-lic-infra-prerequisites-unblock-p2p3

This module provides scheduled wake functionality for multi-touch sequences,
integrating with the Redis coordination fabric for reliable scheduling.

App: apps_lic
Layer: Coordination Fabric (agentic_core/cache/coordination/)

Dependencies:
    - Redis Coordination Fabric (agentic_core/cache/core/redis_coordination_fabric.py)
    - Touch State Schema (agentic_core/L4_state/schemas/apps_lic_touch_state.sql)
    - Touch State Writer (agentic_core/L4_state/uwg/touch_state_writer.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Callable
import json
import uuid


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

DEFAULT_WAKE_QUEUE_KEY = "coordination:apps_lic:wake_queue"
DEFAULT_TOUCH_LOCK_PREFIX = "coordination:apps_lic:touch_lock:"
DEFAULT_LOCK_TTL_SECONDS = 300  # 5 minutes

# Cadence defaults (days between touches)
DEFAULT_CADENCE_DAYS = [7, 14, 21]  # 1 week, 2 weeks, 3 weeks


# -----------------------------------------------------------------------------
# Scheduler Request / Response
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class ScheduleTouchRequest:
    """Request to schedule a touch for future wake.
    
    Fields
    ------
    touch_id : str
        Unique touch identifier
    recipient_hash : str
        Hashed recipient identifier (PII-safe)
    campaign_id : str
        Parent campaign
    touch_sequence : int
        Position in sequence (1, 2, 3...)
    wake_at : datetime
        When to wake this touch (UTC)
    context_carry_forward : dict
        Context to pass to next touch
    trigger_signal : Optional[str]
        What triggered scheduling (resurfacing signal)
    trigger_confidence : float
        Confidence in trigger (0.0-1.0)
    hitl_review_required : bool
        Whether HITL review needed before send
    retry_count : int
        Number of previous scheduling attempts
    """
    
    touch_id: str
    recipient_hash: str
    campaign_id: str
    touch_sequence: int
    wake_at: datetime
    context_carry_forward: dict[str, Any] = field(default_factory=dict)
    trigger_signal: Optional[str] = None
    trigger_confidence: float = 0.0
    hitl_review_required: bool = False
    retry_count: int = 0
    
    def __post_init__(self):
        if self.wake_at.tzinfo is None:
            raise ValueError("wake_at must be timezone-aware (UTC)")


@dataclass(frozen=True)
class ScheduleTouchReceipt:
    """Receipt confirming touch was scheduled.
    
    Fields
    ------
    touch_id : str
        The touch that was scheduled
    scheduled_at : datetime
        When scheduling occurred (UTC)
    queue_position : int
        Approximate position in wake queue
    wake_at : datetime
        Confirmed wake time
    coordination_key : str
        Redis key where scheduled
    """
    
    touch_id: str
    scheduled_at: datetime
    queue_position: int
    wake_at: datetime
    coordination_key: str


@dataclass(frozen=True)
class ScheduleTouchFailure:
    """Failure when scheduling touch.
    
    Fields
    ------
    touch_id : str
        The touch that failed to schedule
    failed_at : datetime
        When failure occurred
    reason : str
        Why scheduling failed
    retryable : bool
        Whether retry might succeed
    """
    
    touch_id: str
    failed_at: datetime
    reason: str
    retryable: bool


# -----------------------------------------------------------------------------
# Cadence Calculator
# -----------------------------------------------------------------------------

class TouchCadenceCalculator:
    """Calculate optimal wake timing for multi-touch sequences.
    
    Implements configurable cadence strategies with backoff and
    signal-aware adjustments.
    """
    
    def __init__(
        self,
        base_cadence_days: list[int] = None,
        signal_boost_threshold: float = 0.8,
        signal_boost_hours: int = 24,
        max_sequence_length: int = 5,
    ):
        self.base_cadence_days = base_cadence_days or DEFAULT_CADENCE_DAYS
        self.signal_boost_threshold = signal_boost_threshold
        self.signal_boost_hours = signal_boost_hours
        self.max_sequence_length = max_sequence_length
    
    def calculate_next_wake(
        self,
        prior_touch_sent_at: Optional[datetime],
        touch_sequence: int,
        trigger_confidence: float = 0.0,
        trigger_signal: Optional[str] = None,
    ) -> datetime:
        """Calculate when to wake the next touch in sequence.
        
        Parameters
        ----------
        prior_touch_sent_at : Optional[datetime]
            When prior touch was sent (None for first touch)
        touch_sequence : int
            Position in sequence (1-indexed)
        trigger_confidence : float
            Confidence in resurfacing signal
        trigger_signal : Optional[str]
            Type of signal (e.g., "hiring_signal", "funding_announcement")
        
        Returns
        -------
        datetime
            UTC datetime for next wake
        """
        now = datetime.now(timezone.utc)
        
        # Base cadence from sequence position
        cadence_index = min(touch_sequence - 1, len(self.base_cadence_days) - 1)
        base_delay_days = self.base_cadence_days[cadence_index]
        
        # Calculate base wake time
        if prior_touch_sent_at:
            base_wake = prior_touch_sent_at + timedelta(days=base_delay_days)
        else:
            # First touch - schedule soon
            base_wake = now + timedelta(hours=1)
        
        # Signal boost: high-confidence triggers wake sooner
        if trigger_confidence >= self.signal_boost_threshold and trigger_signal:
            # Boost by reducing delay
            boost = timedelta(hours=self.signal_boost_hours)
            base_wake = max(now + timedelta(hours=1), base_wake - boost)
        
        return base_wake
    
    def calculate_sequence_wakes(
        self,
        campaign_start: datetime,
        sequence_length: int,
        signal_profile: Optional[dict[str, Any]] = None,
    ) -> list[datetime]:
        """Calculate wake times for an entire touch sequence.
        
        Parameters
        ----------
        campaign_start : datetime
            When campaign begins (UTC)
        sequence_length : int
            How many touches in sequence
        signal_profile : Optional[dict]
            Signal confidence per touch position
        
        Returns
        -------
        list[datetime]
            Wake time for each touch in sequence
        """
        signal_profile = signal_profile or {}
        wakes = []
        prior_sent = None
        
        for i in range(1, min(sequence_length, self.max_sequence_length) + 1):
            confidence = signal_profile.get(i, 0.0)
            signal = signal_profile.get(f"signal_{i}")
            
            wake = self.calculate_next_wake(
                prior_touch_sent_at=prior_sent,
                touch_sequence=i,
                trigger_confidence=confidence,
                trigger_signal=signal,
            )
            wakes.append(wake)
            # Simulate that each touch gets sent shortly after wake
            prior_sent = wake + timedelta(hours=2)
        
        return wakes


# -----------------------------------------------------------------------------
# Touch Scheduler
# -----------------------------------------------------------------------------

class TouchScheduler:
    """Scheduler for multi-touch wake coordination.
    
    Integrates with Redis coordination fabric to provide:
    - Sorted set wake queue (wake_at as score)
    - Per-touch locking to prevent double-processing
    - Retry with exponential backoff
    
    Parameters
    ----------
    fabric : RedisCoordinationFabric
        The coordination fabric to use
    queue_key : str
        Redis key for wake queue
    lock_prefix : str
        Prefix for touch lock keys
    lock_ttl_seconds : int
        Lock TTL to prevent stuck locks
    """
    
    def __init__(
        self,
        fabric: Any,  # RedisCoordinationFabric
        queue_key: str = DEFAULT_WAKE_QUEUE_KEY,
        lock_prefix: str = DEFAULT_TOUCH_LOCK_PREFIX,
        lock_ttl_seconds: int = DEFAULT_LOCK_TTL_SECONDS,
    ):
        self._fabric = fabric
        self._queue_key = queue_key
        self._lock_prefix = lock_prefix
        self._lock_ttl_seconds = lock_ttl_seconds
        self._cadence_calc = TouchCadenceCalculator()
    
    def schedule_touch(
        self,
        request: ScheduleTouchRequest,
    ) -> tuple[Optional[ScheduleTouchReceipt], Optional[ScheduleTouchFailure]]:
        """Schedule a touch for future wake.
        
        Parameters
        ----------
        request : ScheduleTouchRequest
            Scheduling request
        
        Returns
        -------
        tuple[Optional[ScheduleTouchReceipt], Optional[ScheduleTouchFailure]]
            (receipt, failure) — exactly one is non-None
        """
        try:
            # Serialize touch data for queue
            touch_data = {
                "touch_id": request.touch_id,
                "recipient_hash": request.recipient_hash,
                "campaign_id": request.campaign_id,
                "touch_sequence": request.touch_sequence,
                "context_carry_forward": request.context_carry_forward,
                "trigger_signal": request.trigger_signal,
                "trigger_confidence": request.trigger_confidence,
                "hitl_review_required": request.hitl_review_required,
                "retry_count": request.retry_count,
            }
            
            # Add to sorted set with wake_at timestamp as score
            score = request.wake_at.timestamp()
            member = json.dumps(touch_data)
            
            # Redis ZADD
            redis_client = self._fabric._redis
            redis_client.zadd(self._queue_key, {member: score})
            
            # Get approximate queue position
            rank = redis_client.zrank(self._queue_key, member)
            
            return (
                ScheduleTouchReceipt(
                    touch_id=request.touch_id,
                    scheduled_at=datetime.now(timezone.utc),
                    queue_position=rank + 1 if rank is not None else 0,
                    wake_at=request.wake_at,
                    coordination_key=self._queue_key,
                ),
                None,
            )
        except Exception as e:
            return (
                None,
                ScheduleTouchFailure(
                    touch_id=request.touch_id,
                    failed_at=datetime.now(timezone.utc),
                    reason=str(e),
                    retryable=True,
                ),
            )
    
    def unschedule_touch(self, touch_id: str) -> bool:
        """Remove a touch from the wake queue.
        
        Used when touch is cancelled or converted early.
        
        Parameters
        ----------
        touch_id : str
            Touch to unschedule
        
        Returns
        -------
        bool
            True if touch was found and removed
        """
        try:
            # Find and remove by touch_id pattern
            redis_client = self._fabric._redis
            # Get all members
            members = redis_client.zrange(self._queue_key, 0, -1)
            for member in members:
                data = json.loads(member)
                if data.get("touch_id") == touch_id:
                    redis_client.zrem(self._queue_key, member)
                    return True
            return False
        except Exception:
            return False
    
    def acquire_touch_lock(self, touch_id: str) -> bool:
        """Acquire distributed lock for processing a touch.
        
        Prevents duplicate processing when multiple workers wake
        the same touch.
        
        Parameters
        ----------
        touch_id : str
            Touch to lock
        
        Returns
        -------
        bool
            True if lock acquired
        """
        lock_key = f"{self._lock_prefix}{touch_id}"
        redis_client = self._fabric._redis
        
        # SET NX EX - set if not exists with expiry
        acquired = redis_client.set(
            lock_key,
            "1",
            nx=True,  # Only if not exists
            ex=self._lock_ttl_seconds,
        )
        return acquired is not None
    
    def release_touch_lock(self, touch_id: str) -> bool:
        """Release distributed lock for a touch.
        
        Parameters
        ----------
        touch_id : str
            Touch to unlock
        
        Returns
        -------
        bool
            True if lock released
        """
        lock_key = f"{self._lock_prefix}{touch_id}"
        redis_client = self._fabric._redis
        return redis_client.delete(lock_key) > 0
    
    def get_due_touches(
        self,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get touches due for wake (wake_at <= now).
        
        Parameters
        ----------
        limit : int
            Maximum touches to return
        
        Returns
        -------
        list[dict]
            Touch data dicts ready for wake
        """
        now = datetime.now(timezone.utc).timestamp()
        redis_client = self._fabric._redis
        
        # ZRANGEBYSCORE to get due touches
        members = redis_client.zrangebyscore(
            self._queue_key,
            0,  # min score
            now,  # max score (now)
            start=0,
            num=limit,
        )
        
        touches = []
        for member in members:
            try:
                data = json.loads(member)
                touches.append(data)
            except json.JSONDecodeError:
                continue
        
        return touches
    
    def calculate_and_schedule_sequence(
        self,
        campaign_id: str,
        recipient_hash: str,
        sequence_length: int = 3,
        campaign_start: Optional[datetime] = None,
        signal_profile: Optional[dict[str, Any]] = None,
    ) -> list[tuple[Optional[ScheduleTouchReceipt], Optional[ScheduleTouchFailure]]]:
        """Calculate and schedule a full touch sequence.
        
        Convenience method for scheduling multiple touches at once.
        
        Parameters
        ----------
        campaign_id : str
            Parent campaign
        recipient_hash : str
            Recipient identifier
        sequence_length : int
            Number of touches to schedule
        campaign_start : Optional[datetime]
            When campaign starts (default: now)
        signal_profile : Optional[dict]
            Signal confidence per position
        
        Returns
        -------
        list[tuple[receipt, failure]]
            Results for each touch in sequence
        """
        if campaign_start is None:
            campaign_start = datetime.now(timezone.utc)
        
        # Calculate wake times
        wake_times = self._cadence_calc.calculate_sequence_wakes(
            campaign_start=campaign_start,
            sequence_length=sequence_length,
            signal_profile=signal_profile,
        )
        
        results = []
        for i, wake_at in enumerate(wake_times, 1):
            touch_id = f"{campaign_id}:{recipient_hash}:{i}:{uuid.uuid4().hex[:8]}"
            
            request = ScheduleTouchRequest(
                touch_id=touch_id,
                recipient_hash=recipient_hash,
                campaign_id=campaign_id,
                touch_sequence=i,
                wake_at=wake_at,
                trigger_signal=signal_profile.get(f"signal_{i}"),
                trigger_confidence=signal_profile.get(i, 0.0),
            )
            
            result = self.schedule_touch(request)
            results.append(result)
        
        return results


# -----------------------------------------------------------------------------
# Factory
# -----------------------------------------------------------------------------

def get_touch_scheduler(
    fabric: Optional[Any] = None,
) -> TouchScheduler:
    """Get configured TouchScheduler instance.
    
    Parameters
    ----------
    fabric : Optional[RedisCoordinationFabric]
        Coordination fabric. If None, uses default fabric.
    
    Returns
    -------
    TouchScheduler
        Configured scheduler instance
    """
    if fabric is None:
        from agentic_core.cache.core.redis_coordination_fabric import get_fabric
        fabric = get_fabric()
    
    return TouchScheduler(fabric=fabric)


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "ScheduleTouchRequest",
    "ScheduleTouchReceipt",
    "ScheduleTouchFailure",
    "TouchCadenceCalculator",
    "TouchScheduler",
    "get_touch_scheduler",
    "DEFAULT_WAKE_QUEUE_KEY",
    "DEFAULT_CADENCE_DAYS",
]
