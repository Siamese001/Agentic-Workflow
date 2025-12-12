"""Control Plane for centralized safety policy routing.

Phase 1 - Pillar 9: Safety & Policy (Control Plane & Guardrails)
Provides unified defense system for prompt generation and output processing.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

from .pii_scrubber import PIIScrubber, PIIResult
from .bias_auditor import BiasAuditor, BiasResult
from .constitutional_ai import ConstitutionalAISystem, ConstitutionalReviewResult

logger = logging.getLogger(__name__)


class PolicyAction(Enum):
    """Actions the control plane can take."""
    ALLOW = "allow"
    BLOCK = "block"
    SANITIZE = "sanitize"
    WARN = "warn"
    REVIEW = "review"


@dataclass
class SafetyPolicy:
    """Safety policy configuration."""
    enable_pii_scrubbing: bool = True
    enable_bias_detection: bool = True
    enable_constitutional_review: bool = True
    block_on_pii: bool = False
    block_on_bias: bool = False
    block_on_violations: bool = False
    auto_sanitize: bool = True


@dataclass
class PolicyDecision:
    """Decision from control plane evaluation."""
    action: PolicyAction
    is_safe: bool
    pii_result: Optional[PIIResult] = None
    bias_result: Optional[BiasResult] = None
    constitutional_result: Optional[ConstitutionalReviewResult] = None
    sanitized_content: Optional[str] = None
    warnings: List[str] = None
    errors: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []
        if self.metadata is None:
            self.metadata = {}


class ControlPlane:
    """Centralized Control Plane for safety policy enforcement.
    
    Routes all agent inputs and outputs through unified defense system:
    - PII scrubbing for compliance
    - Bias detection for quality
    - Constitutional AI for alignment
    
    Integrates with prompt generation and output processing loops.
    """
    
    def __init__(
        self,
        policy: Optional[SafetyPolicy] = None,
        enable_logging: bool = True,
    ):
        """Initialize control plane.
        
        Args:
            policy: Safety policy configuration
            enable_logging: Enable logging of decisions
        """
        self.policy = policy or SafetyPolicy()
        self.enable_logging = enable_logging
        
        self.pii_scrubber = PIIScrubber(enable_logging=enable_logging)
        self.bias_auditor = BiasAuditor(enable_logging=enable_logging)
        self.constitutional_ai = ConstitutionalAISystem(enable_logging=enable_logging)
        
        self._decision_count = 0
        self._block_count = 0
    
    def evaluate_input(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PolicyDecision:
        """Evaluate input content before processing.
        
        Args:
            content: Input content to evaluate
            context: Optional context for evaluation
            
        Returns:
            PolicyDecision with action and results
        """
        return self._evaluate(content, context, is_input=True)
    
    def evaluate_output(
        self,
        content: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PolicyDecision:
        """Evaluate output content before delivery.
        
        Args:
            content: Output content to evaluate
            context: Optional context for evaluation
            
        Returns:
            PolicyDecision with action and results
        """
        return self._evaluate(content, context, is_input=False)
    
    def _evaluate(
        self,
        content: str,
        context: Optional[Dict[str, Any]],
        is_input: bool,
    ) -> PolicyDecision:
        """Internal evaluation logic.
        
        Args:
            content: Content to evaluate
            context: Optional context
            is_input: Whether this is input (vs output)
            
        Returns:
            PolicyDecision
        """
        self._decision_count += 1
        
        warnings: List[str] = []
        errors: List[str] = []
        sanitized_content = content
        
        pii_result: Optional[PIIResult] = None
        bias_result: Optional[BiasResult] = None
        constitutional_result: Optional[ConstitutionalReviewResult] = None
        
        # Step 1: PII Scrubbing
        if self.policy.enable_pii_scrubbing:
            pii_result = self.pii_scrubber.scrub_text(content)
            
            if pii_result.has_pii():
                warnings.append(f"Detected {len(pii_result.detected_pii)} PII items")
                
                if self.policy.auto_sanitize:
                    sanitized_content = pii_result.scrubbed_text
                
                if self.policy.block_on_pii:
                    errors.append("Content blocked due to PII detection")
                    return self._create_block_decision(
                        pii_result=pii_result,
                        warnings=warnings,
                        errors=errors,
                    )
        
        # Step 2: Bias Detection
        if self.policy.enable_bias_detection:
            bias_result = self.bias_auditor.audit_content(sanitized_content)
            
            if bias_result.has_bias:
                warnings.append(
                    f"Detected {len(bias_result.bias_types)} bias types: "
                    f"{[bt.value for bt in bias_result.bias_types]}"
                )
                
                if self.policy.block_on_bias:
                    errors.append("Content blocked due to bias detection")
                    return self._create_block_decision(
                        pii_result=pii_result,
                        bias_result=bias_result,
                        warnings=warnings,
                        errors=errors,
                    )
        
        # Step 3: Constitutional Review
        if self.policy.enable_constitutional_review:
            constitutional_result = self.constitutional_ai.review_content(
                sanitized_content,
                context,
            )
            
            if not constitutional_result.is_compliant:
                warnings.append(
                    f"Constitutional violations: {len(constitutional_result.violations)}"
                )
                
                if self.policy.block_on_violations:
                    errors.append("Content blocked due to constitutional violations")
                    return self._create_block_decision(
                        pii_result=pii_result,
                        bias_result=bias_result,
                        constitutional_result=constitutional_result,
                        warnings=warnings,
                        errors=errors,
                    )
        
        # Determine final action
        action = PolicyAction.ALLOW
        is_safe = True
        
        if errors:
            action = PolicyAction.BLOCK
            is_safe = False
        elif sanitized_content != content:
            action = PolicyAction.SANITIZE
        elif warnings:
            action = PolicyAction.WARN
        
        decision = PolicyDecision(
            action=action,
            is_safe=is_safe,
            pii_result=pii_result,
            bias_result=bias_result,
            constitutional_result=constitutional_result,
            sanitized_content=sanitized_content if action == PolicyAction.SANITIZE else None,
            warnings=warnings,
            errors=errors,
            metadata={
                "is_input": is_input,
                "decision_id": self._decision_count,
            },
        )
        
        if self.enable_logging:
            logger.info(
                "control_plane_decision",
                extra={
                    "action": action.value,
                    "is_safe": is_safe,
                    "is_input": is_input,
                    "has_pii": pii_result.has_pii() if pii_result else False,
                    "has_bias": bias_result.has_bias if bias_result else False,
                    "is_compliant": constitutional_result.is_compliant if constitutional_result else True,
                    "warning_count": len(warnings),
                    "error_count": len(errors),
                },
            )
        
        return decision
    
    def _create_block_decision(
        self,
        pii_result: Optional[PIIResult] = None,
        bias_result: Optional[BiasResult] = None,
        constitutional_result: Optional[ConstitutionalReviewResult] = None,
        warnings: Optional[List[str]] = None,
        errors: Optional[List[str]] = None,
    ) -> PolicyDecision:
        """Create a BLOCK decision.
        
        Args:
            pii_result: PII detection result
            bias_result: Bias detection result
            constitutional_result: Constitutional review result
            warnings: Warning messages
            errors: Error messages
            
        Returns:
            PolicyDecision with BLOCK action
        """
        self._block_count += 1
        
        return PolicyDecision(
            action=PolicyAction.BLOCK,
            is_safe=False,
            pii_result=pii_result,
            bias_result=bias_result,
            constitutional_result=constitutional_result,
            sanitized_content=None,
            warnings=warnings or [],
            errors=errors or [],
            metadata={
                "block_id": self._block_count,
            },
        )
    
    def get_stats(self) -> Dict[str, int]:
        """Get control plane statistics.
        
        Returns:
            Dict with decision and block counts
        """
        return {
            "total_decisions": self._decision_count,
            "total_blocks": self._block_count,
            "block_rate": self._block_count / max(1, self._decision_count),
        }


def create_control_plane(
    enable_pii_scrubbing: bool = True,
    enable_bias_detection: bool = True,
    enable_constitutional_review: bool = True,
    block_on_pii: bool = False,
    block_on_bias: bool = False,
    block_on_violations: bool = False,
) -> ControlPlane:
    """Factory function to create a control plane.
    
    Args:
        enable_pii_scrubbing: Enable PII detection
        enable_bias_detection: Enable bias detection
        enable_constitutional_review: Enable constitutional review
        block_on_pii: Block content with PII
        block_on_bias: Block content with bias
        block_on_violations: Block content with violations
        
    Returns:
        Configured ControlPlane instance
    """
    policy = SafetyPolicy(
        enable_pii_scrubbing=enable_pii_scrubbing,
        enable_bias_detection=enable_bias_detection,
        enable_constitutional_review=enable_constitutional_review,
        block_on_pii=block_on_pii,
        block_on_bias=block_on_bias,
        block_on_violations=block_on_violations,
    )
    
    return ControlPlane(policy=policy)
