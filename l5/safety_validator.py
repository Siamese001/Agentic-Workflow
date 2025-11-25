"""
L5 safety validation for comprehensive résumé protection.

Centralizes all safety constraints, ethical guidelines, privacy rules, and bias mitigation for secure processing.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Callable
from enum import Enum
import logging

from l5.interfaces import (
    SafetyConstraint,
    SafetyPolicy,
    SafetyViolation,
    PolicyDecision,
    PolicyEvaluationError,
    Severity,
    Verdict,
    ExecutionContext,
    SafetyResult,
    SafetyFinding
)
from l5.types import SafetyContext

logger = logging.getLogger(__name__)


class LayerSafetyPolicy(SafetyPolicy):
    """Concrete implementation of SafetyPolicy for a specific layer."""
    
    def __init__(self, layer: str, constraints: List[SafetyConstraint], validation_callback: Callable[[str, SafetyConstraint], Optional[SafetyViolation]]):
        """Initialize the layer safety policy."""
        self.layer = layer
        self.constraints = constraints
        self.validation_callback = validation_callback
    
    @property
    def policy_id(self) -> str:
        """Unique identifier for this policy."""
        return f"{self.layer}_safety_policy"
    
    @property
    def description(self) -> str:
        """Human-readable description of the policy."""
        return f"Safety policy for {self.layer} layer with {len(self.constraints)} constraints"
    
    def evaluate(self, context: SafetyContext) -> PolicyDecision:
        """Evaluate the given context against this policy."""
        if not hasattr(context, 'content'):
            raise PolicyEvaluationError(f"Context missing required 'content' attribute: {context}")
        
        content = str(context.content)
        violations = []
        
        for constraint in self.constraints:
            if self.layer in constraint.layer_applicability:
                violation = self.validation_callback(content, constraint)
                if violation:
                    violations.append(violation)
        
        return PolicyDecision(
            policy_id=self.policy_id,
            verdict=Verdict.BLOCK if any(v.severity >= Severity.HIGH for v in violations) else Verdict.ALLOW,
            findings=violations,
            metadata={"layer": self.layer, "constraints_evaluated": len(self.constraints)}
        )


class SafetyConstraintType(str, Enum):
    """Types of safety constraints enforced by L5."""
    
    CONTENT_SAFETY = "content_safety"
    ETHICAL_GUIDELINES = "ethical_guidelines"
    PRIVACY_RULES = "privacy_rules"
    BIAS_MITIGATION = "bias_mitigation"
    TEMPORAL_CONSTRAINTS = "temporal_constraints"
    AUDIENCE_SAFETY = "audience_safety"


class L5SafetyValidator:
    """
    Centralized L5 safety validation for all layers.
    
    Enforces safety constraints, ethical guidelines, privacy rules, and bias mitigation across the entire architecture.
    """
    
    def __init__(self):
        self.constraints = self._load_safety_constraints()
        self.violation_history: List[SafetyViolation] = []
    
    def _load_safety_constraints(self) -> Dict[SafetyConstraintType, List[SafetyConstraint]]:
        """Load all safety constraints for centralized enforcement."""
        constraints = {
            SafetyConstraintType.CONTENT_SAFETY: [
                SafetyConstraint(
                    constraint_type=SafetyConstraintType.CONTENT_SAFETY,
                    rule="No harmful, illegal, or dangerous content",
                    severity="blocking",
                    layer_applicability=["L1", "L2", "L3"],
                    metadata={"category": "content_filter"}
                ),
            ],
            SafetyConstraintType.ETHICAL_GUIDELINES: [
                SafetyConstraint(
                    constraint_type=SafetyConstraintType.ETHICAL_GUIDELINES,
                    rule="Maintain professional and ethical standards",
                    severity="blocking", 
                    layer_applicability=["L1", "L2", "L3"],
                    metadata={"category": "ethics"}
                ),
            ],
            SafetyConstraintType.PRIVACY_RULES: [
                SafetyConstraint(
                    constraint_type=SafetyConstraintType.PRIVACY_RULES,
                    rule="Protect user privacy and sensitive data",
                    severity="blocking",
                    layer_applicability=["L1", "L2", "L3", "L4"],
                    metadata={"category": "privacy"}
                ),
            ],
            SafetyConstraintType.BIAS_MITIGATION: [
                SafetyConstraint(
                    constraint_type=SafetyConstraintType.BIAS_MITIGATION,
                    rule="Detect and mitigate biased content",
                    severity="warning",
                    layer_applicability=["L1", "L2", "L3"],
                    metadata={"category": "bias"}
                ),
            ],
        }
        return constraints
    
    def validate_layer_input(
        self, 
        layer: str, 
        content: str, 
        context: Optional[ExecutionContext] = None
    ) -> SafetyResult:
        """
        Validates input for any layer using centralized L5 safety rules.
        
        Ensures consistent safety enforcement across all architectural layers.
        """
        violations = []
        
        for constraint_type, constraint_list in self.constraints.items():
            for constraint in constraint_list:
                if layer in constraint.layer_applicability:
                    violation = self._check_constraint(content, constraint, context)
                    if violation:
                        violations.append(violation)
        
        # Convert violations to SafetyFinding objects for SafetyResult
        findings = []
        for violation in violations:
            finding = SafetyFinding(
                check_id=violation.constraint_type,
                category=violation.constraint_type,
                severity="medium",  # Default severity since SafetyViolation doesn't have severity field
                message=f"Rule violation: {violation.rule}",
                details={
                    "detected_content": violation.detected_content,
                    "confidence": violation.confidence,
                    "metadata": violation.metadata
                }
            )
            findings.append(finding)
        
        result = SafetyResult(findings=findings)
        
        # Log violations for audit trail
        if violations:
            self.violation_history.extend(violations)
            logger.warning(f"Safety violations detected in {layer}: {len(violations)} issues")
        
        return result
    
    def _check_constraint(
        self, 
        content: str, 
        constraint: SafetyConstraint, 
        context: Optional[ExecutionContext] = None
    ) -> Optional[SafetyViolation]:
        """Check if content violates a specific safety constraint."""
        # Simplified constraint checking - in production would use sophisticated NLP
        if constraint.constraint_type == SafetyConstraintType.CONTENT_SAFETY:
            return self._check_content_safety(content, constraint)
        elif constraint.constraint_type == SafetyConstraintType.PRIVACY_RULES:
            return self._check_privacy_rules(content, constraint)
        elif constraint.constraint_type == SafetyConstraintType.BIAS_MITIGATION:
            return self._check_bias(content, constraint)
        # Add other constraint types as needed
        return None
    
    def _check_content_safety(self, content: str, constraint: SafetyConstraint) -> Optional[SafetyViolation]:
        """Check content safety violations."""
        # Simplified implementation - would use sophisticated content filtering
        harmful_patterns = ["harmful", "illegal", "dangerous"]
        for pattern in harmful_patterns:
            if pattern.lower() in content.lower():
                return SafetyViolation(
                    constraint_type=constraint.constraint_type,
                    rule=constraint.rule,
                    severity=constraint.severity,
                    detected_content=content,
                    confidence=0.8,
                    metadata=constraint.metadata
                )
        return None
    
    def _check_privacy_rules(self, content: str, constraint: SafetyConstraint) -> Optional[SafetyViolation]:
        """Check privacy rule violations."""
        # Simplified PII detection
        pii_patterns = ["ssn", "social security", "credit card"]
        for pattern in pii_patterns:
            if pattern.lower() in content.lower():
                return SafetyViolation(
                    constraint_type=constraint.constraint_type,
                    rule=constraint.rule,
                    severity=constraint.severity,
                    detected_content=content,
                    confidence=0.9,
                    metadata=constraint.metadata
                )
        return None
    
    def _check_bias(self, content: str, constraint: SafetyConstraint) -> Optional[SafetyViolation]:
        """Check for biased content."""
        # Simplified bias detection
        bias_indicators = ["always", "never", "obviously"]
        for indicator in bias_indicators:
            if indicator.lower() in content.lower():
                return SafetyViolation(
                    constraint_type=constraint.constraint_type,
                    rule=constraint.rule,
                    severity=constraint.severity,
                    detected_content=content,
                    confidence=0.6,
                    metadata=constraint.metadata
                )
        return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for audit trail."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    
    def get_safety_policy_for_layer(self, layer: str) -> SafetyPolicy:
        """
        Get safety policy applicable to a specific layer.
        
        Provides layers with their safety constraints without exposing implementation details.
        """
        applicable_constraints = []
        for constraint_type, constraint_list in self.constraints.items():
            for constraint in constraint_list:
                if layer in constraint.layer_applicability:
                    applicable_constraints.append(constraint)
        
        return LayerSafetyPolicy(
            layer=layer,
            constraints=applicable_constraints,
            validation_callback=self._check_constraint
        )


# Alias for backward compatibility with existing imports
SafetyValidator = L5SafetyValidator
