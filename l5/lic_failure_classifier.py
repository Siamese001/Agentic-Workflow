"""LIC Failure Classifier - L5 policy engine for interpreting safety violations.

Implements nuclear prompt requirements for deterministic failure classification:
- Analyzes SafetyResult violations to determine failure type (factual/creative/safety/other/none)
- Maps severity levels to escalation decisions (ALLOW/REQUIRE_APPROVAL/BLOCK)
- Drives L3 meta-loop retry/fallback decisions with archetype-specific tuning
- Pure L5 logic with no external I/O or cross-layer mutations
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from l5.safety_validator import SafetyResult, SafetyViolation

logger = logging.getLogger(__name__)

# Severity ordering for consistent comparisons
SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
SEVERITY_RANK = {severity: idx for idx, severity in enumerate(SEVERITY_ORDER)}


@dataclass
class LICFailureClassifierConfig:
    """Configuration for LIC failure classification and routing policy."""
    factual_block_severity_min: str = "HIGH"          # severity level at/above which factual issues BLOCK
    safety_block_severity_min: str = "HIGH"           # severity level at/above which safety issues BLOCK
    creative_retry_limit: int = 1                     # max creative retries per archetype
    factual_retry_limit: int = 0                      # factual retries per archetype (usually 0)
    default_escalation_for_creative: str = "REQUIRE_APPROVAL"
    default_escalation_for_factual: str = "BLOCK"
    default_escalation_for_safety: str = "BLOCK"
    default_escalation_for_other: str = "REQUIRE_APPROVAL"


@dataclass
class LICFailureInfo:
    """L5-level interpretation of a single message attempt.
    
    Used by L3 LICMetaLoopRouter to decide retry/fallback/block.
    """
    failure_type: str                      # "none" | "factual" | "creative" | "safety" | "other"
    should_retry: bool
    should_fallback: bool
    escalation_level: str                  # "ALLOW" | "REQUIRE_APPROVAL" | "BLOCK"
    attempt_index_for_archetype: int       # 1-based index within current archetype loop
    metadata: Dict[str, Any] = field(default_factory=dict)


class LICFailureClassifier:
    """L5 policy engine for classifying message generation failures.
    
    Interprets SafetyResult violations and applies deterministic rules
    to guide L3 meta-loop retry/fallback/block decisions.
    """
    
    def __init__(
        self,
        *,
        config: Optional[LICFailureClassifierConfig] = None,
        telemetry_bus: Optional[Any] = None,
    ) -> None:
        """Initialize LIC failure classifier with configuration."""
        self.config = config or LICFailureClassifierConfig()
        self.telemetry_bus = telemetry_bus
        
        logger.debug(f"LIC Failure Classifier initialized: {self.config}")
    
    async def classify(
        self,
        *,
        message: str,
        safety_result: SafetyResult,
        outreach_context: "OutreachContext",
        archetype: str,
        attempt_index_for_archetype: int,
    ) -> LICFailureInfo:
        """Classify a message attempt outcome for meta-loop routing.
        
        Args:
            message: Generated message content
            safety_result: Safety validation result with violations
            outreach_context: L3 outreach context (treated as opaque)
            archetype: Current archetype being attempted
            attempt_index_for_archetype: 1-based attempt index within archetype
            
        Returns:
            LICFailureInfo with classification and routing decisions
        """
        # 1. Determine failure type from SafetyResult violations
        failure_type = self._determine_failure_type(safety_result)
        
        # 2. Compute escalation level based on failure type and severity
        escalation_level = self._compute_escalation_level(
            failure_type, safety_result.severity
        )
        
        # 3. Apply archetype-specific tuning to retry limits
        effective_creative_limit, effective_factual_limit = self._get_effective_retry_limits(
            archetype
        )
        
        # 4. Decide retry/fallback based on classification and attempt index
        should_retry, should_fallback = self._compute_retry_fallback(
            failure_type=failure_type,
            escalation_level=escalation_level,
            attempt_index=attempt_index_for_archetype,
            creative_limit=effective_creative_limit,
            factual_limit=effective_factual_limit,
        )
        
        # 5. Build failure info with comprehensive metadata
        violation_codes = [v.code for v in safety_result.violations]
        metadata = {
            "violation_codes": violation_codes,
            "severity": safety_result.severity,
            "effective_creative_retry_limit": effective_creative_limit,
            "effective_factual_retry_limit": effective_factual_limit,
            "archetype": archetype,
            "message_length": len(message),
        }
        
        failure_info = LICFailureInfo(
            failure_type=failure_type,
            should_retry=should_retry,
            should_fallback=should_fallback,
            escalation_level=escalation_level,
            attempt_index_for_archetype=attempt_index_for_archetype,
            metadata=metadata,
        )
        
        # 6. Record telemetry (best-effort, non-blocking)
        self._safe_record_telemetry(failure_info, archetype, attempt_index_for_archetype)
        
        return failure_info
    
    def _determine_failure_type(self, safety_result: SafetyResult) -> str:
        """Determine failure type from SafetyResult violations and metadata.
        
        Classification precedence:
        1. No violations + passes → "none"
        2. Any violation with failure_type_hint == "factual" → "factual"
        3. Any violation with category == "safety" → "safety"
        4. Any violation with failure_type_hint == "creative" → "creative"
        5. SafetyResult.metadata.failure_type → that value
        6. Default → "other"
        
        Args:
            safety_result: Safety validation result
            
        Returns:
            Failure type string
        """
        # No violations and passes → no failure
        if not safety_result.violations and safety_result.passes:
            return "none"
        
        # Check violations for failure type hints and categories
        for violation in safety_result.violations:
            # Priority 1: Factual issues (highest precedence)
            if violation.metadata.get("failure_type_hint") == "factual":
                return "factual"
        
        # Second pass for safety and creative (lower precedence)
        for violation in safety_result.violations:
            # Priority 2: Safety category issues
            if violation.category == "safety":
                return "safety"
            
            # Priority 3: Creative issues
            if violation.metadata.get("failure_type_hint") == "creative":
                return "creative"
        
        # Check SafetyResult metadata for explicit failure type
        metadata_failure_type = safety_result.metadata.get("failure_type")
        if metadata_failure_type in {"factual", "creative", "safety", "other"}:
            return metadata_failure_type
        
        # Default fallback
        return "other"
    
    def _compute_escalation_level(
        self, 
        failure_type: str, 
        severity: str
    ) -> str:
        """Compute escalation level based on failure type and severity.
        
        Args:
            failure_type: Classified failure type
            severity: Safety result severity level
            
        Returns:
            Escalation level: "ALLOW" | "REQUIRE_APPROVAL" | "BLOCK"
        """
        if failure_type == "none":
            return "ALLOW"
        
        severity_rank = SEVERITY_RANK.get(severity, 0)
        
        if failure_type == "creative":
            if severity_rank <= SEVERITY_RANK["MEDIUM"]:
                # Low/medium creative issues may allow or require approval
                return self.config.default_escalation_for_creative
            else:
                # High/critical creative issues require configured escalation
                return self.config.default_escalation_for_creative
        
        elif failure_type == "factual":
            factual_min_rank = SEVERITY_RANK.get(self.config.factual_block_severity_min, 2)
            if severity_rank >= factual_min_rank:
                return "BLOCK"
            else:
                return self.config.default_escalation_for_factual
        
        elif failure_type == "safety":
            safety_min_rank = SEVERITY_RANK.get(self.config.safety_block_severity_min, 2)
            if severity_rank >= safety_min_rank:
                return "BLOCK"
            else:
                return self.config.default_escalation_for_safety
        
        elif failure_type == "other":
            return self.config.default_escalation_for_other
        
        # Fallback for unknown failure types
        return self.config.default_escalation_for_other
    
    def _get_effective_retry_limits(self, archetype: str) -> tuple[int, int]:
        """Get archetype-specific effective retry limits.
        
        Args:
            archetype: Current archetype string
            
        Returns:
            Tuple of (effective_creative_limit, effective_factual_limit)
        """
        base_creative = self.config.creative_retry_limit
        base_factual = self.config.factual_retry_limit
        
        # Archetype-specific tuning
        if archetype == "EXECUTIVE":
            # More strict on creative issues - fewer retries
            return max(0, base_creative - 1), base_factual
        
        elif archetype == "SENIOR_TA":
            # More strict on factual issues - no retries on factual
            return base_creative, 0
        
        elif archetype == "RECRUITER":
            # More tolerant of creative issues - allow one more retry
            return base_creative + 1, base_factual
        
        else:
            # Default behavior for unknown archetypes
            return base_creative, base_factual
    
    def _compute_retry_fallback(
        self,
        failure_type: str,
        escalation_level: str,
        attempt_index: int,
        creative_limit: int,
        factual_limit: int,
    ) -> tuple[bool, bool]:
        """Compute retry and fallback decisions.
        
        Args:
            failure_type: Classified failure type
            escalation_level: Computed escalation level
            attempt_index: Current attempt index (1-based)
            creative_limit: Effective creative retry limit
            factual_limit: Effective factual retry limit
            
        Returns:
            Tuple of (should_retry, should_fallback)
        """
        # No failures - no retry needed
        if failure_type == "none":
            return False, False
        
        # Creative failures - retry within limit, then fallback
        if failure_type == "creative":
            if attempt_index <= creative_limit:  # Use <= for inclusive limit
                return True, False
            else:
                return False, True
        
        # Factual failures - respect factual retry limit
        if failure_type == "factual":
            if factual_limit == 0:
                should_retry = False
            else:
                should_retry = attempt_index <= factual_limit  # Use <= for inclusive limit
            
            should_fallback = not should_retry and escalation_level != "BLOCK"
            return should_retry, should_fallback
        
        # Safety failures - generally block, no retry or fallback
        if failure_type == "safety":
            return False, False
        
        # Other failures - fallback unless blocked
        if failure_type == "other":
            return False, (escalation_level != "BLOCK")
        
        # Default fallback
        return False, False
    
    def _safe_record_telemetry(
        self, 
        failure_info: LICFailureInfo, 
        archetype: str, 
        attempt_index: int
    ) -> None:
        """Record telemetry event safely without breaking classification.
        
        Args:
            failure_info: Classification result
            archetype: Current archetype
            attempt_index: Attempt index within archetype
        """
        if not self.telemetry_bus:
            return
        
        try:
            self.telemetry_bus.record_event(
                "lic_failure_classification",
                layer="L5",
                payload={
                    "archetype": archetype,
                    "failure_type": failure_info.failure_type,
                    "escalation_level": failure_info.escalation_level,
                    "should_retry": failure_info.should_retry,
                    "should_fallback": failure_info.should_fallback,
                    "attempt_index_for_archetype": attempt_index,
                },
            )
        except Exception:
            # Telemetry failures should never break classification logic
            logger.debug("Failed to record telemetry for LIC failure classification")
