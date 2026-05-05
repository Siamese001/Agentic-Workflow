"""Coordination-Touch State Integration for apps_lic.

Wave 2, Phase 3 of apps-lic-infra-prerequisites-unblock-p2p3

This module provides the integration layer between coordination fabric
scheduled wake and L4 touch state persistence.

App: apps_lic
Layer: Integration (apps_lic/coordination/)

Dependencies:
    - Touch Scheduler (apps_lic/coordination/touch_scheduler.py)
    - Wake Handler (apps_lic/coordination/wake_handler.py)
    - Touch State Registration (apps_lic/state/touch_state_registration.py)
    - UWG (agentic_core/L4_state/uwg/)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional


# -----------------------------------------------------------------------------
# Integration Configuration
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class CoordinationTouchIntegrationConfig:
    """Configuration for coordination-touch integration."""
    
    # Queue settings
    wake_queue_key: str = "coordination:apps_lic:wake_queue"
    poll_interval_seconds: float = 60.0
    max_touches_per_poll: int = 100
    
    # Lock settings
    lock_ttl_seconds: int = 300
    
    # Retry settings
    max_retry_count: int = 3
    base_backoff_hours: int = 2
    
    # HITL settings
    hitl_enabled: bool = True
    default_hitl_threshold: float = 0.7
    
    # State sync settings
    sync_touch_state_on_wake: bool = True
    sync_touch_state_on_send: bool = True


# -----------------------------------------------------------------------------
# Integration State
# -----------------------------------------------------------------------------

class CoordinationTouchIntegration:
    """Integration manager for coordination fabric and touch state.
    
    This class wires together:
    - TouchScheduler (coordination fabric)
    - WakeHandler (wake processing)
    - TouchStateUWGAdapter (L4 persistence)
    
    Provides the spine initialization point for apps_lic multi-touch
    coordination.
    
    Parameters
    ----------
    config : CoordinationTouchIntegrationConfig
        Integration configuration
    scheduler : TouchScheduler
        Configured scheduler instance
    state_adapter : TouchStateUWGAdapter
        UWG adapter for touch state
    """
    
    def __init__(
        self,
        config: CoordinationTouchIntegrationConfig,
        scheduler: Any,  # TouchScheduler
        state_adapter: Any,  # TouchStateUWGAdapter
        touch_sender: Optional[Any] = None,
        hitl_client: Optional[Any] = None,
    ):
        self._config = config
        self._scheduler = scheduler
        self._state_adapter = state_adapter
        
        # Create wake handler
        from apps_lic.coordination.wake_handler import WakeHandler
        self._wake_handler = WakeHandler(
            scheduler=scheduler,
            state_adapter=state_adapter,
            touch_sender=touch_sender,
            hitl_client=hitl_client,
        )
        
        # Create processor
        from apps_lic.coordination.wake_handler import WakeProcessor
        self._processor = WakeProcessor(
            scheduler=scheduler,
            handler=self._wake_handler,
            poll_interval_seconds=config.poll_interval_seconds,
        )
    
    def schedule_new_touch(
        self,
        touch_id: str,
        recipient_hash: str,
        campaign_id: str,
        touch_sequence: int,
        wake_at: datetime,
        context_carry_forward: Optional[dict] = None,
        trigger_signal: Optional[str] = None,
        trigger_confidence: float = 0.0,
        hitl_review_required: bool = False,
    ) -> tuple[bool, Optional[str]]:
        """Schedule a new touch with full state integration.
        
        This method:
        1. Schedules in coordination fabric
        2. Creates initial state in L4 touch state table
        
        Parameters
        ----------
        touch_id : str
            Unique touch identifier
        recipient_hash : str
            Hashed recipient identifier
        campaign_id : str
            Parent campaign
        touch_sequence : int
            Position in sequence
        wake_at : datetime
            When to wake (UTC)
        context_carry_forward : Optional[dict]
            Context to carry forward
        trigger_signal : Optional[str]
            What triggered this touch
        trigger_confidence : float
            Confidence in trigger
        hitl_review_required : bool
            Whether HITL review needed
        
        Returns
        -------
        tuple[bool, Optional[str]]
            (success, error_message)
        """
        from apps_lic.coordination.touch_scheduler import ScheduleTouchRequest
        from agentic_core.L4_state.uwg.touch_state_writer import TouchStateWriteRequest
        
        # Step 1: Schedule in coordination fabric
        schedule_request = ScheduleTouchRequest(
            touch_id=touch_id,
            recipient_hash=recipient_hash,
            campaign_id=campaign_id,
            touch_sequence=touch_sequence,
            wake_at=wake_at,
            context_carry_forward=context_carry_forward or {},
            trigger_signal=trigger_signal,
            trigger_confidence=trigger_confidence,
            hitl_review_required=hitl_review_required,
        )
        
        receipt, failure = self._scheduler.schedule_touch(schedule_request)
        
        if receipt is None:
            return False, f"Scheduling failed: {failure.reason if failure else 'unknown'}"
        
        # Step 2: Create initial state in L4
        if self._config.sync_touch_state_on_wake:
            state_request = TouchStateWriteRequest(
                touch_id=touch_id,
                recipient_hash=recipient_hash,
                campaign_id=campaign_id,
                touch_sequence=touch_sequence,
                touch_state="scheduled",
                next_scheduled_wake=wake_at,
                context_carry_forward=context_carry_forward or {},
                trigger_signal=trigger_signal,
                trigger_confidence=trigger_confidence,
                hitl_review_required=hitl_review_required,
            )
            
            state_receipt, state_blocked = self._state_adapter.write_touch_state(state_request)
            
            if state_receipt is None:
                # Rollback: unschedule from coordination fabric
                self._scheduler.unschedule_touch(touch_id)
                return False, f"State creation failed: {state_blocked.blocked_reason if state_blocked else 'unknown'}"
        
        return True, None
    
    def process_wake_queue(self, limit: Optional[int] = None) -> list[Any]:
        """Process pending wake queue.
        
        Polls coordination fabric for due touches and processes them.
        
        Parameters
        ----------
        limit : Optional[int]
            Max touches to process (default: config.max_touches_per_poll)
        
        Returns
        -------
        list[WakeResult]
            Results of processed touches
        """
        if limit is None:
            limit = self._config.max_touches_per_poll
        
        return self._processor.poll_once(limit=limit)
    
    def get_queue_status(self) -> dict[str, Any]:
        """Get current wake queue status.
        
        Returns
        -------
        dict
            Queue statistics and status
        """
        now = datetime.now(timezone.utc).timestamp()
        redis_client = self._scheduler._fabric._redis
        
        # Get queue stats
        total_queued = redis_client.zcard(self._config.wake_queue_key)
        due_count = redis_client.zcount(
            self._config.wake_queue_key,
            0,
            now,
        )
        
        # Get next wake
        next_wake = None
        next_members = redis_client.zrange(
            self._config.wake_queue_key,
            0,
            0,
            withscores=True,
        )
        if next_members:
            member, score = next_members[0]
            next_wake = datetime.fromtimestamp(score, tz=timezone.utc).isoformat()
        
        return {
            "total_queued": total_queued,
            "due_now": due_count,
            "next_wake": next_wake,
            "queue_key": self._config.wake_queue_key,
            "poll_interval_seconds": self._config.poll_interval_seconds,
        }
    
    def cancel_touch(self, touch_id: str) -> bool:
        """Cancel a scheduled touch.
        
        Removes from coordination fabric and updates state.
        
        Parameters
        ----------
        touch_id : str
            Touch to cancel
        
        Returns
        -------
        bool
            True if cancelled successfully
        """
        # Unschedule from coordination fabric
        unscheduled = self._scheduler.unschedule_touch(touch_id)
        
        # Update state (best effort)
        try:
            from agentic_core.L4_state.uwg.touch_state_writer import TouchStateWriteRequest
            
            # Note: This is a partial update - in production, would fetch
            # current state first and preserve other fields
            state_request = TouchStateWriteRequest(
                touch_id=touch_id,
                recipient_hash="",  # Would be populated
                campaign_id="",      # Would be populated
                touch_sequence=0,    # Would be populated
                touch_state="cancelled",
            )
            self._state_adapter.write_touch_state(state_request)
        except Exception:
            pass  # Best effort state update
        
        return unscheduled


# -----------------------------------------------------------------------------
# Spine Integration
# -----------------------------------------------------------------------------

class CoordinationTouchSpineIntegration:
    """Spine integration point for coordination-touch wiring.
    
    This class provides the standard spine initialization pattern,
    ensuring all components are wired correctly on startup.
    """
    
    @staticmethod
    def initialize(
        touch_sender: Optional[Any] = None,
        hitl_client: Optional[Any] = None,
        config: Optional[CoordinationTouchIntegrationConfig] = None,
    ) -> dict[str, Any]:
        """Initialize coordination-touch integration for apps_lic spine.
        
        This method should be called during apps_lic spine startup,
        after touch state registration but before accepting campaigns.
        
        Parameters
        ----------
        touch_sender : Optional[Callable]
            Callback for sending touch messages
        hitl_client : Optional[Any]
            HITL client for escalations
        config : Optional[CoordinationTouchIntegrationConfig]
            Integration config (uses defaults if None)
        
        Returns
        -------
        dict[str, Any]
            {
                "status": "success|error",
                "integration": CoordinationTouchIntegration|None,
                "error": str|None,
            }
        """
        try:
            from apps_lic.coordination.touch_scheduler import get_touch_scheduler
            from agentic_core.L4_state.uwg.touch_state_writer import TouchStateUWGAdapter
            from agentic_core.L4_state.uwg.durable_write_gateway import get_gateway
            
            cfg = config or CoordinationTouchIntegrationConfig()
            
            # Get scheduler
            scheduler = get_touch_scheduler()
            
            # Get state adapter
            gateway = get_gateway()
            state_adapter = TouchStateUWGAdapter(gateway)
            
            # Create integration
            integration = CoordinationTouchIntegration(
                config=cfg,
                scheduler=scheduler,
                state_adapter=state_adapter,
                touch_sender=touch_sender,
                hitl_client=hitl_client,
            )
            
            return {
                "status": "success",
                "integration": integration,
                "error": None,
            }
        
        except Exception as e:
            return {
                "status": "error",
                "integration": None,
                "error": str(e),
            }


# -----------------------------------------------------------------------------
# Convenience Entry Point
# -----------------------------------------------------------------------------

def initialize_coordination_touch_integration(
    touch_sender: Optional[Any] = None,
    hitl_client: Optional[Any] = None,
) -> Optional[CoordinationTouchIntegration]:
    """One-shot initialization of coordination-touch integration.
    
    Primary entry point for apps_lic spine initialization.
    
    Parameters
    ----------
    touch_sender : Optional[Callable]
        Callback for sending touch messages
    hitl_client : Optional[Any]
        HITL client for escalations
    
    Returns
    -------
    Optional[CoordinationTouchIntegration]
        Integration instance if successful, None if failed
    
    Example
    -------
    >>> from apps_lic.coordination.touch_state_integration import (
    ...     initialize_coordination_touch_integration
    ... )
    >>> integration = initialize_coordination_touch_integration(
    ...     touch_sender=my_sender,
    ...     hitl_client=my_hitl,
    ... )
    >>> if integration:
    ...     print("Coordination ready")
    """
    result = CoordinationTouchSpineIntegration.initialize(
        touch_sender=touch_sender,
        hitl_client=hitl_client,
    )
    return result.get("integration")


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "CoordinationTouchIntegrationConfig",
    "CoordinationTouchIntegration",
    "CoordinationTouchSpineIntegration",
    "initialize_coordination_touch_integration",
]
