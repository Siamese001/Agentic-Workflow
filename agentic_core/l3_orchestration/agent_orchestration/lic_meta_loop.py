"""LIC Meta-Loop Router - L3 orchestration for archetype fallback sequences.

Implements nuclear prompt requirements for LIC meta-loop routing:
- Exec → Senior_TA → Recruiter fallback sequence with retry limits
- Safety + failure classification integration
- Circuit-breaking and retry limits
- Deterministic, async-safe orchestration only (L3 pure)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable

from l5.safety_validator import SafetyValidator
from l5.types import SafetyContext

logger = logging.getLogger(__name__)


@dataclass
class OutreachContext:
    """L3 orchestration DTO for outreach workflows."""
    recipient_profile: Dict[str, Any] = field(default_factory=dict)
    company_data: Dict[str, Any] = field(default_factory=dict)
    mission: Optional[str] = None
    target_archetype: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LICMetaLoopConfig:
    """Configuration for LIC meta-loop router."""
    archetype_order: List[str] = field(default_factory=lambda: ["EXECUTIVE", "SENIOR_TA", "RECRUITER"])
    max_retries_per_archetype: int = 3
    max_total_attempts: int = 9
    enable_circuit_breaker: bool = True


@dataclass
class LICFallbackHop:
    """Record of a fallback transition in the meta-loop."""
    from_archetype: str
    to_archetype: Optional[str]
    reason: str
    failure_type: str  # "factual" | "creative" | "safety" | "other"
    safety_severity: str  # LOW | MEDIUM | HIGH | CRITICAL
    attempts_used: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LICMetaLoopOutcome:
    """Result of LIC meta-loop execution."""
    success: bool
    final_archetype: Optional[str]
    final_message: Optional[str]
    safety_result: Optional[Any]  # SafetyResult
    failure_type: str  # "none" | "factual" | "creative" | "safety" | "other"
    escalation_level: str  # "ALLOW" | "REQUIRE_APPROVAL" | "BLOCK"
    fallback_chain: List[LICFallbackHop] = field(default_factory=list)
    attempts_total: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LICFailureInfo:
    """Classification result from LIC failure classifier."""
    failure_type: str  # "factual" | "creative" | "safety" | "other"
    should_retry: bool
    should_fallback: bool
    escalation_level: str  # "ALLOW" | "REQUIRE_APPROVAL" | "BLOCK"
    metadata: Dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class LICFailureClassifier(Protocol):
    """Protocol for LIC failure classifier (L5 component)."""
    
    async def classify(
        self,
        *,
        message: str,
        safety_result: Any,
        outreach_context: OutreachContext,
        archetype: str,
    ) -> LICFailureInfo:
        """Classify failure type and recommend action."""
        ...


@runtime_checkable
class LICCircuitBreaker(Protocol):
    """Protocol for LIC circuit breaker (L3 component)."""
    
    async def check_can_attempt(
        self,
        outreach_context: OutreachContext,
        attempts_total: int,
        archetype: str,
    ) -> bool:
        """Check if attempt is allowed (circuit not open)."""
        ...
    
    async def record_attempt(
        self,
        *,
        outreach_context: OutreachContext,
        archetype: str,
        success: bool,
        safety_result: Any,
        failure_type: str,
    ) -> None:
        """Record attempt outcome for circuit breaking logic."""
        ...


@runtime_checkable
class OutreachOrchestratorInterface(Protocol):
    """Protocol for outreach orchestrator to generate messages per archetype."""
    
    async def run_for_archetype(
        self,
        *,
        context: OutreachContext,
        archetype: str,
    ) -> str:
        """Generate outreach message for specific archetype."""
        ...


class LICMetaLoopRouter:
    """LIC meta-loop router implementing archetype fallback sequences."""
    
    def __init__(
        self,
        *,
        safety_validator: SafetyValidator,
        failure_classifier: LICFailureClassifier,
        outreach_orchestrator: OutreachOrchestratorInterface,
        circuit_breaker: Optional[LICCircuitBreaker] = None,
        config: Optional[LICMetaLoopConfig] = None,
        telemetry_bus: Optional[Any] = None,
    ) -> None:
        """Initialize LIC meta-loop router with dependencies."""
        self.safety_validator = safety_validator
        self.failure_classifier = failure_classifier
        self.outreach_orchestrator = outreach_orchestrator
        self.circuit_breaker = circuit_breaker
        self.config = config or LICMetaLoopConfig()
        self.telemetry_bus = telemetry_bus
        
        # Validate archetype order contains initial_archetype default
        if "EXECUTIVE" not in self.config.archetype_order:
            self.config.archetype_order.insert(0, "EXECUTIVE")
    
    async def run_meta_loop(
        self,
        *,
        outreach_context: OutreachContext,
        initial_archetype: str = "EXECUTIVE",
    ) -> LICMetaLoopOutcome:
        """Run the complete LIC meta-loop with fallback and retry logic."""
        # Initialize state
        fallback_chain: List[LICFallbackHop] = []
        attempts_total = 0
        
        # Determine starting position in archetype sequence
        archetype_sequence = self._get_archetype_sequence(initial_archetype)
        
        self._safe_record_telemetry("lic_meta_loop_start", {
            "initial_archetype": initial_archetype,
            "archetype_sequence": archetype_sequence,
            "max_total_attempts": self.config.max_total_attempts,
        })
        
        # Process each archetype in sequence
        for archetype in archetype_sequence:
            if attempts_total >= self.config.max_total_attempts:
                break
                
            # Run archetype loop with retries
            outcome, hop, new_attempts_total = await self._run_archetype_loop(
                archetype=archetype,
                outreach_context=outreach_context,
                attempts_total_so_far=attempts_total,
            )
            
            attempts_total = new_attempts_total
            if hop:
                fallback_chain.append(hop)
            
            # If we got a final outcome (success or terminal failure), return it
            if outcome:
                outcome.fallback_chain = fallback_chain
                outcome.attempts_total = attempts_total
                
                self._safe_record_telemetry("lic_meta_loop_end", {
                    "success": outcome.success,
                    "final_archetype": outcome.final_archetype,
                    "failure_type": outcome.failure_type,
                    "attempts_total": attempts_total,
                    "fallback_chain_length": len(fallback_chain),
                })
                
                return outcome
        
        # All archetypes exhausted without success
        terminal_outcome = self._build_outcome_terminal_failure(
            failure_type="other",
            escalation_level="BLOCK",
            reason="All archetype attempts exhausted",
            fallback_chain=fallback_chain,
            attempts_total=attempts_total,
        )
        
        self._safe_record_telemetry("lic_meta_loop_end", {
            "success": False,
            "failure_type": "other",
            "attempts_total": attempts_total,
            "fallback_chain_length": len(fallback_chain),
        })
        
        return terminal_outcome
    
    async def _run_archetype_loop(
        self,
        archetype: str,
        outreach_context: OutreachContext,
        attempts_total_so_far: int,
    ) -> Tuple[Optional[LICMetaLoopOutcome], Optional[LICFallbackHop], int]:
        """Run retry loop for a single archetype."""
        attempts_used = 0
        failure_info = None  # Store outside loop for post-loop assessment
        safety_result = None  # Store outside loop for post-loop assessment
        max_attempts = min(
            self.config.max_retries_per_archetype,
            self.config.max_total_attempts - attempts_total_so_far
        )
        
        while attempts_used < max_attempts:
            attempts_used += 1
            current_total_attempts = attempts_total_so_far + attempts_used
            
            # Circuit breaker check
            if self.config.enable_circuit_breaker and self.circuit_breaker:
                can_attempt = await self.circuit_breaker.check_can_attempt(
                    outreach_context=outreach_context,
                    archetype=archetype,
                    attempts_total=current_total_attempts,
                )
                if not can_attempt:
                    hop = LICFallbackHop(
                        from_archetype=archetype,
                        to_archetype=None,
                        reason="Circuit breaker open",
                        failure_type="safety",
                        safety_severity="HIGH",
                        attempts_used=attempts_used,
                        metadata={"circuit_breaker_open": True},
                    )
                    outcome = self._build_outcome_terminal_block(
                        failure_type="safety",
                        hop=hop,
                        attempts_total=current_total_attempts,
                    )
                    return outcome, hop, current_total_attempts
            
            # Attempt message generation and validation
            try:
                message, safety_result, failure_info = await self._attempt_single_message(
                    archetype=archetype,
                    outreach_context=outreach_context,
                )
            except Exception as e:
                logger.error(f"Error in attempt for {archetype}: {e}")
                # Create failure info for exception
                failure_info = LICFailureInfo(
                    failure_type="other",
                    should_retry=attempts_used < max_attempts,
                    should_fallback=attempts_used >= max_attempts,
                    escalation_level="BLOCK",
                    metadata={"exception": str(e)},
                )
                safety_result = type('MockSafetyResult', (), {
                    'passes': False,
                    'severity': 'HIGH',
                    'metadata': {'failure_type': 'other'}
                })()
                message = f"Error generating message: {str(e)}"
            
            # Record attempt with circuit breaker
            if self.config.enable_circuit_breaker and self.circuit_breaker:
                await self.circuit_breaker.record_attempt(
                    outreach_context=outreach_context,
                    archetype=archetype,
                    success=safety_result.passes and failure_info.escalation_level == "ALLOW",
                    safety_result=safety_result,
                    failure_type=failure_info.failure_type,
                )
            
            # Check for success
            if safety_result.passes and failure_info.escalation_level == "ALLOW":
                outcome = self._build_outcome_success(
                    message=message,
                    archetype=archetype,
                    safety_result=safety_result,
                    attempts_total=current_total_attempts,
                )
                return outcome, None, current_total_attempts
            
            # Handle failure based on classification
            if failure_info.escalation_level == "BLOCK":
                hop = LICFallbackHop(
                    from_archetype=archetype,
                    to_archetype=None,
                    reason=f"Block escalation: {failure_info.failure_type}",
                    failure_type=failure_info.failure_type,
                    safety_severity=getattr(safety_result, 'severity', 'HIGH'),
                    attempts_used=attempts_used,
                    metadata=failure_info.metadata,
                )
                outcome = self._build_outcome_terminal_block(
                    failure_type=failure_info.failure_type,
                    hop=hop,
                    attempts_total=current_total_attempts,
                )
                return outcome, hop, current_total_attempts
            
            # Retry logic
            if (failure_info.should_retry and 
                attempts_used < max_attempts):
                self._safe_record_telemetry("lic_meta_loop_retry", {
                    "archetype": archetype,
                    "attempt": attempts_used,
                    "failure_type": failure_info.failure_type,
                })
                continue
            
            # Fallback logic
            if failure_info.should_fallback:
                next_archetype = self._get_next_archetype(archetype)
                hop = LICFallbackHop(
                    from_archetype=archetype,
                    to_archetype=next_archetype,
                    reason=f"Fallback: {failure_info.failure_type}",
                    failure_type=failure_info.failure_type,
                    safety_severity=getattr(safety_result, 'severity', 'MEDIUM'),
                    attempts_used=attempts_used,
                    metadata=failure_info.metadata,
                )
                return None, hop, current_total_attempts
            
            # Terminal failure for this archetype
            hop = LICFallbackHop(
                from_archetype=archetype,
                to_archetype=self._get_next_archetype(archetype),
                reason=f"Terminal failure: {failure_info.failure_type}",
                failure_type=failure_info.failure_type,
                safety_severity=getattr(safety_result, 'severity', 'MEDIUM'),
                attempts_used=attempts_used,
                metadata=failure_info.metadata,
            )
            return None, hop, current_total_attempts
        
        # Max retries reached for archetype - check if last failure indicated fallback
        next_archetype = self._get_next_archetype(archetype)
        
        # Check if we have a failure_info from the last attempt that indicates fallback
        # This handles the case where retries are exhausted but fallback should occur
        if failure_info and failure_info.should_fallback:
            hop = LICFallbackHop(
                from_archetype=archetype,
                to_archetype=next_archetype,
                reason=f"Fallback after max retries: {failure_info.failure_type}",
                failure_type=failure_info.failure_type,
                safety_severity=getattr(safety_result, 'severity', 'MEDIUM'),
                attempts_used=attempts_used,
                metadata=failure_info.metadata,
            )
            return None, hop, current_total_attempts
        
        # Default: max retries reached without fallback indication
        hop = LICFallbackHop(
            from_archetype=archetype,
            to_archetype=next_archetype,
            reason="Max retries reached",
            failure_type="other",
            safety_severity="MEDIUM",
            attempts_used=attempts_used,
        )
        return None, hop, current_total_attempts
    
    async def _attempt_single_message(
        self,
        archetype: str,
        outreach_context: OutreachContext,
    ) -> Tuple[str, Any, LICFailureInfo]:
        """Generate and validate a single message attempt."""
        # Generate message via outreach orchestrator
        message = await self.outreach_orchestrator.run_for_archetype(
            context=outreach_context,
            archetype=archetype,
        )
        
        # Safety validation
        safety_context = SafetyContext(
            content=message,
            content_type="text",
            domain="outreach",
            metadata={
                "archetype": archetype,
                "context": outreach_context.metadata,
            }
        )
        
        safety_result = self.safety_validator.evaluate(safety_context)
        
        # Handle async safety results
        if asyncio.iscoroutine(safety_result):
            safety_result = await safety_result
        
        # Failure classification
        failure_info = await self.failure_classifier.classify(
            message=message,
            safety_result=safety_result,
            outreach_context=outreach_context,
            archetype=archetype,
        )
        
        return message, safety_result, failure_info
    
    def _get_archetype_sequence(self, initial_archetype: str) -> List[str]:
        """Get ordered archetype sequence starting from initial_archetype."""
        if initial_archetype not in self.config.archetype_order:
            return self.config.archetype_order
        
        start_idx = self.config.archetype_order.index(initial_archetype)
        return self.config.archetype_order[start_idx:]
    
    def _get_next_archetype(self, current_archetype: str) -> Optional[str]:
        """Get next archetype in sequence, or None if current is last."""
        try:
            idx = self.config.archetype_order.index(current_archetype)
            if idx + 1 < len(self.config.archetype_order):
                return self.config.archetype_order[idx + 1]
        except ValueError:
            pass
        return None
    
    def _build_outcome_success(
        self,
        message: str,
        archetype: str,
        safety_result: Any,
        attempts_total: int,
    ) -> LICMetaLoopOutcome:
        """Build successful outcome."""
        return LICMetaLoopOutcome(
            success=True,
            final_archetype=archetype,
            final_message=message,
            safety_result=safety_result,
            failure_type="none",
            escalation_level="ALLOW",
            attempts_total=attempts_total,
            metadata={"completion_reason": "success"},
        )
    
    def _build_outcome_terminal_block(
        self,
        failure_type: str,
        hop: LICFallbackHop,
        attempts_total: int,
    ) -> LICMetaLoopOutcome:
        """Build terminal blocked outcome."""
        return LICMetaLoopOutcome(
            success=False,
            final_archetype=hop.from_archetype,
            final_message=None,
            safety_result=None,
            failure_type=failure_type,
            escalation_level="BLOCK",
            attempts_total=attempts_total,
            metadata={
                "completion_reason": "blocked",
                "block_reason": hop.reason,
                **hop.metadata,
            },
        )
    
    def _build_outcome_terminal_failure(
        self,
        failure_type: str,
        escalation_level: str,
        reason: str,
        fallback_chain: List[LICFallbackHop],
        attempts_total: int,
    ) -> LICMetaLoopOutcome:
        """Build terminal failure outcome."""
        return LICMetaLoopOutcome(
            success=False,
            final_archetype=None,
            final_message=None,
            safety_result=None,
            failure_type=failure_type,
            escalation_level=escalation_level,
            fallback_chain=fallback_chain,
            attempts_total=attempts_total,
            metadata={"completion_reason": reason},
        )
    
    def _safe_record_telemetry(self, event: str, payload: Dict[str, Any]) -> None:
        """Record telemetry event safely without breaking control flow."""
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(event, "L3", payload)
        except Exception:
            # Telemetry failures should never break workflow
            pass
