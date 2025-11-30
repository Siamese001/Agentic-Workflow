"""
Base Policy Implementation

Provides comprehensive policy governance for prompt management,
validation, and compliance across the L1-L5 architecture.
"""

from __future__ import annotations

import asyncio
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable, Set
from enum import Enum
import json

from ..templates.base import BaseTemplate, RenderContext


class PolicyType(str, Enum):
    """Types of governance policies."""
    SAFETY = "safety"
    PRIVACY = "privacy"
    COMPLIANCE = "compliance"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ETHICS = "ethics"
    ACCESS_CONTROL = "access_control"


class PolicySeverity(str, Enum):
    """Severity levels for policy violations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PolicyAction(str, Enum):
    """Actions to take on policy violations."""
    WARN = "warn"
    BLOCK = "block"
    MODIFY = "modify"
    LOG = "log"
    ESCALATE = "escalate"


@dataclass
class PolicyViolation:
    """Represents a policy violation."""
    policy_name: str
    policy_type: PolicyType
    severity: PolicySeverity
    description: str
    detected_at: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    suggested_action: Optional[str] = None
    auto_fixable: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "policy_name": self.policy_name,
            "policy_type": self.policy_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "detected_at": self.detected_at,
            "context": self.context,
            "suggested_action": self.suggested_action,
            "auto_fixable": self.auto_fixable,
        }


@dataclass
class PolicyResult:
    """Result of policy validation."""
    is_compliant: bool
    violations: List[PolicyViolation] = field(default_factory=list)
    applied_actions: List[PolicyAction] = field(default_factory=list)
    modified_prompt: Optional[str] = None
    validation_time: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_violation(self, violation: PolicyViolation) -> None:
        """Add a policy violation."""
        self.violations.append(violation)
        self.is_compliant = False
    
    def get_max_severity(self) -> Optional[PolicySeverity]:
        """Get the maximum severity violation."""
        if not self.violations:
            return None
        
        severity_order = [PolicySeverity.LOW, PolicySeverity.MEDIUM, 
                         PolicySeverity.HIGH, PolicySeverity.CRITICAL]
        
        for severity in reversed(severity_order):
            if any(v.severity == severity for v in self.violations):
                return severity
        
        return PolicySeverity.LOW


class BasePolicy(ABC):
    """Base class for all governance policies."""
    
    def __init__(self, name: str, policy_type: PolicyType, 
                 severity: PolicySeverity = PolicySeverity.MEDIUM,
                 action: PolicyAction = PolicyAction.WARN,
                 enabled: bool = True):
        self.name = name
        self.policy_type = policy_type
        self.severity = severity
        self.action = action
        self.enabled = enabled
        
        # Statistics
        self.validation_count = 0
        self.violation_count = 0
        self.last_validated: Optional[float] = None
        
        # Configuration
        self.config: Dict[str, Any] = {}
        self.exceptions: Set[str] = set()  # Exception patterns
    
    @abstractmethod
    def validate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> PolicyResult:
        """Validate prompt against this policy."""
        pass
    
    def is_enabled(self) -> bool:
        """Check if policy is enabled."""
        return self.enabled
    
    def enable(self) -> None:
        """Enable the policy."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the policy."""
        self.enabled = False
    
    def add_exception(self, pattern: str) -> None:
        """Add an exception pattern."""
        self.exceptions.add(pattern)
    
    def remove_exception(self, pattern: str) -> None:
        """Remove an exception pattern."""
        self.exceptions.discard(pattern)
    
    def is_exception(self, prompt: str) -> bool:
        """Check if prompt matches any exception pattern."""
        for pattern in self.exceptions:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True
        return False
    
    def update_config(self, **kwargs) -> None:
        """Update policy configuration."""
        self.config.update(kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get policy statistics."""
        return {
            "name": self.name,
            "policy_type": self.policy_type.value,
            "severity": self.severity.value,
            "action": self.action.value,
            "enabled": self.enabled,
            "validation_count": self.validation_count,
            "violation_count": self.violation_count,
            "violation_rate": self.violation_count / max(self.validation_count, 1),
            "last_validated": self.last_validated,
        }


class SafetyPolicy(BasePolicy):
    """Safety policy for harmful content detection."""
    
    def __init__(self, name: str = "safety_policy"):
        super().__init__(name, PolicyType.SAFETY, PolicySeverity.HIGH, PolicyAction.BLOCK)
        
        # Harmful content patterns
        self.harmful_patterns = [
            r'\b(how to|instructions for|step by step).*(kill|harm|hurt|injure|violence)\b',
            r'\b(illegal|illegal activities|criminal|felony)\b',
            r'\b(hate|discriminat|racist|sexist|homophobic)\b',
            r'\b(self.?harm|suicide|kill.?myself)\b',
            r'\b(weapon|bomb|explosive|poison|toxin)\b',
        ]
        
        self.config.update({
            "max_pattern_matches": 1,
            "case_sensitive": False,
        })
    
    def validate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> PolicyResult:
        """Validate prompt for harmful content."""
        self.validation_count += 1
        self.last_validated = time.time()
        
        result = PolicyResult(is_compliant=True)
        
        if not self.enabled or self.is_exception(prompt):
            return result
        
        # Check for harmful patterns
        matches = 0
        for pattern in self.harmful_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                matches += 1
                violation = PolicyViolation(
                    policy_name=self.name,
                    policy_type=self.policy_type,
                    severity=self.severity,
                    description=f"Harmful content detected: {pattern}",
                    context={"pattern": pattern, "matches": matches},
                    suggested_action="Block or modify harmful content",
                    auto_fixable=False,
                )
                result.add_violation(violation)
        
        if matches >= self.config.get("max_pattern_matches", 1):
            result.applied_actions.append(self.action)
        
        if not result.is_compliant:
            self.violation_count += 1
        
        return result


class PrivacyPolicy(BasePolicy):
    """Privacy policy for personal information detection."""
    
    def __init__(self, name: str = "privacy_policy"):
        super().__init__(name, PolicyType.PRIVACY, PolicySeverity.MEDIUM, PolicyAction.MODIFY)
        
        # PII patterns
        self.pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone number
        ]
        
        self.config.update({
            "redaction_char": "*",
            "preserve_length": True,
        })
    
    def validate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> PolicyResult:
        """Validate prompt for personal information."""
        self.validation_count += 1
        self.last_validated = time.time()
        
        result = PolicyResult(is_compliant=True)
        modified_prompt = prompt
        
        if not self.enabled or self.is_exception(prompt):
            return result
        
        # Check for PII patterns
        for pattern in self.pii_patterns:
            matches = re.finditer(pattern, prompt)
            for match in matches:
                violation = PolicyViolation(
                    policy_name=self.name,
                    policy_type=self.policy_type,
                    severity=self.severity,
                    description=f"Personal information detected: {match.group()}",
                    context={"pattern": pattern, "matched_text": match.group()},
                    suggested_action="Redact personal information",
                    auto_fixable=True,
                )
                result.add_violation(violation)
                
                # Auto-redact if possible
                if self.action == PolicyAction.MODIFY:
                    redaction_char = self.config.get("redaction_char", "*")
                    if self.config.get("preserve_length", True):
                        redacted = redaction_char * len(match.group())
                    else:
                        redacted = "[REDACTED]"
                    
                    modified_prompt = modified_prompt.replace(match.group(), redacted)
        
        if not result.is_compliant:
            result.applied_actions.append(self.action)
            result.modified_prompt = modified_prompt
            self.violation_count += 1
        
        return result


class QualityPolicy(BasePolicy):
    """Quality policy for prompt quality standards."""
    
    def __init__(self, name: str = "quality_policy"):
        super().__init__(name, PolicyType.QUALITY, PolicySeverity.LOW, PolicyAction.WARN)
        
        self.config.update({
            "min_length": 10,
            "max_length": 10000,
            "required_keywords": [],
            "forbidden_keywords": [],
        })
    
    def validate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> PolicyResult:
        """Validate prompt quality standards."""
        self.validation_count += 1
        self.last_validated = time.time()
        
        result = PolicyResult(is_compliant=True)
        
        if not self.enabled or self.is_exception(prompt):
            return result
        
        # Check length constraints
        if len(prompt) < self.config.get("min_length", 10):
            violation = PolicyViolation(
                policy_name=self.name,
                policy_type=self.policy_type,
                severity=PolicySeverity.LOW,
                description=f"Prompt too short: {len(prompt)} < {self.config.get('min_length')}",
                context={"length": len(prompt), "min_length": self.config.get("min_length")},
                suggested_action="Add more detail to the prompt",
                auto_fixable=False,
            )
            result.add_violation(violation)
        
        if len(prompt) > self.config.get("max_length", 10000):
            violation = PolicyViolation(
                policy_name=self.name,
                policy_type=self.policy_type,
                severity=PolicySeverity.MEDIUM,
                description=f"Prompt too long: {len(prompt)} > {self.config.get('max_length')}",
                context={"length": len(prompt), "max_length": self.config.get("max_length")},
                suggested_action="Shorten the prompt",
                auto_fixable=False,
            )
            result.add_violation(violation)
        
        # Check required keywords
        required_keywords = self.config.get("required_keywords", [])
        for keyword in required_keywords:
            if keyword.lower() not in prompt.lower():
                violation = PolicyViolation(
                    policy_name=self.name,
                    policy_type=self.policy_type,
                    severity=PolicySeverity.LOW,
                    description=f"Missing required keyword: {keyword}",
                    context={"keyword": keyword},
                    suggested_action=f"Include '{keyword}' in the prompt",
                    auto_fixable=False,
                )
                result.add_violation(violation)
        
        # Check forbidden keywords
        forbidden_keywords = self.config.get("forbidden_keywords", [])
        for keyword in forbidden_keywords:
            if keyword.lower() in prompt.lower():
                violation = PolicyViolation(
                    policy_name=self.name,
                    policy_type=self.policy_type,
                    severity=PolicySeverity.MEDIUM,
                    description=f"Forbidden keyword detected: {keyword}",
                    context={"keyword": keyword},
                    suggested_action=f"Remove '{keyword}' from the prompt",
                    auto_fixable=False,
                )
                result.add_violation(violation)
        
        if not result.is_compliant:
            result.applied_actions.append(self.action)
            self.violation_count += 1
        
        return result


class PolicyEngine:
    """Engine for managing and executing governance policies."""
    
    def __init__(self):
        self.policies: Dict[str, BasePolicy] = {}
        self.policy_chains: Dict[str, List[str]] = {}
        
        # Initialize default policies
        self._initialize_default_policies()
    
    def _initialize_default_policies(self) -> None:
        """Initialize default governance policies."""
        self.register_policy(SafetyPolicy())
        self.register_policy(PrivacyPolicy())
        self.register_policy(QualityPolicy())
    
    def register_policy(self, policy: BasePolicy) -> None:
        """Register a governance policy."""
        self.policies[policy.name] = policy
    
    def unregister_policy(self, name: str) -> None:
        """Unregister a governance policy."""
        if name in self.policies:
            del self.policies[name]
    
    def get_policy(self, name: str) -> Optional[BasePolicy]:
        """Get policy by name."""
        return self.policies.get(name)
    
    def list_policies(self, policy_type: Optional[PolicyType] = None) -> List[str]:
        """List registered policies, optionally filtered by type."""
        if policy_type:
            return [name for name, policy in self.policies.items() 
                   if policy.policy_type == policy_type]
        return list(self.policies.keys())
    
    def validate_prompt(self, prompt: str, 
                       policy_names: Optional[List[str]] = None,
                       context: Optional[Dict[str, Any]] = None) -> PolicyResult:
        """Validate prompt against specified policies."""
        policies_to_check = policy_names or list(self.policies.keys())
        
        combined_result = PolicyResult(is_compliant=True)
        
        for policy_name in policies_to_check:
            policy = self.get_policy(policy_name)
            if policy and policy.is_enabled():
                result = policy.validate(prompt, context)
                
                # Merge results
                combined_result.violations.extend(result.violations)
                combined_result.applied_actions.extend(result.applied_actions)
                
                if result.modified_prompt:
                    combined_result.modified_prompt = result.modified_prompt
                
                if not result.is_compliant:
                    combined_result.is_compliant = False
        
        return combined_result
    
    async def validate_prompt_async(self, prompt: str,
                                  policy_names: Optional[List[str]] = None,
                                  context: Optional[Dict[str, Any]] = None) -> PolicyResult:
        """Validate prompt asynchronously."""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.validate_prompt, prompt, policy_names, context
        )
    
    def create_policy_chain(self, chain_name: str, policy_names: List[str]) -> None:
        """Create a chain of policies to execute in order."""
        self.policy_chains[chain_name] = policy_names
    
    def execute_policy_chain(self, chain_name: str, prompt: str,
                           context: Optional[Dict[str, Any]] = None) -> PolicyResult:
        """Execute a policy chain."""
        policy_names = self.policy_chains.get(chain_name)
        if not policy_names:
            raise ValueError(f"Policy chain '{chain_name}' not found")
        
        return self.validate_prompt(prompt, policy_names, context)
    
    def get_policy_stats(self) -> Dict[str, Any]:
        """Get statistics for all policies."""
        return {
            "total_policies": len(self.policies),
            "enabled_policies": len([p for p in self.policies.values() if p.is_enabled()]),
            "policy_chains": len(self.policy_chains),
            "policy_details": {name: policy.get_stats() for name, policy in self.policies.items()},
        }


# Global policy engine
_policy_engine: Optional[PolicyEngine] = None


def get_policy_engine() -> PolicyEngine:
    """Get the global policy engine instance."""
    global _policy_engine
    if _policy_engine is None:
        _policy_engine = PolicyEngine()
    return _policy_engine


def validate_prompt(prompt: str, policy_names: Optional[List[str]] = None,
                   context: Optional[Dict[str, Any]] = None) -> PolicyResult:
    """Validate prompt using global policy engine."""
    return get_policy_engine().validate_prompt(prompt, policy_names, context)


__all__ = [
    "BasePolicy",
    "SafetyPolicy",
    "PrivacyPolicy", 
    "QualityPolicy",
    "PolicyEngine",
    "PolicyType",
    "PolicySeverity",
    "PolicyAction",
    "PolicyViolation",
    "PolicyResult",
    "get_policy_engine",
    "validate_prompt",
]
