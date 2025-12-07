"""
validate_generated_content.py - Policy Enforcement Module

Domain: resume
Generated: 2025-12-07T13:28:54.203789
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PolicyDecision(Enum):
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"


@dataclass
class PolicyViolation:
    """A policy violation."""
    rule_id: str
    message: str
    severity: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyResult:
    """Result of policy evaluation."""
    decision: PolicyDecision
    violations: List[PolicyViolation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ValidateGeneratedContent:
    """Policy enforcer for resume domain."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.rules = self.config.get("rules", [])
        self.strict = self.config.get("strict", True)
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def evaluate(self, data: Any, context: Optional[Dict] = None) -> PolicyResult:
        """Evaluate data against policy rules."""
        violations = []
        
        # Check required fields
        violations.extend(self._check_required(data))
        
        # Check constraints
        violations.extend(self._check_constraints(data))
        
        # Check safety rules
        violations.extend(self._check_safety(data))
        
        # Determine decision
        if any(v.severity == "error" for v in violations):
            decision = PolicyDecision.DENY
        elif violations:
            decision = PolicyDecision.WARN if not self.strict else PolicyDecision.DENY
        else:
            decision = PolicyDecision.ALLOW
        
        return PolicyResult(decision=decision, violations=violations)
    
    def _check_required(self, data: Any) -> List[PolicyViolation]:
        """Check required fields."""
        violations = []
        if isinstance(data, dict):
            for field in self.config.get("required_fields", []):
                if field not in data:
                    violations.append(PolicyViolation(
                        rule_id="REQUIRED_FIELD",
                        message=f"Missing required field: {field}",
                        severity="error"
                    ))
        return violations
    
    def _check_constraints(self, data: Any) -> List[PolicyViolation]:
        """Check value constraints."""
        violations = []
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and len(value) > 10000:
                    violations.append(PolicyViolation(
                        rule_id="MAX_LENGTH",
                        message=f"Field {key} exceeds max length",
                        severity="warning"
                    ))
        return violations
    
    def _check_safety(self, data: Any) -> List[PolicyViolation]:
        """Check safety rules."""
        violations = []
        dangerous = ["<script>", "javascript:", "__import__"]
        data_str = str(data).lower()
        for pattern in dangerous:
            if pattern in data_str:
                violations.append(PolicyViolation(
                    rule_id="DANGEROUS_CONTENT",
                    message=f"Dangerous pattern detected",
                    severity="error"
                ))
                break
        return violations


def evaluate_policy(data: Any, config: Optional[Dict] = None) -> PolicyResult:
    """Evaluate data against policy."""
    return ValidateGeneratedContent(config).evaluate(data)
