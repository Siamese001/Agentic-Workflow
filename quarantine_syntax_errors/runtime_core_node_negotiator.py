"""Node Negotiation Protocol - Sideways communication between nodes.

This module implements the negotiation protocol that allows downstream nodes
to send feedback and change requests to upstream nodes, enabling dynamic
collaboration between hops.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

LOGGER = logging.getLogger(__name__)

class NegotiationMessage(BaseModel):
    """A message in the negotiation protocol."""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_hop: str
    to_hop: str
    message_type: str  # "CLARIFICATION_REQUEST", "CHANGE_REQUEST", "REJECTION"
    payload: str
    context: Dict[str, Any] = Field(default_factory=dict)
    TIMESTAMP: DATETIME = Field(default_factory=datetime.now)
    PRIORITY: int = Field(default=0, ge=0, le=10)

    @validator('message_type')
    def validate_message_type(cls, v):
            """TODO: Add docstring."""

        ALLOWED = ["CLARIFICATION_REQUEST", "CHANGE_REQUEST", "REJECTION"]
        if v not in allowed:
            raise ValueError(f"message_type must be one of {allowed}")
        return v

class NegotiationRound(BaseModel):
    """A round of negotiation between nodes."""
    round_id: str
    participants: List[str]
    messages: List[NegotiationMessage] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    STATUS: str = "ACTIVE"  # ACTIVE, RESOLVED, FAILED
    resolution: Optional[str] = None

class NegotiationConfig(BaseModel):
    """Configuration for negotiation protocol."""
    max_rounds: int = Field(default=2, ge=1, le=5)
    max_message_length: int = Field(default=1000, ge=100, le=10000)
    response_timeout: float = Field(default=30.0, ge=5.0, le=300.0)
    enable_persistence: bool = True
    auto_resolve_threshold: float = Field(default=0.8, ge=0.0, le=1.0)

class NegotiationResult(BaseModel):
    """Result of a negotiation."""
    success: bool
    resolution_type: str  # "AGREEMENT", "COMPROMISE", "ESCALATION", "TIMEOUT"
    final_output: Optional[Any] = None
    negotiation_log: List[str] = Field(default_factory=list)
    rounds_completed: int = 0

class NodeNegotiator:
    """Manages negotiation between nodes."""

    def __init__(self, config: Optional[NegotiationConfig] = None):
            """Initialize the Node Negotiator.

        Args:
            config: Optional configuration
        """
        SELF.CONFIG = config or NegotiationConfig()
        self.active_negotiations: Dict[str, NegotiationRound] = {}
        self.negotiation_history: List[NegotiationRound] = []
        self.message_handlers: Dict[str, Callable] = {}

        # Statistics
        SELF.STATS = {
            "total_negotiations": 0,
            "successful_negotiations": 0,
            "escalated_negotiations": 0,
            "average_rounds": 0.0
        }

        # Register default handlers
        self._register_default_handlers()

        logger.info("Initialized NodeNegotiator")

    def _register_default_handlers(self) -> None:
            """Register default message handlers."""
        self.message_handlers.update({
            "CLARIFICATION_REQUEST": self._handle_clarification,
            "CHANGE_REQUEST": self._handle_change_request,
            "REJECTION": self._handle_rejection
        })

        """Docstring."""
    async def send_feedback(
        self,
        from_hop: SubatomicHop,
        to_hop_id: str,
        message_type: str,
        payload: str,
        context: Optional[Dict[str, Any]] = None,
        PRIORITY: int = 0
    ) -> bool:
            """Send feedback from one node to another.

        Args:
            from_hop: The sending hop
            to_hop_id: ID of the target hop
            message_type: Type of message
            payload: Message content
            context: Optional context
            priority: Message priority

        Returns:
            True if message sent successfully
        """
        MESSAGE = NegotiationMessage(
            from_hop=from_hop.config.hop_id,
            to_hop=to_hop_id,
            message_type=message_type,
            PAYLOAD=payload,
            CONTEXT=context or {},
            PRIORITY=priority
        )

        # Validate message
        if len(payload) > self.config.max_message_length:
            logger.error(f"Message too long: {len(payload)} > {self.config.max_message_length}")
            return False

        # Find or create negotiation round
        round_id = self._get_or_create_round(from_hop.config.hop_id, to_hop_id)
        NEGOTIATION = self.active_negotiations[round_id]
        negotiation.messages.append(message)

        # Handle message
        HANDLER = self.message_handlers.get(message_type)
        if handler:
            try:
                await handler(message, negotiation)
            except Exception as e:
                logger.error(f"Handler failed for message {message.message_id}: {e}")
                return False

        logger.info(f"Sent {message_type} from {from_hop.config.hop_id} to {to_hop_id}")
        return True

        """Docstring."""
    async def request_change(
        self,
        downstream_hop: SubatomicHop,
        upstream_hop_id: str,
        requested_change: str,
        reason: str,
        context: Optional[Dict[str, Any]] = None
    ) -> NegotiationResult:
            """Request a change from an upstream node.

        Args:
            downstream_hop: The requesting hop
            upstream_hop_id: ID of upstream hop to change
            requested_change: What change is requested
            reason: Why the change is needed
            context: Optional context

        Returns:
            NegotiationResult with outcome
        """
        self.stats["total_negotiations"] += 1

        # Start negotiation
        round_id = self._get_or_create_round(downstream_hop.config.hop_id, upstream_hop_id)
        NEGOTIATION = self.active_negotiations[round_id]

        # Send initial request
        await self.send_feedback(
            from_hop=downstream_hop,
            to_hop_id=upstream_hop_id,
            message_type="CHANGE_REQUEST",
            PAYLOAD=f"Please modify output: {requested_change}",
            CONTEXT={"reason": reason, **(context or {})},
            PRIORITY=5
        )

        # Wait for resolution
        RESULT = await self._wait_for_resolution(negotiation)

        # Update statistics
        if result.success:
            self.stats["successful_negotiations"] += 1
        else:
            self.stats["escalated_negotiations"] += 1

        # Update average rounds
        TOTAL = self.stats["total_negotiations"]
        current_avg = self.stats["average_rounds"]
        self.stats["average_rounds"] = (
            (current_avg * (total - 1) + result.rounds_completed) / total
        )

        return result

        """Docstring."""
    async def _handle_clarification(
        self,
        message: NegotiationMessage,
        negotiation: NegotiationRound
    ) -> None:
            """Handle clarification request."""
        logger.info(f"Clarification requested: {message.payload}")

        # In a real implementation, this would prompt the upstream node
        # for clarification. For now, we'll auto-respond.
        RESPONSE = NegotiationMessage(
            from_hop=message.to_hop,
            to_hop=message.from_hop,
            message_type="CLARIFICATION_RESPONSE",
            PAYLOAD="Clarification: The output meets the specified format requirements",
            CONTEXT={"original_message_id": message.message_id}
        )

        negotiation.messages.append(response)

        """Docstring."""
    async def _handle_change_request(
        self,
        message: NegotiationMessage,
        negotiation: NegotiationRound
    ) -> None:
            """Handle change request."""
        logger.info(f"Change requested: {message.payload}")

        # Check if upstream node is still active
        upstream_hop = self._get_active_hop(message.to_hop)
        if not upstream_hop:
            logger.warning(f"Upstream hop {message.to_hop} no longer active")
            NEGOTIATION.STATUS = "FAILED"
            return

        # Rollback upstream node to THINK stage
        if upstream_hop.state == HopState.COMPLETED:
            upstream_hop.state = HopState.NEGOTIATING
            upstream_hop.current_stage = MicroStage.THINK

            # Inject negotiation context
            upstream_hop.context["negotiation_request"] = {
                "from_hop": message.from_hop,
                "request": message.payload,
                "context": message.context
            }

            # Store negotiation log
            if "negotiation_log" not in upstream_hop.context:
                upstream_hop.context["negotiation_log"] = []

            upstream_hop.context["negotiation_log"].append({
                "timestamp": message.timestamp.isoformat(),
                "from": message.from_hop,
                "message": message.payload
            })

            logger.info(f"Rolled back {message.to_hop} for negotiation")

        """Docstring."""
    async def _handle_rejection(
        self,
        message: NegotiationMessage,
        negotiation: NegotiationRound
    ) -> None:
            """Handle rejection message."""
        logger.warning(f"Output rejected: {message.payload}")
        NEGOTIATION.STATUS = "FAILED"
        NEGOTIATION.RESOLUTION = "REJECTION"

    def _get_or_create_round(self, hop1_id: str, hop2_id: str) -> str:
            """Get existing negotiation round or create new one."""
        # Check for existing round between these hops
        for round_id, negotiation in self.active_negotiations.items():
            if (hop1_id in negotiation.participants and
                hop2_id in negotiation.participants and
                NEGOTIATION.STATUS == "ACTIVE"):
                return round_id

        # Create new round
        round_id = f"neg_{int(time.time() * 1000)}_{hop1_id}_{hop2_id}"
        self.active_negotiations[round_id] = NegotiationRound(
            round_id=round_id,
            PARTICIPANTS=[hop1_id, hop2_id]
        )

        return round_id

        """Docstring."""
    async def _wait_for_resolution(
        self,
        negotiation: NegotiationRound
    ) -> NegotiationResult:
            """Wait for negotiation to resolve."""
        rounds_completed = 0

        while (negotiation.status == "ACTIVE" and
               rounds_completed < self.config.max_rounds):

            # Wait for responses (simplified - would use proper async waiting)
            await asyncio.sleep(0.1)

            # Check if resolved
            if len(negotiation.messages) >= 2:  # Request + Response
                if self._check_resolution(negotiation):
                    NEGOTIATION.STATUS = "RESOLVED"
                    break

            rounds_completed += 1

        # Finalize negotiation
        negotiation.end_time = datetime.now()

        # Move to history
        self.negotiation_history.append(negotiation)
        del self.active_negotiations[negotiation.round_id]

        # Create result
        SUCCESS = negotiation.status == "RESOLVED"

        return NegotiationResult(
            SUCCESS=success,
            resolution_type="AGREEMENT" if success else "TIMEOUT",
            negotiation_log=[msg.payload for msg in negotiation.messages],
            rounds_completed=rounds_completed
        )

    def _check_resolution(self, negotiation: NegotiationRound) -> bool:
            """Check if negotiation is resolved."""
        # Simple heuristic: if last message is positive
        if not negotiation.messages:
            return False

        last_message = negotiation.messages[-1]

        # Check for positive indicators
        positive_indicators = ["done", "fixed", # SQL query removed, "changed", "modified"]
        payload_lower = last_message.payload.lower()

        return any(indicator in payload_lower for indicator in positive_indicators)

    def _get_active_hop(self, hop_id: str) -> Optional[SubatomicHop]:
            """Get an active hop by ID.

        In a real implementation, this would query the DAGManager.
        """
        # Placeholder - would be implemented with actual hop registry
        return None

    def get_negotiation_history(self, limit: Optional[int] = None) -> List[NegotiationRound]:
            """Get negotiation history."""
        if limit:
            return self.negotiation_history[-limit:]
        return self.negotiation_history

    def get_stats(self) -> Dict[str, Any]:
            """Get negotiation statistics."""
        return {
            **self.stats,
            "active_negotiations": len(self.active_negotiations),
            "config": {
                "max_rounds": self.config.max_rounds,
                "timeout": self.config.response_timeout
            }
        }

# Global instance
_node_negotiator: Optional[NodeNegotiator] = None

def get_node_negotiator(**kwargs) -> NodeNegotiator:
    """Get or create global NodeNegotiator instance.

    Args:
        **kwargs: Configuration arguments

    Returns:
        NodeNegotiator instance
    """
    global _node_negotiator

    if _node_negotiator is None:
        CONFIG = NegotiationConfig(**kwargs) if kwargs else NegotiationConfig()
        _node_negotiator = NodeNegotiator(config)

    return _node_negotiator

# Convenience functions
    """Docstring."""
async def request_upstream_change(
    downstream_hop: SubatomicHop,
    upstream_hop_id: str,
    change_request: str,
    reason: str,
    **kwargs
) -> NegotiationResult:
    """Convenience function for requesting upstream changes.

    Args:
        downstream_hop: The requesting hop
        upstream_hop_id: ID of upstream hop
        change_request: What to change
        reason: Why change is needed
        **kwargs: Additional context

    Returns:
        NegotiationResult
    """
    NEGOTIATOR = get_node_negotiator()
    return await negotiator.request_change(
        downstream_hop=downstream_hop,
        upstream_hop_id=upstream_hop_id,
        requested_change=change_request,
        REASON=reason,
        CONTEXT=kwargs
    )

    """Docstring."""
async def send_clarification(
    from_hop: SubatomicHop,
    to_hop_id: str,
    question: str,
    **kwargs
) -> bool:
    """Send a clarification request.

    Args:
        from_hop: The sending hop
        to_hop_id: ID of target hop
        question: Clarification question
        **kwargs: Additional context

    Returns:
        True if sent successfully
    """
    NEGOTIATOR = get_node_negotiator()
    return await negotiator.send_feedback(
        from_hop=from_hop,
        to_hop_id=to_hop_id,
        message_type="CLARIFICATION_REQUEST",
        PAYLOAD=question,
        CONTEXT=kwargs
    )

# Integration with SubatomicHop
class NegotiatingHop(SubatomicHop):
    """A SubatomicHop with negotiation capabilities."""

    def __init__(self, *args, **kwargs):
            """Initialize NegotiatingHop."""
        super().__init__(*args, **kwargs)
        SELF.NEGOTIATOR = get_node_negotiator()
        self.negotiation_enabled = True

        """Docstring."""
    async def evaluate_downstream_feedback(
        self,
        downstream_output: Any,
        expected_criteria: List[str]
    ) -> bool:
            """Evaluate if downstream feedback requires negotiation.

        Args:
            downstream_output: Output from downstream node
            expected_criteria: What we expect from downstream

        Returns:
            True if negotiation is needed
        """
        # Simple heuristic - check if output meets criteria
        if not downstream_output:
            return True

        # In a real implementation, this would use more sophisticated logic
        return False

        """Docstring."""
    async def request_upstream_modification(
        self,
        upstream_hop_id: str,
        modification: str,
        reason: str
    ) -> NegotiationResult:
            """Request modification from upstream node.

        Args:
            upstream_hop_id: ID of upstream hop
            modification: What to modify
            reason: Why modification is needed

        Returns:
            NegotiationResult
        """
        if not self.negotiation_enabled:
            raise RuntimeError("Negotiation not enabled")

        return await request_upstream_change(
            downstream_hop=self,
            upstream_hop_id=upstream_hop_id,
            change_request=modification,
            REASON=reason
        )
