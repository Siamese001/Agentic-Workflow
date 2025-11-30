"""L5 Safety Engine - Robust Implementation

Provides comprehensive safety, security, and compliance capabilities
for both resume and outreach workflows with robust validation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Set, Pattern
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
import re
from datetime import datetime

# Re-export robust implementations from engines
from agentic_core.outreach_engine.l5_safety.policies.lic_safety_validator import (
    OutreachSafetyValidator,
)  # noqa: F401
from agentic_core.outreach_engine.l5_safety.policies.lic_failure_classifier import (
    FailureClassifier,
)  # noqa: F401
from agentic_core.resume_engine.l5_safety.policies.rg_injection_detection import (
    InjectionDetector,
)  # noqa: F401

class SafetyLevel(str, Enum):
    """Safety validation levels."""
    STRICT = "strict"
    STANDARD = "standard"
    RELAXED = "relaxed"
    DEBUG = "debug"

class ThreatType(str, Enum):
    """Types of security threats to detect."""
    PII_EXPOSURE = "pii_exposure"
    INJECTION_ATTACK = "injection_attack"
    MALICIOUS_CONTENT = "malicious_content"
    PRIVACY_VIOLATION = "privacy_violation"
    COMPLIANCE_BREACH = "compliance_breach"
    DATA_EXFILTRATION = "data_exfiltration"

class ValidationStatus(str, Enum):
    """Validation result status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    ERROR = "error"

@dataclass
class SafetyPolicy:
    """Safety policy configuration."""
    policy_id: str
    name: str
    description: str
    threat_types: List[ThreatType]
    safety_level: SafetyLevel
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Result of safety validation."""
    status: ValidationStatus
    threats_detected: List[ThreatType]
    confidence_scores: Dict[str, float]
    details: Dict[str, Any]
    recommendations: List[str]
    processing_time_ms: int

@dataclass
class SafetyReport:
    """Comprehensive safety report."""
    report_id: str
    validation_results: List[ValidationResult]
    overall_status: ValidationStatus
    risk_score: float
    generated_at: datetime
    metadata: Dict[str, Any]

class SafetyEngine:
    """
    Robust safety engine providing comprehensive security validation
    for both resume and outreach workflows.
    """
    
    def __init__(
        self,
        safety_level: SafetyLevel = SafetyLevel.STANDARD,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.safety_level = safety_level
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize specialized safety components
        self.outreach_validator = OutreachSafetyValidator()
        self.failure_classifier = FailureClassifier()
        self.injection_detector = InjectionDetector()
        
        # PII detection patterns
        self._pii_patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
            "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "credit_card": re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
        }
        
        # Malicious content patterns
        self._malicious_patterns = {
            "sql_injection": re.compile(r'(?i)(union|select|insert|update|delete|drop|exec|script)', re.IGNORECASE),
            "xss": re.compile(r'(?i)(<script|javascript:|onload=|onerror=)', re.IGNORECASE),
            "path_traversal": re.compile(r'(\.\./|\.\.\\|%2e%2e%2f)', re.IGNORECASE),
        }
        
        # Safety policies
        self._policies: Dict[str, SafetyPolicy] = {}
        self._load_default_policies()
        
        # Statistics tracking
        self._validation_stats = {
            "total_validations": 0,
            "threats_detected": 0,
            "false_positives": 0,
        }
    
    async def validate_content(
        self, 
        content: str,
        content_type: str = "text",
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate content against safety policies.
        
        Args:
            content: Content to validate
            content_type: Type of content (text, json, etc.)
            context: Additional context for validation
            
        Returns:
            Validation result with threat detection
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            threats_detected = []
            confidence_scores = {}
            details = {}
            recommendations = []
            
            # PII Detection
            pii_threats = await self._detect_pii(content)
            if pii_threats:
                threats_detected.extend([ThreatType.PII_EXPOSURE])
                confidence_scores["pii_exposure"] = max(pii_threats.values())
                details["pii_detected"] = pii_threats
                recommendations.append("Remove or redact detected PII before processing")
            
            # Injection Attack Detection
            injection_threats = await self._detect_injection_attacks(content)
            if injection_threats:
                threats_detected.extend([ThreatType.INJECTION_ATTACK])
                confidence_scores["injection_attack"] = max(injection_threats.values())
                details["injection_detected"] = injection_threats
                recommendations.append("Sanitize input to prevent injection attacks")
            
            # Malicious Content Detection
            malicious_threats = await self._detect_malicious_content(content)
            if malicious_threats:
                threats_detected.extend([ThreatType.MALICIOUS_CONTENT])
                confidence_scores["malicious_content"] = max(malicious_threats.values())
                details["malicious_detected"] = malicious_threats
                recommendations.append("Remove malicious content before processing")
            
            # Privacy Violation Check
            privacy_violations = await self._check_privacy_violations(content, context)
            if privacy_violations:
                threats_detected.extend([ThreatType.PRIVACY_VIOLATION])
                confidence_scores["privacy_violation"] = privacy_violations["confidence"]
                details["privacy_violations"] = privacy_violations
                recommendations.append("Review content for privacy compliance")
            
            # Determine overall status
            if threats_detected:
                max_confidence = max(confidence_scores.values()) if confidence_scores else 0.0
                if max_confidence > 0.8:
                    status = ValidationStatus.FAILED
                elif max_confidence > 0.6:
                    status = ValidationStatus.WARNING
                else:
                    status = ValidationStatus.PASSED
            else:
                status = ValidationStatus.PASSED
            
            processing_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
            
            # Update statistics
            self._validation_stats["total_validations"] += 1
            if threats_detected:
                self._validation_stats["threats_detected"] += 1
            
            result = ValidationResult(
                status=status,
                threats_detected=list(set(threats_detected)),
                confidence_scores=confidence_scores,
                details=details,
                recommendations=recommendations,
                processing_time_ms=processing_time
            )
            
            self.logger.debug(f"Validation completed: {status} in {processing_time}ms")
            return result
            
        except Exception as e:
            processing_time = int((asyncio.get_event_loop().time() - start_time) * 1000)
            self.logger.error(f"Validation failed: {e}")
            
            return ValidationResult(
                status=ValidationStatus.ERROR,
                threats_detected=[ThreatType.COMPLIANCE_BREACH],
                confidence_scores={"error": 1.0},
                details={"error": str(e)},
                recommendations=["Fix validation system error"],
                processing_time_ms=processing_time
            )
    
    async def _detect_pii(self, content: str) -> Dict[str, float]:
        """Detect personally identifiable information."""
        detected = {}
        
        for pii_type, pattern in self._pii_patterns.items():
            matches = pattern.findall(content)
            if matches:
                # Simple confidence based on number of matches
                confidence = min(0.9, 0.5 + (len(matches) * 0.1))
                detected[pii_type] = confidence
        
        return detected
    
    async def _detect_injection_attacks(self, content: str) -> Dict[str, float]:
        """Detect potential injection attacks."""
        detected = {}
        
        for attack_type, pattern in self._malicious_patterns.items():
            matches = pattern.findall(content)
            if matches:
                # Higher confidence for injection attacks
                confidence = min(0.95, 0.7 + (len(matches) * 0.05))
                detected[attack_type] = confidence
        
        return detected
    
    async def _detect_malicious_content(self, content: str) -> Dict[str, float]:
        """Detect malicious content patterns."""
        # Use injection detector for enhanced detection
        try:
            injection_result = await self.injection_detector.detect(content)
            if injection_result.get("threat_detected"):
                return {"malicious_pattern": injection_result.get("confidence", 0.8)}
        except Exception as e:
            self.logger.warning(f"Injection detector failed: {e}")
        
        return {}
    
    async def _check_privacy_violations(self, content: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Check for privacy violations."""
        violations = []
        confidence = 0.0
        
        # Check for sensitive keywords
        sensitive_keywords = ["confidential", "private", "secret", "internal", "proprietary"]
        content_lower = content.lower()
        
        for keyword in sensitive_keywords:
            if keyword in content_lower:
                violations.append(keyword)
                confidence += 0.1
        
        # Check context-specific privacy rules
        if context:
            if context.get("is_public", False) and violations:
                confidence += 0.3
        
        if violations:
            return {
                "violations": violations,
                "confidence": min(0.8, confidence)
            }
        
        return {}
    
    async def generate_safety_report(
        self, 
        validation_results: List[ValidationResult],
        context: Optional[Dict[str, Any]] = None
    ) -> SafetyReport:
        """Generate comprehensive safety report."""
        
        # Calculate overall risk score
        failed_count = sum(1 for r in validation_results if r.status == ValidationStatus.FAILED)
        warning_count = sum(1 for r in validation_results if r.status == ValidationStatus.WARNING)
        
        total_validations = len(validation_results)
        if total_validations == 0:
            risk_score = 0.0
            overall_status = ValidationStatus.PASSED
        else:
            risk_score = (failed_count * 1.0 + warning_count * 0.5) / total_validations
            if failed_count > 0:
                overall_status = ValidationStatus.FAILED
            elif warning_count > 0:
                overall_status = ValidationStatus.WARNING
            else:
                overall_status = ValidationStatus.PASSED
        
        report = SafetyReport(
            report_id=f"safety_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            validation_results=validation_results,
            overall_status=overall_status,
            risk_score=risk_score,
            generated_at=datetime.now(),
            metadata=context or {}
        )
        
        return report
    
    def _load_default_policies(self) -> None:
        """Load default safety policies."""
        policies = [
            SafetyPolicy(
                policy_id="pii_protection",
                name="PII Protection Policy",
                description="Detect and protect personally identifiable information",
                threat_types=[ThreatType.PII_EXPOSURE],
                safety_level=self.safety_level,
                config={"strict_mode": self.safety_level == SafetyLevel.STRICT}
            ),
            SafetyPolicy(
                policy_id="injection_prevention",
                name="Injection Prevention Policy", 
                description="Prevent injection attacks",
                threat_types=[ThreatType.INJECTION_ATTACK],
                safety_level=self.safety_level,
                config={"block_all_injections": self.safety_level == SafetyLevel.STRICT}
            ),
            SafetyPolicy(
                policy_id="content_safety",
                name="Content Safety Policy",
                description="Detect malicious content",
                threat_types=[ThreatType.MALICIOUS_CONTENT],
                safety_level=self.safety_level,
                config={"strict_content_filter": self.safety_level == SafetyLevel.STRICT}
            )
        ]
        
        for policy in policies:
            self._policies[policy.policy_id] = policy
    
    def add_policy(self, policy: SafetyPolicy) -> None:
        """Add a custom safety policy."""
        self._policies[policy.policy_id] = policy
        self.logger.info(f"Added safety policy: {policy.name}")
    
    def remove_policy(self, policy_id: str) -> bool:
        """Remove a safety policy."""
        if policy_id in self._policies:
            del self._policies[policy_id]
            self.logger.info(f"Removed safety policy: {policy_id}")
            return True
        return False
    
    def get_safety_stats(self) -> Dict[str, Any]:
        """Get safety validation statistics."""
        return {
            **self._validation_stats,
            "active_policies": len(self._policies),
            "safety_level": self.safety_level,
        }

# Global safety engine instance
_global_safety_engine: Optional[SafetyEngine] = None

def get_safety_engine(
    safety_level: SafetyLevel = SafetyLevel.STANDARD,
    config: Optional[Dict[str, Any]] = None
) -> SafetyEngine:
    """Get the global safety engine instance."""
    global _global_safety_engine
    if _global_safety_engine is None:
        _global_safety_engine = SafetyEngine(safety_level, config)
    return _global_safety_engine

def reset_safety_engine() -> None:
    """Reset the global safety engine instance (for testing)."""
    global _global_safety_engine
    _global_safety_engine = None

__all__ = [
    "SafetyLevel",
    "ThreatType",
    "ValidationStatus",
    "SafetyPolicy",
    "ValidationResult",
    "SafetyReport",
    "SafetyEngine",
    "get_safety_engine",
    "reset_safety_engine",
]
