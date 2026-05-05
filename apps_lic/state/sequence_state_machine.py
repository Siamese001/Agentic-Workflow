"""apps_lic.state.sequence_state_machine — W2.P3

Sequence State Machine for multi-touch sequences.

Manages state transitions for touch sequences:
- State: PENDING → SCHEDULED → SENT → RESPONDED → COMPLETE
- Handles timeouts and abandonment
- Tracks sequence progress and health
- Integrates with touch scheduler and propagator
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum, auto
from typing import Any, Optional

from apps_lic.sequences.touch_sequence_definitions import (
    SequenceType,
    get_sequence_definition,
)


class SequenceState(str, Enum):
    """States in the touch sequence lifecycle."""
    
    PENDING = "pending"           # Sequence created, not yet scheduled
    SCHEDULED = "scheduled"     # At least one touch scheduled
    ACTIVE = "active"           # Touch in flight (sent, awaiting response)
    RESPONDED = "responded"     # Recipient responded
    CONVERTED = "converted"     # Positive outcome achieved
    EXHAUSTED = "exhausted"     # Max touches reached, no response
    ABANDONED = "abandoned"     # Operator cancelled
    TIMEOUT = "timeout"         # Sequence exceeded max duration


class TouchStatus(str, Enum):
    """Status of an individual touch."""
    
    PENDING = "pending"         # Not yet scheduled
    SCHEDULED = "scheduled"     # In wake queue
    LOCKED = "locked"           # Lock acquired for processing
    SENDING = "sending"         # Send in progress
    SENT = "sent"               # Successfully sent
    FAILED = "failed"           # Send failed
    RESPONDED = "responded"     # Response received


@dataclass
class TouchState:
    """State of a single touch in a sequence.
    
    Fields
    ------
    touch_id : str
        Unique touch identifier
    touch_number : int
        Position in sequence (1-indexed)
    status : TouchStatus
        Current touch status
    scheduled_at : Optional[datetime]
        When scheduled (if scheduled)
    wake_at : Optional[datetime]
        When due for wake (if scheduled)
    sent_at : Optional[datetime]
        When sent (if sent)
    responded_at : Optional[datetime]
        When response received (if responded)
    message_body_hash : Optional[str]
        Hash of rendered message
    context_carry_forward : dict[str, Any]
        Context propagated from prior touch
    retry_count : int
        Number of send retries
    error : Optional[str]
        Error message if failed
    """
    
    touch_id: str
    touch_number: int
    status: TouchStatus = TouchStatus.PENDING
    scheduled_at: Optional[datetime] = None
    wake_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None
    message_body_hash: Optional[str] = None
    context_carry_forward: dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    error: Optional[str] = None


@dataclass
class SequenceStateRecord:
    """Complete state record for a touch sequence.
    
    Fields
    ------
    sequence_id : str
        Unique sequence identifier
    campaign_id : str
        Parent campaign
    recipient_hash : str
        Hashed recipient identifier
    sequence_type : SequenceType
        Type of sequence
    current_state : SequenceState
        Overall sequence state
    touches : list[TouchState]
        State of each touch in sequence
    created_at : datetime
        When sequence was created
    updated_at : datetime
        Last state update
    max_duration_hours : int
        Maximum allowed duration
    completed_at : Optional[datetime]
        When sequence completed (if completed)
    completion_reason : Optional[str]
        Why sequence completed
    metadata : dict[str, Any]
        Additional metadata
    """
    
    sequence_id: str
    campaign_id: str
    recipient_hash: str
    sequence_type: SequenceType
    current_state: SequenceState = SequenceState.PENDING
    touches: list[TouchState] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    max_duration_hours: int = 336  # 14 days default
    completed_at: Optional[datetime] = None
    completion_reason: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Ensure updated_at is set on creation
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)


@dataclass(frozen=True)
class StateTransition:
    """A state transition that occurred.
    
    Fields
    ------
    sequence_id : str
        Which sequence transitioned
    from_state : SequenceState
        Previous state
    to_state : SequenceState
        New state
    triggered_by : str
        What caused the transition
    touch_id : Optional[str]
        Touch that triggered (if applicable)
    transitioned_at : datetime
        When transition occurred
    """
    
    sequence_id: str
    from_state: SequenceState
    to_state: SequenceState
    triggered_by: str
    touch_id: Optional[str]
    transitioned_at: datetime


class SequenceStateMachine:
    """State machine for managing touch sequence lifecycle.
    
    Handles state transitions:
    - PENDING → SCHEDULED (when first touch scheduled)
    - SCHEDULED → ACTIVE (when touch sent)
    - ACTIVE → RESPONDED (when response received)
    - ACTIVE → SCHEDULED (when next touch scheduled)
    - Any → EXHAUSTED (when max touches reached)
    - Any → TIMEOUT (when max duration exceeded)
    - Any → ABANDONED (when operator cancels)
    - RESPONDED → CONVERTED (positive outcome)
    """
    
    # State transition table: (current, event) → next_state
    TRANSITIONS: dict[tuple[SequenceState, str], SequenceState] = {
        (SequenceState.PENDING, "touch_scheduled"): SequenceState.SCHEDULED,
        (SequenceState.SCHEDULED, "touch_sent"): SequenceState.ACTIVE,
        (SequenceState.ACTIVE, "response_received"): SequenceState.RESPONDED,
        (SequenceState.ACTIVE, "next_touch_scheduled"): SequenceState.SCHEDULED,
        (SequenceState.ACTIVE, "max_touches_reached"): SequenceState.EXHAUSTED,
        (SequenceState.SCHEDULED, "max_touches_reached"): SequenceState.EXHAUSTED,
        (SequenceState.SCHEDULED, "timeout"): SequenceState.TIMEOUT,
        (SequenceState.ACTIVE, "timeout"): SequenceState.TIMEOUT,
        (SequenceState.RESPONDED, "positive_outcome"): SequenceState.CONVERTED,
        (SequenceState.PENDING, "abandoned"): SequenceState.ABANDONED,
        (SequenceState.SCHEDULED, "abandoned"): SequenceState.ABANDONED,
        (SequenceState.ACTIVE, "abandoned"): SequenceState.ABANDONED,
    }
    
    def __init__(self) -> None:
        self._transition_log: list[StateTransition] = []
        self._active_sequences: dict[str, SequenceStateRecord] = {}
    
    def create_sequence(
        self,
        sequence_id: str,
        campaign_id: str,
        recipient_hash: str,
        sequence_type: SequenceType,
    ) -> SequenceStateRecord:
        """Create a new sequence state record.
        
        Parameters
        ----------
        sequence_id : str
            Unique sequence identifier
        campaign_id : str
            Parent campaign
        recipient_hash : str
            Hashed recipient identifier
        sequence_type : SequenceType
            Type of sequence
        
        Returns
        -------
        SequenceStateRecord
            Initialized sequence state
        """
        seq_def = get_sequence_definition(sequence_type)
        
        record = SequenceStateRecord(
            sequence_id=sequence_id,
            campaign_id=campaign_id,
            recipient_hash=recipient_hash,
            sequence_type=sequence_type,
            current_state=SequenceState.PENDING,
            max_duration_hours=seq_def.max_duration_days * 24,
        )
        
        self._active_sequences[sequence_id] = record
        return record
    
    def transition(
        self,
        record: SequenceStateRecord,
        event: str,
        touch_id: Optional[str] = None,
    ) -> SequenceStateRecord:
        """Apply a state transition.
        
        Parameters
        ----------
        record : SequenceStateRecord
            Current sequence state
        event : str
            Event triggering transition
        touch_id : Optional[str]
            Touch that triggered (if applicable)
        
        Returns
        -------
        SequenceStateRecord
            Updated sequence state
        """
        current = record.current_state
        next_state = self.TRANSITIONS.get((current, event))
        
        if next_state is None:
            # No valid transition - check for timeout
            if event == "check_timeout":
                if self._is_timed_out(record):
                    next_state = SequenceState.TIMEOUT
                else:
                    return record  # No change
            else:
                return record  # No valid transition
        
        # Apply transition
        from_state = record.current_state
        record.current_state = next_state
        record.updated_at = datetime.now(timezone.utc)
        
        # Log transition
        transition = StateTransition(
            sequence_id=record.sequence_id,
            from_state=from_state,
            to_state=next_state,
            triggered_by=event,
            touch_id=touch_id,
            transitioned_at=datetime.now(timezone.utc),
        )
        self._transition_log.append(transition)
        
        # Handle completion
        if next_state in (SequenceState.CONVERTED, SequenceState.EXHAUSTED, 
                         SequenceState.ABANDONED, SequenceState.TIMEOUT):
            record.completed_at = datetime.now(timezone.utc)
            record.completion_reason = event
        
        return record
    
    def add_touch_state(
        self,
        record: SequenceStateRecord,
        touch_id: str,
        touch_number: int,
        context_carry_forward: Optional[dict[str, Any]] = None,
    ) -> TouchState:
        """Add a touch to the sequence.
        
        Parameters
        ----------
        record : SequenceStateRecord
            Sequence to add touch to
        touch_id : str
            Touch identifier
        touch_number : int
            Position in sequence
        context_carry_forward : Optional[dict]
            Context from prior touch
        
        Returns
        -------
        TouchState
            Created touch state
        """
        touch_state = TouchState(
            touch_id=touch_id,
            touch_number=touch_number,
            context_carry_forward=context_carry_forward or {},
        )
        record.touches.append(touch_state)
        record.updated_at = datetime.now(timezone.utc)
        return touch_state
    
    def update_touch_status(
        self,
        record: SequenceStateRecord,
        touch_id: str,
        status: TouchStatus,
        **kwargs: Any,
    ) -> Optional[TouchState]:
        """Update status of a touch in the sequence.
        
        Parameters
        ----------
        record : SequenceStateRecord
            Sequence containing touch
        touch_id : str
            Touch to update
        status : TouchStatus
            New status
        **kwargs : Any
            Additional fields to update
        
        Returns
        -------
        Optional[TouchState]
            Updated touch state, or None if not found
        """
        for touch in record.touches:
            if touch.touch_id == touch_id:
                touch.status = status
                
                # Update timestamp fields
                if status == TouchStatus.SCHEDULED:
                    touch.scheduled_at = datetime.now(timezone.utc)
                elif status == TouchStatus.SENT:
                    touch.sent_at = datetime.now(timezone.utc)
                elif status == TouchStatus.RESPONDED:
                    touch.responded_at = datetime.now(timezone.utc)
                
                # Update other fields
                for key, value in kwargs.items():
                    if hasattr(touch, key):
                        setattr(touch, key, value)
                
                record.updated_at = datetime.now(timezone.utc)
                return touch
        
        return None
    
    def _is_timed_out(self, record: SequenceStateRecord) -> bool:
        """Check if sequence has exceeded max duration."""
        now = datetime.now(timezone.utc)
        elapsed = now - record.created_at
        return elapsed.total_seconds() > record.max_duration_hours * 3600
    
    def get_active_sequences(self) -> dict[str, SequenceStateRecord]:
        """Get all active (non-terminal) sequences."""
        terminal_states = {
            SequenceState.CONVERTED,
            SequenceState.EXHAUSTED,
            SequenceState.ABANDONED,
            SequenceState.TIMEOUT,
        }
        return {
            sid: rec for sid, rec in self._active_sequences.items()
            if rec.current_state not in terminal_states
        }
    
    def get_sequence(self, sequence_id: str) -> Optional[SequenceStateRecord]:
        """Get a sequence by ID."""
        return self._active_sequences.get(sequence_id)
    
    def get_transition_history(
        self,
        sequence_id: Optional[str] = None,
    ) -> list[StateTransition]:
        """Get transition history.
        
        Parameters
        ----------
        sequence_id : Optional[str]
            Filter by sequence (None for all)
        
        Returns
        -------
        list[StateTransition]
            Matching transitions
        """
        if sequence_id is None:
            return self._transition_log.copy()
        return [t for t in self._transition_log if t.sequence_id == sequence_id]


def create_sequence_from_scheduler(
    campaign_id: str,
    recipient_hash: str,
    sequence_type: SequenceType,
    scheduler_result: list[tuple[Any, Any]],
) -> tuple[SequenceStateRecord, list[TouchState]]:
    """Factory: Create sequence from scheduler results.
    
    Parameters
    ----------
    campaign_id : str
        Parent campaign
    recipient_hash : str
        Hashed recipient identifier
    sequence_type : SequenceType
        Type of sequence
    scheduler_result : list[tuple[receipt, failure]]
        Results from TouchScheduler.calculate_and_schedule_sequence()
    
    Returns
    -------
    tuple[SequenceStateRecord, list[TouchState]]
        Created sequence and touch states
    """
    from uuid import uuid4
    
    sequence_id = f"{campaign_id}:{recipient_hash}:{uuid4().hex[:8]}"
    
    machine = SequenceStateMachine()
    record = machine.create_sequence(
        sequence_id=sequence_id,
        campaign_id=campaign_id,
        recipient_hash=recipient_hash,
        sequence_type=sequence_type,
    )
    
    touches = []
    for i, (receipt, failure) in enumerate(scheduler_result, 1):
        if receipt:
            touch_id = receipt.touch_id
            touch = machine.add_touch_state(record, touch_id, i)
            touch.status = TouchStatus.SCHEDULED
            touch.scheduled_at = receipt.scheduled_at
            touch.wake_at = receipt.wake_at
            touches.append(touch)
    
    return record, touches


__all__ = [
    "SequenceState",
    "TouchStatus",
    "TouchState",
    "SequenceStateRecord",
    "StateTransition",
    "SequenceStateMachine",
    "create_sequence_from_scheduler",
]
