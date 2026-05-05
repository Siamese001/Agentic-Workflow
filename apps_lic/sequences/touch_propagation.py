"""apps_lic.sequences.touch_propagation — W2.P2

Touch N → N+1 Context Propagation

Handles carry-forward of context between touches in a sequence:
- Extracts carry_forward_keys from touch N result
- Assembles context package for touch N+1
- Manages context accumulation across sequence
- Handles P2 context slot binding
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import hashlib
import json

from apps_lic.sequences.touch_sequence_definitions import (
    SequenceType,
    TouchDefinition,
    get_sequence_definition,
    get_touch_definition,
)


@dataclass(frozen=True)
class TouchContext:
    """Context accumulated from a touch execution.
    
    Fields
    ------
    touch_id : str
        Unique touch identifier
    touch_number : int
        Position in sequence
    sequence_type : SequenceType
        Which sequence this touch belongs to
    campaign_id : str
        Parent campaign
    recipient_hash : str
        Hashed recipient identifier
    sent_at : Optional[datetime]
        When touch was sent (None if not yet sent)
    message_body_hash : Optional[str]
        Hash of rendered message content
    response_received : bool
        Whether recipient has responded
    context_data : dict
        Arbitrary context data from touch execution
    """
    
    touch_id: str
    touch_number: int
    sequence_type: SequenceType
    campaign_id: str
    recipient_hash: str
    sent_at: Optional[datetime] = None
    message_body_hash: Optional[str] = None
    response_received: bool = False
    context_data: dict[str, Any] = field(default_factory=dict)
    
    def to_carry_forward(self, keys: list[str]) -> dict[str, Any]:
        """Extract specified keys for carry-forward to next touch.
        
        Parameters
        ----------
        keys : list[str]
            Keys to extract from this context
        
        Returns
        -------
        dict[str, Any]
            Subset of context for propagation
        """
        result: dict[str, Any] = {}
        
        # Always include metadata
        result["touch_number"] = self.touch_number
        result["sequence_type"] = self.sequence_type.value
        result["campaign_id"] = self.campaign_id
        result["recipient_hash"] = self.recipient_hash
        
        # Include requested keys from context_data
        for key in keys:
            if key in self.context_data:
                result[key] = self.context_data[key]
        
        # Include standard fields if requested
        if "sent_at" in keys and self.sent_at:
            result["prior_sent_at"] = self.sent_at.isoformat()
        if "message_body_hash" in keys and self.message_body_hash:
            result["prior_message_hash"] = self.message_body_hash
        if "response_received" in keys:
            result["prior_response_status"] = self.response_received
        
        return result


@dataclass
class PropagationResult:
    """Result of context propagation between touches.
    
    Fields
    ------
    source_touch_id : str
        Touch that provided context
    target_touch_number : int
        Next touch number (N+1)
    propagated_context : dict[str, Any]
        Context to bind to next touch
    p2_slots_bound : dict[str, Any]
        P2 context slots that were populated
    success : bool
        Whether propagation succeeded
    error : Optional[str]
        Error message if failed
    """
    
    source_touch_id: str
    target_touch_number: int
    propagated_context: dict[str, Any] = field(default_factory=dict)
    p2_slots_bound: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None


class TouchContextPropagator:
    """Propagates context from touch N to touch N+1.
    
    Manages:
    - Extracting carry-forward keys per sequence definition
    - Binding P2 context slots for next touch
    - Assembling complete context package
    """
    
    def __init__(self) -> None:
        self._propagation_log: list[PropagationResult] = []
    
    def propagate(
        self,
        source_context: TouchContext,
        target_touch_number: int,
        p2_context: Optional[dict[str, Any]] = None,
    ) -> PropagationResult:
        """Propagate context from source touch to next touch.
        
        Parameters
        ----------
        source_context : TouchContext
            Context from touch N (just completed)
        target_touch_number : int
            Target touch number (N+1)
        p2_context : Optional[dict[str, Any]]
            Fresh P2 context for target touch
        
        Returns
        -------
        PropagationResult
            Propagation result with context for target touch
        """
        try:
            # Validate target touch exists
            touch_def = get_touch_definition(
                source_context.sequence_type,
                target_touch_number,
            )
            if touch_def is None:
                return PropagationResult(
                    source_touch_id=source_context.touch_id,
                    target_touch_number=target_touch_number,
                    success=False,
                    error=f"Touch {target_touch_number} not defined for {source_context.sequence_type}",
                )
            
            # Extract carry-forward context
            propagated = source_context.to_carry_forward(touch_def.carry_forward_keys)
            
            # Bind P2 slots for target touch
            p2_slots = self._bind_p2_slots(touch_def, p2_context or {})
            
            # Merge propagated + P2 context
            merged_context = {**propagated, **p2_slots}
            
            result = PropagationResult(
                source_touch_id=source_context.touch_id,
                target_touch_number=target_touch_number,
                propagated_context=merged_context,
                p2_slots_bound=p2_slots,
                success=True,
            )
            
            self._propagation_log.append(result)
            return result
            
        except Exception as e:
            return PropagationResult(
                source_touch_id=source_context.touch_id,
                target_touch_number=target_touch_number,
                success=False,
                error=str(e),
            )
    
    def _bind_p2_slots(
        self,
        touch_def: TouchDefinition,
        p2_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Bind P2 context slots for a touch.
        
        Maps P2 context to slot identifiers (N0, A0, L0).
        
        Parameters
        ----------
        touch_def : TouchDefinition
            Touch definition with required P2 slots
        p2_context : dict[str, Any]
            Raw P2 context data
        
        Returns
        -------
        dict[str, Any]
            Bound P2 slots
        """
        bound: dict[str, Any] = {}
        
        slot_mapping = {
            "N0": "narrative_arc_context",
            "A0": "archetype_tone_calibration",
            "L0": "competitive_landscape_context",
        }
        
        for slot in touch_def.p2_context_required:
            context_key = slot_mapping.get(slot)
            if context_key and context_key in p2_context:
                bound[slot] = p2_context[context_key]
            elif context_key:
                # Provide graceful fallback
                bound[slot] = self._p2_fallback(slot)
        
        return bound
    
    def _p2_fallback(self, slot: str) -> str:
        """Get fallback text for missing P2 context.
        
        Parameters
        ----------
        slot : str
            Slot identifier (N0, A0, L0)
        
        Returns
        -------
        str
            Fallback guidance text
        """
        fallbacks = {
            "N0": "No narrative arc context provided. Use standard outreach arc.",
            "A0": "No archetype calibration provided. Use neutral professional tone.",
            "L0": "No competitive landscape context provided. Omit competitive framing.",
        }
        return fallbacks.get(slot, f"No context for {slot}")
    
    def get_propagation_history(self) -> list[PropagationResult]:
        """Get log of all propagation operations."""
        return self._propagation_log.copy()
    
    def clear_history(self) -> None:
        """Clear propagation log."""
        self._propagation_log.clear()


def create_touch_context_from_result(
    touch_result: dict[str, Any],
    sequence_type: SequenceType,
) -> TouchContext:
    """Factory: Create TouchContext from touch execution result.
    
    Parameters
    ----------
    touch_result : dict[str, Any]
        Result from touch execution
    sequence_type : SequenceType
        Sequence type for this touch
    
    Returns
    -------
    TouchContext
        Context object ready for propagation
    """
    sent_at_str = touch_result.get("sent_at")
    sent_at = datetime.fromisoformat(sent_at_str) if sent_at_str else None
    
    # Calculate message body hash if content provided
    message_body = touch_result.get("message_body", "")
    message_hash = None
    if message_body:
        message_hash = hashlib.sha256(message_body.encode()).hexdigest()[:16]
    
    return TouchContext(
        touch_id=touch_result.get("touch_id", ""),
        touch_number=touch_result.get("touch_number", 0),
        sequence_type=sequence_type,
        campaign_id=touch_result.get("campaign_id", ""),
        recipient_hash=touch_result.get("recipient_hash", ""),
        sent_at=sent_at,
        message_body_hash=message_hash,
        response_received=touch_result.get("response_received", False),
        context_data=touch_result.get("context_data", {}),
    )


__all__ = [
    "TouchContext",
    "PropagationResult",
    "TouchContextPropagator",
    "create_touch_context_from_result",
]
