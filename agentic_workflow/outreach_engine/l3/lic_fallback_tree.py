"""LIC Fallback Tree - L3 orchestration for static fallback topology.

Implements nuclear prompt requirements for deterministic fallback logic:
- Encode static fallback topology for LIC archetypes and stages
- L3 only: pure topology, no business logic or safety
- Exec → Senior_TA → Recruiter standard chain with failure type escalation logic
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class LICFallbackNode:
    """Single node in the LIC fallback tree."""
    archetype: str                       # current archetype
    next_archetype: Optional[str]        # next archetype to try
    reason: str                          # reason for fallback decision
    stage: str                           # stage of the process
    metadata: Dict[str, Any] = field(default_factory=dict)


class LICFallbackTree:
    """L3 orchestrator for LIC archetype fallback topology.
    
    Encodes static fallback decisions based on archetype,
    failure type, and escalation level without business logic.
    """
    
    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        """Initialize LIC fallback tree."""
        self.telemetry_bus = telemetry_bus
        
        # Static fallback topology
        self.fallback_chain = {
            "EXECUTIVE": "SENIOR_TA",
            "SENIOR_TA": "RECRUITER", 
            "RECRUITER": "OTHER",
            "OTHER": None,  # Terminal node
        }
        
        # Failure type escalation rules
        self.failure_escalation = {
            # Creative failures: continue on same archetype
            "creative": {
                "ALLOW": {"continue_same": True, "fallback": False},
                "RETRY": {"continue_same": True, "fallback": False},
                "BLOCK": {"continue_same": False, "fallback": True},
            },
            # Safety failures: always fallback or terminate
            "safety": {
                "ALLOW": {"continue_same": True, "fallback": False},
                "RETRY": {"continue_same": False, "fallback": True},
                "BLOCK": {"continue_same": False, "fallback": False},  # Terminal
            },
            # Technical failures: fallback after retries
            "technical": {
                "ALLOW": {"continue_same": True, "fallback": False},
                "RETRY": {"continue_same": True, "fallback": False},
                "BLOCK": {"continue_same": False, "fallback": True},
            },
            # Other/unknown failures: conservative fallback
            "other": {
                "ALLOW": {"continue_same": True, "fallback": False},
                "RETRY": {"continue_same": False, "fallback": True},
                "BLOCK": {"continue_same": False, "fallback": True},
            },
        }
        
        # Stage-specific fallback rules
        self.stage_rules = {
            "planning": {
                "max_attempts": 2,
                "require_fallback_on_block": True,
            },
            "execution": {
                "max_attempts": 3,
                "require_fallback_on_block": False,
            },
            "validation": {
                "max_attempts": 2,
                "require_fallback_on_block": True,
            },
        }
    
    def get_next(
        self,
        current_archetype: str,
        failure_type: str,
        escalation_level: str,
        stage: str = "execution",
    ) -> Optional[LICFallbackNode]:
        """Get next fallback node based on current state.
        
        Args:
            current_archetype: Current archetype being attempted
            failure_type: Type of failure ("creative", "safety", "technical", "other")
            escalation_level: Escalation level ("ALLOW", "RETRY", "BLOCK")
            stage: Current stage of the process
            
        Returns:
            Next fallback node or None if no fallback available
        """
        try:
            # 1. Check if we should continue with same archetype
            if self._should_continue_same(current_archetype, failure_type, escalation_level, stage):
                return LICFallbackNode(
                    archetype=current_archetype,
                    next_archetype=current_archetype,
                    reason=f"Continue same archetype after {escalation_level}",
                    stage=stage,
                    metadata={"fallback_type": "continue_same"},
                )
            
            # 2. Check if we should fallback to next archetype
            next_archetype = self._get_next_archetype(current_archetype)
            if next_archetype and self._should_fallback(current_archetype, failure_type, escalation_level):
                return LICFallbackNode(
                    archetype=current_archetype,
                    next_archetype=next_archetype,
                    reason=f"Fallback from {current_archetype} to {next_archetype} after {escalation_level}",
                    stage=stage,
                    metadata={
                        "fallback_type": "archetype_fallback",
                        "failure_type": failure_type,
                        "escalation_level": escalation_level,
                    },
                )
            
            # 3. Check if we should terminate
            if self._should_terminate(current_archetype, failure_type, escalation_level):
                return LICFallbackNode(
                    archetype=current_archetype,
                    next_archetype=None,
                    reason=f"Terminate process after {escalation_level} in {current_archetype}",
                    stage=stage,
                    metadata={"fallback_type": "terminate"},
                )
            
            # 4. Default: no fallback available
            return None
            
        except Exception as e:
            logger.error(f"Fallback tree error: {e}")
            return LICFallbackNode(
                archetype=current_archetype,
                next_archetype=None,
                reason=f"Error in fallback tree: {str(e)}",
                stage=stage,
                metadata={"error": str(e)},
            )
    
    def _should_continue_same(
        self,
        current_archetype: str,
        failure_type: str,
        escalation_level: str,
        stage: str,
    ) -> bool:
        """Check if we should continue with the same archetype."""
        # Get escalation rules for this failure type
        failure_rules = self.failure_escalation.get(failure_type, {})
        escalation_rules = failure_rules.get(escalation_level, {})
        
        return escalation_rules.get("continue_same", False)
    
    def _should_fallback(
        self,
        current_archetype: str,
        failure_type: str,
        escalation_level: str,
    ) -> bool:
        """Check if we should fallback to next archetype."""
        # Get escalation rules for this failure type
        failure_rules = self.failure_escalation.get(failure_type, {})
        escalation_rules = failure_rules.get(escalation_level, {})
        
        return escalation_rules.get("fallback", False)
    
    def _should_terminate(
        self,
        current_archetype: str,
        failure_type: str,
        escalation_level: str,
    ) -> bool:
        """Check if we should terminate the process."""
        # Check if current archetype is terminal
        if current_archetype == "OTHER":
            return True
        
        # Check if escalation level requires termination
        if failure_type == "safety" and escalation_level == "BLOCK":
            return True
        
        # Check if no next archetype available and escalation is not ALLOW
        next_archetype = self._get_next_archetype(current_archetype)
        if not next_archetype and escalation_level != "ALLOW":
            return True
        
        return False
    
    def _get_next_archetype(self, current_archetype: str) -> Optional[str]:
        """Get the next archetype in the fallback chain."""
        return self.fallback_chain.get(current_archetype)
    
    def get_fallback_path(self, start_archetype: str) -> List[str]:
        """Get the complete fallback path from a starting archetype.
        
        Args:
            start_archetype: Starting archetype
            
        Returns:
            List of archetypes in fallback order
        """
        path = []
        current = start_archetype
        
        while current and current not in path:  # Prevent infinite loops
            path.append(current)
            current = self._get_next_archetype(current)
        
        return path
    
    def is_terminal_archetype(self, archetype: str) -> bool:
        """Check if an archetype is terminal (no further fallbacks).
        
        Args:
            archetype: Archetype to check
            
        Returns:
            True if terminal, False otherwise
        """
        return self._get_next_archetype(archetype) is None
    
    def can_fallback_from_failure(
        self,
        current_archetype: str,
        failure_type: str,
        escalation_level: str,
    ) -> bool:
        """Check if fallback is possible for given failure conditions.
        
        Args:
            current_archetype: Current archetype
            failure_type: Type of failure
            escalation_level: Escalation level
            
        Returns:
            True if fallback is possible, False otherwise
        """
        # Check if we should terminate
        if self._should_terminate(current_archetype, failure_type, escalation_level):
            return False
        
        # Check if we have a next archetype
        next_archetype = self._get_next_archetype(current_archetype)
        if not next_archetype:
            return False
        
        # Check if fallback is allowed by escalation rules
        return self._should_fallback(current_archetype, failure_type, escalation_level)
    
    def get_max_attempts_for_stage(self, stage: str) -> int:
        """Get maximum allowed attempts for a given stage.
        
        Args:
            stage: Stage name
            
        Returns:
            Maximum number of attempts allowed
        """
        stage_config = self.stage_rules.get(stage, {})
        return stage_config.get("max_attempts", 3)
    
    def requires_fallback_on_block(self, stage: str) -> bool:
        """Check if stage requires fallback on block escalation.
        
        Args:
            stage: Stage name
            
        Returns:
            True if fallback required on block, False otherwise
        """
        stage_config = self.stage_rules.get(stage, {})
        return stage_config.get("require_fallback_on_block", False)
    
    def validate_fallback_decision(
        self,
        current_archetype: str,
        next_archetype: Optional[str],
        failure_type: str,
        escalation_level: str,
    ) -> bool:
        """Validate that a fallback decision follows the topology rules.
        
        Args:
            current_archetype: Current archetype
            next_archetype: Proposed next archetype
            failure_type: Type of failure
            escalation_level: Escalation level
            
        Returns:
            True if decision is valid, False otherwise
        """
        # If no fallback (same archetype), check if allowed
        if next_archetype == current_archetype:
            return self._should_continue_same(current_archetype, failure_type, escalation_level, "execution")
        
        # If terminating, check if allowed
        if next_archetype is None:
            return self._should_terminate(current_archetype, failure_type, escalation_level)
        
        # If falling back, check if it follows the chain
        expected_next = self._get_next_archetype(current_archetype)
        if next_archetype != expected_next:
            return False
        
        # Check if fallback is allowed for this failure
        return self._should_fallback(current_archetype, failure_type, escalation_level)
    
    def _safe_record_telemetry(self, fallback_node: LICFallbackNode) -> None:
        """Record telemetry event safely without breaking fallback logic."""
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(
                "lic_fallback_decision_made",
                layer="L3",
                payload={
                    "current_archetype": fallback_node.archetype,
                    "next_archetype": fallback_node.next_archetype,
                    "reason": fallback_node.reason,
                    "stage": fallback_node.stage,
                    "metadata": fallback_node.metadata,
                },
            )
        except Exception:
            # Telemetry failures should never break fallback logic
            logger.debug("Failed to record telemetry for LIC fallback tree")
