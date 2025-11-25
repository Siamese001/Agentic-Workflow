"""
L5 safety validation for comprehensive résumé protection.

Centralizes all safety constraints, ethical guidelines, privacy rules, and bias mitigation for secure processing.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

from .interfaces import SafetyPolicy, SafetyResult, SafetyViolation
from core.models.models import ExecutionContext

logger = logging.getLogger(__name__)


class SafetyConstraintType(str, Enum):
    """Types of safety constraints enforced by L5."""
    
    CONTENT_SAFETY = "content_safety"
    ETHICAL_GUIDELINES = "ethical_guidelines"
    PRIVACY_RULES = "privacy_rules"
    BIAS_MITIGATION = "bias_mitigation"
    TEMPORAL_CONSTRAINTS = "temporal_constraints"
    AUDIENCE_SAFETY = "audience_safety"


@dataclass
class SafetyConstraint:
    """Individual safety constraint with enforcement rules."""
    
    constraint_type: SafetyConstraintType
    rule: str
    severity: str  # "blocking", "warning", "info"
    layer_applicability: List[str]  # ["L1", "L2", "L3", "L4"]
    metadata: Dict[str, Any]


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
        
        result = SafetyResult(
            is_safe=len([v for v in violations if v.severity == "blocking"]) == 0,
            violations=violations,
            layer=layer,
            timestamp=self._get_timestamp()
        )
        
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
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
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
        
        return SafetyPolicy(
            layer=layer,
            constraints=applicable_constraints,
            validation_callback=lambda content: self.validate_layer_input(layer, content)
        )
