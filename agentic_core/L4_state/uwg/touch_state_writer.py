"""Touch State Writer for apps_lic — UWG Integration.

Wave 1, Phase 2 of apps-lic-infra-prerequisites-unblock-p2p3

This module provides DurableWriteGateway (UWG) integration for apps_lic
touch state persistence. It defines write requests, receipts, and the
write class severity for touch state operations.

Layer: L4 State (agentic_core/L4_state/uwg/)
App: apps_lic

Dependencies:
    - DurableWriteGateway (agentic_core/L4_state/uwg/durable_write_gateway.py)
    - WriteClassSeverity (agentic_core/L4_state/uwg/write_class_severity.py)
    - apps_lic_touch_state schema (agentic_core/L4_state/schemas/apps_lic_touch_state.sql)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from agentic_core.L4_state.uwg.write_class_severity import WriteClassSeverity


# -----------------------------------------------------------------------------
# Touch State Write Request
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class TouchStateWriteRequest:
    """Request to write/update touch state through UWG.
    
    Fields
    ------
    touch_id : str
        Unique identifier for this touch (UUID or structured ID)
    recipient_hash : str
        Hashed recipient identifier (PII-safe, not reversible)
    campaign_id : str
        Parent campaign identifier
    touch_sequence : int
        Position in multi-touch sequence (1, 2, 3...)
    touch_state : str
        Current state: scheduled|sent|replied|bounced|converted|expired|cancelled
    next_scheduled_wake : Optional[datetime]
        When coordination fabric should wake this touch (UTC)
    context_carry_forward : dict[str, Any]
        Context to carry to next touch in sequence
    trigger_signal : Optional[str]
        What triggered this touch (resurfacing signal type)
    trigger_confidence : float
        Confidence in trigger (0.0-1.0)
    hitl_review_required : bool
        Whether this touch needs L5 HITL review before sending
    metadata : dict[str, Any]
        Additional metadata for this touch
    """
    
    touch_id: str
    recipient_hash: str
    campaign_id: str
    touch_sequence: int
    touch_state: str
    next_scheduled_wake: Optional[datetime] = None
    context_carry_forward: dict[str, Any] = field(default_factory=dict)
    trigger_signal: Optional[str] = None
    trigger_confidence: float = 0.0
    hitl_review_required: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Validate touch_state
        valid_states = {"scheduled", "sent", "replied", "bounced", "converted", "expired", "cancelled"}
        if self.touch_state not in valid_states:
            raise ValueError(f"Invalid touch_state: {self.touch_state}. Must be one of {valid_states}")
        
        # Validate trigger_confidence
        if not 0.0 <= self.trigger_confidence <= 1.0:
            raise ValueError(f"trigger_confidence must be in [0.0, 1.0], got {self.trigger_confidence}")


# -----------------------------------------------------------------------------
# Touch State Commit Receipt
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class TouchStateCommitReceipt:
    """Receipt from UWG after successful touch state commit.
    
    Fields
    ------
    touch_id : str
        The touch ID that was committed
    commit_timestamp : datetime
        When the commit occurred (UTC)
    bundle_digest : str
        UWG bundle digest for verification
    state_diff_applied : bool
        Whether state diff was successfully applied
    """
    
    touch_id: str
    commit_timestamp: datetime
    bundle_digest: str
    state_diff_applied: bool


@dataclass(frozen=True)
class TouchStateBlockedReceipt:
    """Receipt when UWG blocks a touch state write.
    
    Fields
    ------
    touch_id : str
        The touch ID that was blocked
    blocked_reason : str
        Why the write was blocked
    blocked_at : datetime
        When the block occurred (UTC)
    resolution_hint : Optional[str]
        Guidance on how to resolve the block
    """
    
    touch_id: str
    blocked_reason: str
    blocked_at: datetime
    resolution_hint: Optional[str] = None


# -----------------------------------------------------------------------------
# Write Class Severity
# -----------------------------------------------------------------------------

TOUCH_STATE_WRITE_CLASS = "apps_lic.touch_state"

# Touch state writes are DURABLE because:
# 1. They represent customer-facing commitments (scheduled outreach)
# 2. Loss of touch state would break multi-touch sequences
# 3. Regulatory compliance may require audit trail
# 4. HITL decisions depend on durable state
TOUCH_STATE_SEVERITY = WriteClassSeverity.DURABLE


def get_touch_state_write_class_severity() -> tuple[str, WriteClassSeverity]:
    """Return the write class and severity for touch state operations.
    
    This function is used by UWG catalog registration.
    
    Returns
    -------
    tuple[str, WriteClassSeverity]
        (write_class, severity) for touch state writes
    """
    return (TOUCH_STATE_WRITE_CLASS, TOUCH_STATE_SEVERITY)


# -----------------------------------------------------------------------------
# Touch State UWG Integration
# -----------------------------------------------------------------------------

class TouchStateUWGAdapter:
    """Adapter for writing touch state through UWG.
    
    This class bridges apps_lic touch state operations to the
    DurableWriteGateway, ensuring ACID guarantees for touch state.
    
    Parameters
    ----------
    gateway : DurableWriteGateway
        The UWG instance to use for writes
    
    Example
    -------
    >>> from agentic_core.L4_state.uwg.durable_write_gateway import get_default_gateway
    >>> from agentic_core.L4_state.uwg.touch_state_writer import TouchStateUWGAdapter, TouchStateWriteRequest
    >>> 
    >>> gateway = get_default_gateway()
    >>> adapter = TouchStateUWGAdapter(gateway)
    >>> 
    >>> request = TouchStateWriteRequest(
    ...     touch_id="touch-123",
    ...     recipient_hash="hash-abc",
    ...     campaign_id="campaign-456",
    ...     touch_sequence=1,
    ...     touch_state="scheduled",
    ...     next_scheduled_wake=datetime.now(timezone.utc),
    ... )
    >>> 
    >>> receipt = adapter.write_touch_state(request)
    """
    
    def __init__(self, gateway):
        # Deferred import to avoid circular dependency
        from agentic_core.L4_state.uwg.durable_write_gateway import DurableWriteGateway
        self._gateway: DurableWriteGateway = gateway
    
    def write_touch_state(
        self,
        request: TouchStateWriteRequest,
        rollback_plan: Optional[dict[str, Any]] = None,
    ) -> tuple[Optional[TouchStateCommitReceipt], Optional[TouchStateBlockedReceipt]]:
        """Write touch state through UWG.
        
        Parameters
        ----------
        request : TouchStateWriteRequest
            The touch state to write
        rollback_plan : Optional[dict]
            Rollback instructions if commit fails
        
        Returns
        -------
        tuple[Optional[TouchStateCommitReceipt], Optional[TouchStateBlockedReceipt]]
            (commit_receipt, blocked_receipt) — exactly one will be non-None
        """
        # Build state diff for UWG
        state_diff = self._build_state_diff(request)
        
        # Submit to UWG
        commit_receipt, blocked_receipt, _ = self._gateway.commit(
            write_class=TOUCH_STATE_WRITE_CLASS,
            state_diffs=[state_diff],
            rollback_plan=rollback_plan or {},
        )
        
        if commit_receipt is not None:
            return (
                TouchStateCommitReceipt(
                    touch_id=request.touch_id,
                    commit_timestamp=datetime.now(timezone.utc),
                    bundle_digest=commit_receipt.bundle_digest,
                    state_diff_applied=True,
                ),
                None,
            )
        else:
            return (
                None,
                TouchStateBlockedReceipt(
                    touch_id=request.touch_id,
                    blocked_reason=blocked_receipt.reason if blocked_receipt else "unknown",
                    blocked_at=datetime.now(timezone.utc),
                    resolution_hint=blocked_receipt.resolution_hint if blocked_receipt else None,
                ),
            )
    
    def _build_state_diff(self, request: TouchStateWriteRequest) -> dict[str, Any]:
        """Convert TouchStateWriteRequest to UWG state diff format."""
        import json
        
        return {
            "table": "apps_lic_touch_state",
            "operation": "UPSERT",
            "key": {"touch_id": request.touch_id},
            "values": {
                "touch_id": request.touch_id,
                "recipient_hash": request.recipient_hash,
                "campaign_id": request.campaign_id,
                "touch_sequence": request.touch_sequence,
                "touch_state": request.touch_state,
                "next_scheduled_wake": request.next_scheduled_wake.isoformat() if request.next_scheduled_wake else None,
                "context_carry_forward": json.dumps(request.context_carry_forward) if request.context_carry_forward else None,
                "trigger_signal": request.trigger_signal,
                "trigger_confidence": request.trigger_confidence,
                "hitl_review_required": request.hitl_review_required,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        }


# -----------------------------------------------------------------------------
# Convenience Functions
# -----------------------------------------------------------------------------

def schedule_touch(
    touch_id: str,
    recipient_hash: str,
    campaign_id: str,
    touch_sequence: int,
    wake_at: datetime,
    context_carry_forward: Optional[dict[str, Any]] = None,
    trigger_signal: Optional[str] = None,
    trigger_confidence: float = 0.0,
    hitl_review_required: bool = False,
) -> tuple[Optional[TouchStateCommitReceipt], Optional[TouchStateBlockedReceipt]]:
    """Convenience: Schedule a new touch.
    
    This is a fire-and-forget helper for the common case of scheduling
    a touch. For more control, use TouchStateUWGAdapter directly.
    """
    from agentic_core.L4_state.uwg.durable_write_gateway import get_default_gateway
    
    gateway = get_default_gateway()
    adapter = TouchStateUWGAdapter(gateway)
    
    request = TouchStateWriteRequest(
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
    
    return adapter.write_touch_state(request)


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "TouchStateWriteRequest",
    "TouchStateCommitReceipt",
    "TouchStateBlockedReceipt",
    "TOUCH_STATE_WRITE_CLASS",
    "TOUCH_STATE_SEVERITY",
    "get_touch_state_write_class_severity",
    "TouchStateUWGAdapter",
    "schedule_touch",
]
