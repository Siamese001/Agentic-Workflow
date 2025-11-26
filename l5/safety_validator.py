"""
L5 safety validation for resume job alignment workflows.

Centralizes safety constraints and ethical guidelines for resume enhancement.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Callable
from enum import Enum
import logging

from l5.interfaces import (
    SafetyConstraint,
    SafetyViolation,
    PolicyDecision,
    PolicyEvaluationError,
    Severity,
    Verdict
)
from l5.types import SafetyPolicy, SafetyContext
from core.models.models import SafetyResult, SafetyFinding, ExecutionContext

logger = logging.getLogger(__name__)


class LayerSafetyPolicy(SafetyPolicy):
    """Concrete safety policy implementation for resume workflow layers."""
    
    def __init__(self, layer: str, constraints: List[SafetyConstraint], validation_callback: Callable[[str, SafetyConstraint], Optional[SafetyViolation]]):
        """Initializes safety policy for resume workflow layer."""
        self.layer = layer
        self.constraints = constraints
        self.validation_callback = validation_callback
    
    @property
    def policy_id(self) -> str:
        """Unique identifier for resume workflow safety policy."""
        return f"{self.layer}_safety_policy"
    
    @property
    def description(self) -> str:
        """Human-readable description of resume workflow safety policy."""
        return f"Safety policy for {self.layer} layer with {len(self.constraints)} constraints"
    
    def evaluate(self, context: SafetyContext) -> PolicyDecision:
        """Evaluates resume workflow context against safety policy."""
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
    OUTREACH_CONSTRAINTS = "outreach_constraints"
    MESSAGE_STYLE = "message_style"
    ROUTE_REQUIREMENTS = "route_requirements"
    ARCHETYPE_COMPLIANCE = "archetype_compliance"


class L5SafetyValidator:
    """
    Centralized L5 safety validation for resume job alignment workflows.

    Enforces safety constraints and ethical guidelines for resume enhancement.
    """
    
    def __init__(self):
        self.constraints = self._load_safety_constraints()
        self.violation_history: List[SafetyViolation] = []
    
    def _is_outreach_constraint(self, ctype):
        """Check if constraint type is outreach-specific."""
        return ctype in {
            SafetyConstraintType.OUTREACH_CONSTRAINTS,
            SafetyConstraintType.MESSAGE_STYLE,
            SafetyConstraintType.ROUTE_REQUIREMENTS,
            SafetyConstraintType.ARCHETYPE_COMPLIANCE
        }
    
    def _load_safety_constraints(self) -> Dict[SafetyConstraintType, List[SafetyConstraint]]:
        """Loads safety constraints for resume workflow enforcement."""
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
            SafetyConstraintType.OUTREACH_CONSTRAINTS: [
                SafetyConstraint(
                    constraint_type=SafetyConstraintType.OUTREACH_CONSTRAINTS,
                    rule="No placeholders in message",
                    severity="blocking",
                    layer_applicability=["L2"],
                    metadata={"lic_error_code": "LIC-E001"}
                ),
                SafetyConstraint(
                    constraint_type=SafetyConstraintType.OUTREACH_CONSTRAINTS,
                    rule="Per-claim confidence must be >= 0.70",
                    severity="blocking",
                    layer_applicability=["L2"],
                    metadata={"lic_error_code": "LIC-E002"}
                ),
                SafetyConstraint(
                    constraint_type=SafetyConstraintType.OUTREACH_CONSTRAINTS,
                    rule="Message must contain job title in first 50 words",
                    severity="warning",
                    layer_applicability=["L2"],
                    metadata={"lic_error_code": "LIC-E005"}
                )
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
        
        domain = context.metadata.get("domain", "resume") if context else "resume"
        
        for constraint_type, constraint_list in self.constraints.items():
            for constraint in constraint_list:
                if layer in constraint.layer_applicability:
                    # Skip outreach constraints unless domain is outreach
                    if self._is_outreach_constraint(constraint_type) and domain != "outreach":
                        continue
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
        """Checks if resume workflow content violates safety constraint."""
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
        """Checks content safety violations in resume workflow data."""
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
        """Checks privacy rule violations in resume workflow data."""
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
        """Checks for biased content in resume workflow data."""
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
        """Gets timestamp for resume workflow audit trail."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
    
    def get_safety_policy_for_layer(self, layer: str) -> SafetyPolicy:
        """Gets safety policy for resume workflow layer enhancement."""
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
