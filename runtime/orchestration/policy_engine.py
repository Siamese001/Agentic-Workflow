"""
Policy engine for content safety and rule enforcement in the agentic runtime.

Provides content evaluation, safety policy enforcement, and prompt injection
protection with deterministic behavior and performance optimization.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Pattern
from dataclasses import dataclass, field
from datetime import datetime, UTC
import logging
import re
import time
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PolicyViolation:
    """Represents a policy violation with details."""
    violation_type: str
    severity: str  # low, medium, high, critical
    description: str
    confidence: float
    rule_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyEvaluationResult:
    """Result of policy evaluation with comprehensive metadata."""
    allowed: bool
    confidence_score: float
    policy_violations: List[PolicyViolation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    evaluation_time_ms: Optional[float] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SafetyPolicy:
    """Individual safety policy with rules and configuration."""
    policy_id: str
    name: str
    description: str
    rules: List[str]
    threshold: float = 0.8
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class PolicyEngine:
    """
    Policy engine for content safety and rule enforcement.
    
    Evaluates content against safety policies, detects prompt injection attempts,
    and enforces configurable rules with deterministic behavior.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize policy engine with configuration."""
        self.config = config or {}
        self.policy_level = self.config.get("policy_level", "medium")
        self.strict_mode = self.config.get("strict_mode", False)
        
        self.policies: Dict[str, SafetyPolicy] = {}
        self.compiled_patterns: Dict[str, Pattern] = {}
        
        # Predefined safety patterns
        self._initialize_safety_patterns()
        self._load_default_policies()

    def _initialize_safety_patterns(self) -> None:
        """Initialize compiled regex patterns for safety checking."""
        patterns = {
            "harmful_content": [
                r"(?i)(kill|harm|hurt|violence|murder|death|suicide)",
                r"(?i)(weapon|bomb|explosive|poison|toxic)",
                r"(?i)(illegal|criminal|fraud|scam|blackmail)"
            ],
            "personal_data": [
                r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone numbers
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
                r"\b\d{4}[-.]?\d{4}[-.]?\d{4}[-.]?\d{4}\b",  # Credit card
                r"\b\d{3}-\d{2}-\d{4}\b"  # SSN
            ],
            "prompt_injection": [
                r"(?i)(ignore previous instructions|forget everything|system prompt)",
                r"(?i)(act as|pretend to be|roleplay as)\s+(dan|jailbreak|uncensored)",
                r"(?i)(override|disable|bypass)\s+(safety|filter|restriction)",
                r"(?i)(###|---|\*\*\*)\s*(new|override|system)\s*(instructions|prompt|rules)"
            ],
            "illegal_activity": [
                r"(?i)(hack|crack|exploit|vulnerability|breach)",
                r"(?i)(steal|theft|robbery|burglary)",
                r"(?i)(drugs|narcotics|illegal substances)"
            ]
        }
        
        # Compile patterns for performance
        for category, pattern_list in patterns.items():
            compiled = []
            for pattern in pattern_list:
                try:
                    compiled.append(re.compile(pattern))
                except re.error:
                    logger.warning(f"Invalid regex pattern: {pattern}")
            self.compiled_patterns[category] = compiled

    def _load_default_policies(self) -> None:
        """Load default safety policies."""
        default_policies = [
            SafetyPolicy(
                policy_id="content_safety",
                name="Content Safety Policy",
                description="Blocks harmful and dangerous content",
                rules=["no_harmful_content", "no_illegal_activity"],
                threshold=0.8 if self.policy_level == "high" else 0.6
            ),
            SafetyPolicy(
                policy_id="privacy_protection",
                name="Privacy Protection Policy", 
                description="Protects personal and sensitive information",
                rules=["no_personal_data"],
                threshold=0.9
            ),
            SafetyPolicy(
                policy_id="prompt_injection_protection",
                name="Prompt Injection Protection",
                description="Blocks prompt injection and jailbreak attempts",
                rules=["no_prompt_injection"],
                threshold=0.7 if self.policy_level == "high" else 0.5
            )
        ]
        
        for policy in default_policies:
            self.policies[policy.policy_id] = policy

    def evaluate_content(self, content: Dict[str, Any]) -> PolicyEvaluationResult:
        """
        Evaluate content against all active safety policies.

        Args:
            content: Content dictionary with text, context, and metadata

        Returns:
            PolicyEvaluationResult with comprehensive evaluation metadata
        """
        start_time = time.time()
        
        # Normalize input
        normalized_content = self._normalize_input(content)
        text = normalized_content.get("text", "")
        
        violations = []
        total_confidence = 1.0
        
        # Evaluate against each policy
        for policy in self.policies.values():
            if not policy.enabled:
                continue
                
            policy_violations = self._evaluate_policy(policy, text, normalized_content)
            violations.extend(policy_violations)
            
            # Adjust confidence based on violations
            if policy_violations:
                max_violation_confidence = max(v.confidence for v in policy_violations)
                total_confidence = min(total_confidence, 1.0 - max_violation_confidence)
        
        # Determine if content is allowed
        allowed = len(violations) == 0 or (
            not self.strict_mode and 
            all(v.severity in ["low", "medium"] for v in violations)
        )
        
        evaluation_time_ms = (time.time() - start_time) * 1000
        
        result = PolicyEvaluationResult(
            allowed=allowed,
            confidence_score=total_confidence,
            policy_violations=violations,
            metadata={
                "policy_level": self.policy_level,
                "strict_mode": self.strict_mode,
                "content_length": len(text),
                "policies_evaluated": len([p for p in self.policies.values() if p.enabled])
            },
            evaluation_time_ms=evaluation_time_ms
        )
        
        logger.debug(f"Content evaluated: allowed={allowed}, violations={len(violations)}, "
                    f"time={evaluation_time_ms:.2f}ms")
        
        return result

    def _normalize_input(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize input content to consistent format."""
        normalized = {
            "text": "",
            "context": {},
            "metadata": {}
        }
        
        # Extract text from various possible fields
        for field in ["text", "content", "message", "prompt"]:
            if field in content and isinstance(content[field], str):
                normalized["text"] = content[field].strip()
                break
        
        # Copy context and metadata
        if "context" in content:
            normalized["context"] = content["context"]
        if "metadata" in content:
            normalized["metadata"] = content["metadata"]
        
        return normalized

    def _evaluate_policy(self, policy: SafetyPolicy, text: str, context: Dict[str, Any]) -> List[PolicyViolation]:
        """Evaluate a single policy against the text."""
        violations = []
        
        for rule in policy.rules:
            rule_violations = self._evaluate_rule(rule, text, context)
            violations.extend(rule_violations)
        
        return violations

    def _evaluate_rule(self, rule: str, text: str, context: Dict[str, Any]) -> List[PolicyViolation]:
        """Evaluate a single rule against the text."""
        violations = []
        
        if rule in self.compiled_patterns:
            patterns = self.compiled_patterns[rule]
            
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    severity = self._determine_severity(rule, matches)
                    confidence = min(0.9, 0.5 + len(matches) * 0.1)
                    
                    violation = PolicyViolation(
                        violation_type=rule,
                        severity=severity,
                        description=f"Detected {rule} in content",
                        confidence=confidence,
                        rule_id=rule,
                        metadata={"matches": matches[:5]}  # Limit to first 5 matches
                    )
                    violations.append(violation)
        
        return violations

    def _determine_severity(self, rule: str, matches: List[str]) -> str:
        """Determine violation severity based on rule and matches."""
        if rule == "prompt_injection":
            return "critical"
        elif rule in ["harmful_content", "illegal_activity"]:
            return "high"
        elif rule == "personal_data":
            return "medium"
        else:
            return "low"

    def apply_policies(self, content: Dict[str, Any]) -> PolicyEvaluationResult:
        """Apply all policies to content (alias for evaluate_content)."""
        return self.evaluate_content(content)

    def get_policy_result(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Get policy evaluation result as dictionary."""
        result = self.evaluate_content(content)
        
        return {
            "allowed": result.allowed,
            "confidence_score": result.confidence_score,
            "policy_violations": [
                {
                    "type": v.violation_type,
                    "severity": v.severity,
                    "description": v.description,
                    "confidence": v.confidence
                }
                for v in result.policy_violations
            ],
            "metadata": result.metadata
        }

    def load_policies(self, policy_config: Optional[Dict[str, Any]] = None) -> None:
        """Load or reload policies with optional configuration."""
        if policy_config:
            # Load custom policies from config
            for policy_data in policy_config.get("policies", []):
                policy = SafetyPolicy(
                    policy_id=policy_data["policy_id"],
                    name=policy_data["name"],
                    description=policy_data.get("description", ""),
                    rules=policy_data["rules"],
                    threshold=policy_data.get("threshold", 0.8),
                    enabled=policy_data.get("enabled", True),
                    metadata=policy_data.get("metadata", {})
                )
                self.policies[policy.policy_id] = policy

    def get_loaded_policies(self) -> List[Dict[str, Any]]:
        """Get list of currently loaded policies."""
        return [
            {
                "policy_id": policy.policy_id,
                "name": policy.name,
                "description": policy.description,
                "rules": policy.rules,
                "threshold": policy.threshold,
                "enabled": policy.enabled
            }
            for policy in self.policies.values()
        ]

    def add_custom_pattern(self, pattern_config: Dict[str, Any]) -> bool:
        """Add a custom pattern for policy evaluation."""
        pattern_str = pattern_config.get("pattern", "")
        category = pattern_config.get("category", "custom")
        
        if not pattern_str:
            raise ValueError("Pattern cannot be empty")
        
        try:
            # Validate pattern
            compiled = re.compile(pattern_str)
            
            # Add to patterns
            if category not in self.compiled_patterns:
                self.compiled_patterns[category] = []
            self.compiled_patterns[category].append(compiled)
            
            logger.info(f"Added custom pattern to category: {category}")
            return True
            
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

    def validate_pattern(self, pattern_config: Dict[str, Any]) -> bool:
        """Validate a regex pattern without adding it."""
        pattern_str = pattern_config.get("pattern", "")
        
        if not pattern_str:
            return False
        
        try:
            re.compile(pattern_str)
            return True
        except re.error:
            return False

    def update_policy_threshold(self, policy_id: str, threshold: float) -> bool:
        """Update threshold for a specific policy."""
        if policy_id in self.policies:
            if 0.0 <= threshold <= 1.0:
                self.policies[policy_id].threshold = threshold
                logger.info(f"Updated threshold for policy {policy_id}: {threshold}")
                return True
            else:
                raise ValueError("Threshold must be between 0.0 and 1.0")
        return False

    def enable_policy(self, policy_id: str) -> bool:
        """Enable a specific policy."""
        if policy_id in self.policies:
            self.policies[policy_id].enabled = True
            return True
        return False

    def disable_policy(self, policy_id: str) -> bool:
        """Disable a specific policy."""
        if policy_id in self.policies:
            self.policies[policy_id].enabled = False
            return True
        return False


# Global policy engine instance
_policy_engine = PolicyEngine()


def get_policy_engine() -> PolicyEngine:
    """Get the global policy engine instance."""
    return _policy_engine


def evaluate_content(content: Dict[str, Any]) -> PolicyEvaluationResult:
    """Evaluate content using the global policy engine."""
    return _policy_engine.evaluate_content(content)


def configure_policy_engine(config: Dict[str, Any]) -> None:
    """Configure the global policy engine with new settings."""
    global _policy_engine
    _policy_engine = PolicyEngine(config)


__all__ = [
    "PolicyViolation",
    "PolicyEvaluationResult", 
    "SafetyPolicy",
    "PolicyEngine",
    "get_policy_engine",
    "evaluate_content",
    "configure_policy_engine"
]
