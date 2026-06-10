"""Context Carry-Forward Bridge for apps_lic Multi-Touch Sequences.

Wave 5, Phase 2 of apps-lic-infra-prerequisites-unblock-p2p3

This module provides the bridge between identity propagation and
touch state, enabling context to flow from touch N to touch N+1.

App: apps_lic
Layer: Integration (apps_lic/identity/)

Dependencies:
    - Identity Propagation (apps_lic/identity/propagation.py)
    - Touch Scheduler (apps_lic/coordination/touch_scheduler.py)
    - Touch State Writer (agentic_core/L4_state/uwg/touch_state_writer.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime, timezone

from apps_lic.identity.propagation import (
    IdentityContext,
    IdentityPropagationService,
    RecipientIdentity,
)


# -----------------------------------------------------------------------------
# Carry-Forward Request / Result
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class CarryForwardRequest:
    """Request to carry context forward between touches.
    
    Fields
    ------
    prior_touch_id : str
        Touch ID of prior touch (source)
    next_touch_id : str
        Touch ID of next touch (target)
    campaign_id : str
        Campaign ID
    recipient_hash : str
        Hashed recipient identifier
    prior_touch_sequence : int
        Sequence number of prior touch
    next_touch_sequence : int
        Sequence number of next touch
    new_signals : list[dict]
        New signals to add to context
    """
    
    prior_touch_id: str
    next_touch_id: str
    campaign_id: str
    recipient_hash: str
    prior_touch_sequence: int
    next_touch_sequence: int
    new_signals: list[dict] = field(default_factory=list)


@dataclass(frozen=True)
class CarryForwardResult:
    """Result of context carry-forward operation.
    
    Fields
    ------
    success : bool
        Whether carry-forward succeeded
    context_carried : dict
        The context that was carried forward
    next_touch_id : str
        Target touch ID
    error : Optional[str]
        Error message if failed
    """
    
    success: bool
    context_carried: dict[str, Any] = field(default_factory=dict)
    next_touch_id: str = ""
    error: Optional[str] = None


# -----------------------------------------------------------------------------
# Context Carry-Forward Bridge
# -----------------------------------------------------------------------------

class ContextCarryForwardBridge:
    """Bridge for carrying context between touches in a sequence.
    
    This class implements the logic for:
    1. Loading context from prior touch
    2. Propagating to next touch
    3. Serializing for coordination fabric scheduling
    4. Storing in L4 touch state
    
    Parameters
    ----------
    identity_service : IdentityPropagationService
        Identity propagation service
    state_adapter : TouchStateUWGAdapter
        UWG adapter for state updates
    """
    
    def __init__(
        self,
        identity_service: IdentityPropagationService,
        state_adapter: Any,
    ):
        self._identity = identity_service
        self._state = state_adapter
    
    def carry_forward(
        self,
        request: CarryForwardRequest,
    ) -> CarryForwardResult:
        """Carry context from prior touch to next touch.
        
        This is the core context propagation function.
        
        Parameters
        ----------
        request : CarryForwardRequest
            Carry-forward request
        
        Returns
        -------
        CarryForwardResult
            Result of operation
        """
        try:
            # Step 1: Propagate context via identity service
            new_context = self._identity.propagate_context(
                identity_hash=request.recipient_hash,
                campaign_id=request.campaign_id,
                from_touch_sequence=request.prior_touch_sequence,
                to_touch_sequence=request.next_touch_sequence,
                additional_signals=request.new_signals,
            )
            
            if new_context is None:
                # No prior context - create fresh context
                identity = RecipientIdentity(
                    identity_hash=request.recipient_hash,
                    identity_type="hash",
                )
                new_context = self._identity.create_context(
                    identity=identity,
                    campaign_id=request.campaign_id,
                    touch_sequence=request.next_touch_sequence,
                    initial_context={},
                )
                
                # Add new signals if any
                if request.new_signals:
                    new_context = IdentityContext(
                        identity_hash=new_context.identity_hash,
                        campaign_id=new_context.campaign_id,
                        touch_sequence=new_context.touch_sequence,
                        accumulated_signals=list(request.new_signals),
                        prior_responses=list(new_context.prior_responses),
                        content_preferences=dict(new_context.content_preferences),
                        timing_preferences=dict(new_context.timing_preferences),
                        custom_context=dict(new_context.custom_context),
                        created_at=new_context.created_at,
                        updated_at=datetime.now(timezone.utc).isoformat(),
                    )
            
            # Step 2: Serialize context for storage
            context_data = self._serialize_context(new_context)
            
            # Step 3: Update next touch's state with context_carry_forward
            self._update_touch_context(
                touch_id=request.next_touch_id,
                recipient_hash=request.recipient_hash,
                campaign_id=request.campaign_id,
                touch_sequence=request.next_touch_sequence,
                context_data=context_data,
            )
            
            return CarryForwardResult(
                success=True,
                context_carried=context_data,
                next_touch_id=request.next_touch_id,
            )
        
        except Exception as e:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
            return CarryForwardResult(
                success=False,
                context_carried={},
                next_touch_id=request.next_touch_id,
                error=str(e),
            )
    
    def prepare_scheduling_context(
        self,
        recipient_hash: str,
        campaign_id: str,
        touch_sequence: int,
        prior_context: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Prepare context for scheduling in coordination fabric.
        
        This creates the context_carry_forward payload that gets
        stored in the coordination fabric wake queue.
        
        Parameters
        ----------
        recipient_hash : str
            Recipient identifier
        campaign_id : str
            Campaign ID
        touch_sequence : int
            Position in sequence
        prior_context : Optional[dict]
            Context from prior touches
        
        Returns
        -------
        dict
            Scheduling context payload
        """
        context = {
            "identity_hash": recipient_hash,
            "campaign_id": campaign_id,
            "touch_sequence": touch_sequence,
            "accumulated_context": prior_context or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "_version": "1.0.0",
        }
        
        return context
    
    def extract_context_from_wake(
        self,
        wake_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Extract carry-forward context from wake data.
        
        Called when a touch is woken to retrieve prior context.
        
        Parameters
        ----------
        wake_data : dict
            Wake data from coordination fabric
        
        Returns
        -------
        dict
            Extracted context
        """
        # Extract from wake data
        context = wake_data.get("context_carry_forward", {})
        
        # Validate and upgrade if needed
        version = context.get("_version", "0.0.0")
        
        if version == "0.0.0":
            # Legacy format - upgrade
            context = self._upgrade_legacy_context(context)
        
        return context
    
    def update_context_from_send(
        self,
        touch_id: str,
        recipient_hash: str,
        campaign_id: str,
        touch_sequence: int,
        send_metadata: dict[str, Any],
    ) -> bool:
        """Update context when a touch is sent.
        
        Records send time, message ID, etc. in context.
        
        Parameters
        ----------
        touch_id : str
            Touch ID
        recipient_hash : str
            Recipient identifier
        campaign_id : str
            Campaign ID
        touch_sequence : int
            Sequence number
        send_metadata : dict
            Send metadata (message_id, sent_at, etc.)
        
        Returns
        -------
        bool
            True if update succeeded
        """
        # Load existing context
        existing = self._load_touch_context(
            touch_id=touch_id,
            recipient_hash=recipient_hash,
            campaign_id=campaign_id,
        )
        
        # Merge with send metadata
        updated = dict(existing)
        updated["last_sent_at"] = send_metadata.get("sent_at")
        updated["message_id"] = send_metadata.get("message_id")
        updated["send_channel"] = send_metadata.get("channel");
        
        # Store updated context
        return self._update_touch_context(
            touch_id=touch_id,
            recipient_hash=recipient_hash,
            campaign_id=campaign_id,
            touch_sequence=touch_sequence,
            context_data=updated,
        )
    
    def _serialize_context(self, context: IdentityContext) -> dict[str, Any]:
        """Serialize IdentityContext to dictionary."""
        return {
            "identity_hash": context.identity_hash,
            "campaign_id": context.campaign_id,
            "touch_sequence": context.touch_sequence,
            "accumulated_signals": context.accumulated_signals,
            "prior_responses": context.prior_responses,
            "content_preferences": context.content_preferences,
            "timing_preferences": context.timing_preferences,
            "custom_context": context.custom_context,
            "created_at": context.created_at,
            "updated_at": context.updated_at,
            "_version": "1.0.0",
        }
    
    def _update_touch_context(
        self,
        touch_id: str,
        recipient_hash: str,
        campaign_id: str,
        touch_sequence: int,
        context_data: dict[str, Any],
    ) -> bool:
        """Update touch state with context_carry_forward."""
        from agentic_core.L4_state.uwg.touch_state_writer import (
            TouchStateWriteRequest,
            schedule_touch,
        )
        
        # Use schedule_touch convenience function with context
        receipt, blocked = schedule_touch(
            touch_id=touch_id,
            recipient_hash=recipient_hash,
            campaign_id=campaign_id,
            touch_sequence=touch_sequence,
            wake_at=datetime.now(timezone.utc),  # Immediate for context update
            context_carry_forward=context_data,
        )
        
        return receipt is not None
    
    def _load_touch_context(
        self,
        touch_id: str,
        recipient_hash: str,
        campaign_id: str,
    ) -> dict[str, Any]:
        """Load context from touch state."""
        # In production, query touch_state table
        # For now, return empty context
        return {}
    
    def _upgrade_legacy_context(self, context: dict) -> dict[str, Any]:
        """Upgrade legacy context format to current version."""
        upgraded = dict(context)
        upgraded["_version"] = "1.0.0"
        
        # Ensure required fields exist
        if "identity_hash" not in upgraded:
            upgraded["identity_hash"] = ""
        if "campaign_id" not in upgraded:
            upgraded["campaign_id"] = ""
        if "touch_sequence" not in upgraded:
            upgraded["touch_sequence"] = 0
        
        return upgraded


# -----------------------------------------------------------------------------
# Convenience Functions
# -----------------------------------------------------------------------------

def carry_context_forward(
    prior_touch_id: str,
    next_touch_id: str,
    recipient_hash: str,
    campaign_id: str,
    prior_sequence: int,
    next_sequence: int,
    new_signals: Optional[list] = None,
) -> CarryForwardResult:
    """One-shot context carry-forward.
    
    Convenience function that creates bridge and executes carry-forward.
    
    Parameters
    ----------
    prior_touch_id : str
    next_touch_id : str
    recipient_hash : str
    campaign_id : str
    prior_sequence : int
    next_sequence : int
    new_signals : Optional[list]
    
    Returns
    -------
    CarryForwardResult
        Result of operation
    """
    from apps_lic.identity.propagation import get_identity_propagation_service
    from agentic_core.L4_state.uwg.durable_write_gateway import get_default_gateway
    from agentic_core.L4_state.uwg.touch_state_writer import TouchStateUWGAdapter
    
    identity_service = get_identity_propagation_service()
    gateway = get_default_gateway()
    state_adapter = TouchStateUWGAdapter(gateway)
    
    bridge = ContextCarryForwardBridge(
        identity_service=identity_service,
        state_adapter=state_adapter,
    )
    
    request = CarryForwardRequest(
        prior_touch_id=prior_touch_id,
        next_touch_id=next_touch_id,
        campaign_id=campaign_id,
        recipient_hash=recipient_hash,
        prior_touch_sequence=prior_sequence,
        next_touch_sequence=next_sequence,
        new_signals=new_signals or [],
    )
    
    return bridge.carry_forward(request)


# -----------------------------------------------------------------------------
# Exports
# -----------------------------------------------------------------------------

__all__ = [
    "CarryForwardRequest",
    "CarryForwardResult",
    "ContextCarryForwardBridge",
    "carry_context_forward",
]
