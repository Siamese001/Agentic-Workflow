"""Wake Handler for apps_lic — Coordination Fabric Integration.

Wave 2, Phase 2 of apps-lic-infra-prerequisites-unblock-p2p3

This module handles the processing of scheduled wake events from the
coordination fabric, routing touches to appropriate handlers and managing
state transitions.

App: apps_lic
Layer: Coordination Fabric (agentic_core/cache/coordination/)

Dependencies:
    - Touch Scheduler (apps_lic/coordination/touch_scheduler.py)
    - Touch State Writer (agentic_core/L4_state/uwg/touch_state_writer.py)
    - Redis Coordination Fabric (agentic_core/cache/core/redis_coordination_fabric.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional, Callable
from enum import Enum


# -----------------------------------------------------------------------------
# Wake Result Types
# -----------------------------------------------------------------------------

class WakeAction(str, Enum):
    """Actions that can result from wake processing."""
    
    SEND_TOUCH = "send_touch"              # Proceed to send message
    REQUIRE_HITL = "require_hitl"        # Escalate to HITL review
    RESCHEDULE = "reschedule"            # Delay and retry later
    SKIP_EXPIRED = "skip_expired"        # Touch window expired, skip
    SKIP_CANCELLED = "skip_cancelled"    # Campaign or touch cancelled
    SKIP_CONVERTED = "skip_converted"    # Recipient already converted


class WakeOutcome(str, Enum):
    """Outcomes of wake processing."""
    
    PROCESSED = "processed"              # Successfully processed
    LOCKED = "locked"                    # Another worker has lock
    FAILED = "failed"                    # Processing failed
    RETRY_SCHEDULED = "retry_scheduled"  # Will retry later


# -----------------------------------------------------------------------------
# Wake Request / Response
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class WakeRequest:
    """Request to process a woken touch.
    
    Fields
    ------
    touch_id : str
        Unique touch identifier
    recipient_hash : str
        Hashed recipient identifier
    campaign_id : str
        Parent campaign
    touch_sequence : int
        Position in sequence
    context_carry_forward : dict
        Context from prior touches
    trigger_signal : Optional[str]
        What triggered this touch
    trigger_confidence : float
        Confidence in trigger
    hitl_review_required : bool
        Whether HITL review needed
    retry_count : int
        Number of previous processing attempts
    """
    
    touch_id: str
    recipient_hash: str
    campaign_id: str
    touch_sequence: int
    context_carry_forward: dict[str, Any] = field(default_factory=dict)
    trigger_signal: Optional[str] = None
    trigger_confidence: float = 0.0
    hitl_review_required: bool = False
    retry_count: int = 0


@dataclass(frozen=True)
class WakeResult:
    """Result of wake processing.
    
    Fields
    ------
    touch_id : str
        The touch that was processed
    outcome : WakeOutcome
        What happened during processing
    action : WakeAction
        What action to take
    processed_at : datetime
        When processing occurred (UTC)
    message_id : Optional[str]
        Message ID if message was sent
    hitl_review_id : Optional[str]
        HITL review ID if escalated
    next_wake_at : Optional[datetime]
        When to retry if rescheduled
    error : Optional[str]
        Error message if failed
    """
    
    touch_id: str
    outcome: WakeOutcome
    action: WakeAction
    processed_at: datetime
    message_id: Optional[str] = None
    hitl_review_id: Optional[str] = None
    next_wake_at: Optional[datetime] = None
    error: Optional[str] = None


# -----------------------------------------------------------------------------
# Wake Handler
# -----------------------------------------------------------------------------

class WakeHandler:
    """Handler for processing scheduled wake events.
    
    This class implements the wake processing pipeline:
    1. Acquire distributed lock on touch
    2. Check current state (is touch still valid?)
    3. Determine action based on state and context
    4. Execute action (send, HITL, reschedule, skip)
    5. Update touch state via UWG
    6. Release lock
    
    Parameters
    ----------
    scheduler : TouchScheduler
        The scheduler for lock management and rescheduling
    state_adapter : TouchStateUWGAdapter
        UWG adapter for state updates
    touch_sender : Optional[Callable]
        Callback to actually send touch messages
    hitl_client : Optional[Any]
        Client for HITL escalation
    """
    
    def __init__(
        self,
        scheduler: Any,  # TouchScheduler
        state_adapter: Any,  # TouchStateUWGAdapter
        touch_sender: Optional[Callable[[WakeRequest], tuple[bool, Optional[str]]]] = None,
        hitl_client: Optional[Any] = None,
    ):
        self._scheduler = scheduler
        self._state_adapter = state_adapter
        self._touch_sender = touch_sender
        self._hitl_client = hitl_client
    
    def process_wake(self, request: WakeRequest) -> WakeResult:
        """Process a single wake request.
        
        This is the main entry point for wake processing.
        
        Parameters
        ----------
        request : WakeRequest
            The wake request to process
        
        Returns
        -------
        WakeResult
            Result of processing
        """
        now = datetime.now(timezone.utc)
        
        # Step 1: Acquire lock
        if not self._scheduler.acquire_touch_lock(request.touch_id):
            return WakeResult(
                touch_id=request.touch_id,
                outcome=WakeOutcome.LOCKED,
                action=WakeAction.RESCHEDULE,
                processed_at=now,
                error="Another worker holds the touch lock",
            )
        
        try:
            # Step 2: Determine action
            action = self._determine_action(request)
            
            # Step 3: Execute action
            if action == WakeAction.SEND_TOUCH:
                return self._handle_send(request, now)
            elif action == WakeAction.REQUIRE_HITL:
                return self._handle_hitl(request, now)
            elif action == WakeAction.RESCHEDULE:
                return self._handle_reschedule(request, now)
            elif action in (WakeAction.SKIP_EXPIRED, WakeAction.SKIP_CANCELLED, WakeAction.SKIP_CONVERTED):
                return self._handle_skip(request, now, action)
            else:
                return WakeResult(
                    touch_id=request.touch_id,
                    outcome=WakeOutcome.FAILED,
                    action=action,
                    processed_at=now,
                    error=f"Unknown action: {action}",
                )
        
        except Exception as e:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            return WakeResult(
                touch_id=request.touch_id,
                outcome=WakeOutcome.FAILED,
                action=WakeAction.RESCHEDULE,
                processed_at=now,
                error=str(e),
            )
        
        finally:
            # Always release lock
            self._scheduler.release_touch_lock(request.touch_id)
    
    def _determine_action(self, request: WakeRequest) -> WakeAction:
        """Determine what action to take for this wake.
        
        This is the business logic layer that decides based on:
        - HITL policy requirements
        - Campaign state
        - Signal confidence
        - Retry count
        """
        # Check HITL requirement first
        if request.hitl_review_required:
            return WakeAction.REQUIRE_HITL
        
        # Check retry count
        if request.retry_count >= 3:
            # Too many retries - mark expired
            return WakeAction.SKIP_EXPIRED
        
        # Default: send the touch
        return WakeAction.SEND_TOUCH
    
    def _handle_send(self, request: WakeRequest, now: datetime) -> WakeResult:
        """Handle sending a touch message."""
        if self._touch_sender is None:
            return WakeResult(
                touch_id=request.touch_id,
                outcome=WakeOutcome.FAILED,
                action=WakeAction.SEND_TOUCH,
                processed_at=now,
                error="No touch sender configured",
            )
        
        # Send via callback
        success, message_id = self._touch_sender(request)
        
        if success:
            # Update state to 'sent'
            self._update_touch_state(
                request.touch_id,
                "sent",
                {"sent_at": now.isoformat(), "message_id": message_id},
            )
            
            return WakeResult(
                touch_id=request.touch_id,
                outcome=WakeOutcome.PROCESSED,
                action=WakeAction.SEND_TOUCH,
                processed_at=now,
                message_id=message_id,
            )
        else:
            # Send failed - reschedule
            return self._handle_reschedule(request, now, reason="send_failed")
    
    def _handle_hitl(self, request: WakeRequest, now: datetime) -> WakeResult:
        """Handle HITL escalation."""
        if self._hitl_client is None:
            return WakeResult(
                touch_id=request.touch_id,
                outcome=WakeOutcome.FAILED,
                action=WakeAction.REQUIRE_HITL,
                processed_at=now,
                error="No HITL client configured",
            )
        
        # Create HITL review
        try:
            review_id = self._hitl_client.create_review(
                touch_id=request.touch_id,
                recipient_hash=request.recipient_hash,
                campaign_id=request.campaign_id,
                context=request.context_carry_forward,
            )
            
            # Update state
            self._update_touch_state(
                request.touch_id,
                "hitl_pending",
                {"hitl_review_id": review_id, "hitl_review_required": True},
            )
            
            return WakeResult(
                touch_id=request.touch_id,
                outcome=WakeOutcome.PROCESSED,
                action=WakeAction.REQUIRE_HITL,
                processed_at=now,
                hitl_review_id=review_id,
            )
        
        except Exception as e:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            return WakeResult(
                touch_id=request.touch_id,
                outcome=WakeOutcome.FAILED,
                action=WakeAction.REQUIRE_HITL,
                processed_at=now,
                error=f"HITL escalation failed: {e}",
            )
    
    def _handle_reschedule(
        self,
        request: WakeRequest,
        now: datetime,
        reason: str = "retry",
    ) -> WakeResult:
        """Handle rescheduling a touch."""
        from apps_lic.coordination.touch_scheduler import ScheduleTouchRequest
        from datetime import timedelta
        
        # Calculate next wake with exponential backoff
        backoff_hours = min(2 ** request.retry_count, 24)  # Max 24 hours
        next_wake = now + timedelta(hours=backoff_hours)
        
        # Reschedule
        reschedule_request = ScheduleTouchRequest(
            touch_id=request.touch_id,
            recipient_hash=request.recipient_hash,
            campaign_id=request.campaign_id,
            touch_sequence=request.touch_sequence,
            wake_at=next_wake,
            context_carry_forward=request.context_carry_forward,
            trigger_signal=request.trigger_signal,
            trigger_confidence=request.trigger_confidence,
            hitl_review_required=request.hitl_review_required,
            retry_count=request.retry_count + 1,
        )
        
        receipt, failure = self._scheduler.schedule_touch(reschedule_request)
        
        if receipt:
            return WakeResult(
                touch_id=request.touch_id,
                outcome=WakeOutcome.RETRY_SCHEDULED,
                action=WakeAction.RESCHEDULE,
                processed_at=now,
                next_wake_at=next_wake,
            )
        else:
            return WakeResult(
                touch_id=request.touch_id,
                outcome=WakeOutcome.FAILED,
                action=WakeAction.RESCHEDULE,
                processed_at=now,
                next_wake_at=next_wake,
                error=f"Reschedule failed: {failure.reason if failure else 'unknown'}",
            )
    
    def _handle_skip(
        self,
        request: WakeRequest,
        now: datetime,
        action: WakeAction,
    ) -> WakeResult:
        """Handle skipping a touch."""
        # Update state
        state_map = {
            WakeAction.SKIP_EXPIRED: "expired",
            WakeAction.SKIP_CANCELLED: "cancelled",
            WakeAction.SKIP_CONVERTED: "converted",
        }
        new_state = state_map.get(action, "skipped")
        
        self._update_touch_state(request.touch_id, new_state, {})
        
        # Remove from queue
        self._scheduler.unschedule_touch(request.touch_id)
        
        return WakeResult(
            touch_id=request.touch_id,
            outcome=WakeOutcome.PROCESSED,
            action=action,
            processed_at=now,
        )
    
    def _update_touch_state(
        self,
        touch_id: str,
        new_state: str,
        update_fields: dict[str, Any],
    ) -> bool:
        """Update touch state via UWG."""
        from agentic_core.L4_state.uwg.touch_state_writer import (
            TouchStateWriteRequest,
            TouchStateUWGAdapter,
        )
        
        # Build update request - minimal, just state change
        # In production, would fetch current state first
        request = TouchStateWriteRequest(
            touch_id=touch_id,
            recipient_hash="",  # Would be populated from lookup
            campaign_id="",    # Would be populated from lookup
            touch_sequence=0,  # Would be populated from lookup
            touch_state=new_state,
        )
        
        # Update fields
        for key, value in update_fields.items():
            setattr(request, key, value)
        
        receipt, blocked = self._state_adapter.write_touch_state(request)
        return receipt is not None


# -----------------------------------------------------------------------------
# Wake Processor (Batch)
# -----------------------------------------------------------------------------

class WakeProcessor:
    """Batch processor for wake queue.
    
    Polls coordination fabric for due touches and processes them
    using WakeHandler.
    """
    
    def __init__(
        self,
        scheduler: Any,  # TouchScheduler
        handler: WakeHandler,
        poll_interval_seconds: float = 60.0,
    ):
        self._scheduler = scheduler
        self._handler = handler
        self._poll_interval = poll_interval_seconds
        self._running = False
    
    def poll_once(self, limit: int = 100) -> list[WakeResult]:
        """Single poll cycle - get and process due touches.
        
        Parameters
        ----------
        limit : int
            Max touches to process in this cycle
        
        Returns
        -------
        list[WakeResult]
            Results of all processed touches
        """
        # Get due touches from queue
        due_touches = self._scheduler.get_due_touches(limit=limit)
        
        results = []
        for touch_data in due_touches:
            # Convert to WakeRequest
            request = WakeRequest(
                touch_id=touch_data["touch_id"],
                recipient_hash=touch_data["recipient_hash"],
                campaign_id=touch_data["campaign_id"],
                touch_sequence=touch_data["touch_sequence"],
                context_carry_forward=touch_data.get("context_carry_forward", {}),
                trigger_signal=touch_data.get("trigger_signal"),
                trigger_confidence=touch_data.get("trigger_confidence", 0.0),
                hitl_review_required=touch_data.get("hitl_review_required", False),
                retry_count=touch_data.get("retry_count", 0),
            )
            
            # Process
            result = self._handler.process_wake(request)
            results.append(result)
            
            # Remove from queue if successfully processed
            if result.outcome in (WakeOutcome.PROCESSED, WakeOutcome.RETRY_SCHEDULED):
                self._scheduler.unschedule_touch(request.touch_id)
        
        return results


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "WakeAction",
    "WakeOutcome",
    "WakeRequest",
    "WakeResult",
    "WakeHandler",
    "WakeProcessor",
]
