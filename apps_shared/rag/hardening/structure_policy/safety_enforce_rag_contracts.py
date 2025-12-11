"""Safety-Enhanced RAG Contracts Enforcement - Enforces RAG contracts with safety-first approach.

This module provides enhanced contract enforcement with additional safety checks,
including content filtering, privacy protection, and security validation.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Set
import logging
import re
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SafetyRiskLevel(Enum):
    """Safety risk levels for content."""
    SAFE = "safe"
    LOW_RISK = "low_risk"
    MEDIUM_RISK = "medium_risk"
    HIGH_RISK = "high_risk"
    BLOCKED = "blocked"


class ContentType(Enum):
    """Types of content to check."""
    TEXT = "text"
    QUERY = "query"
    DOCUMENT = "document"
    RESPONSE = "response"
    METADATA = "metadata"


@dataclass
class SafetyCheck:
    """Definition of a safety check."""
    id: str
    name: str
    risk_level: SafetyRiskLevel
    content_types: List[ContentType]
    pattern: str  # Regex pattern or function name
    action: str  # warn, block, sanitize, audit
    description: str = ""


@dataclass
class SafetyViolation:
    """Record of a safety violation."""
    check_id: str
    check_name: str
    risk_level: SafetyRiskLevel
    content_type: ContentType
    detected_content: str
    sanitized_content: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SafetyEnforcementResult:
    """Result of safety contract enforcement."""
    safe: bool
    risk_level: SafetyRiskLevel
    violations: List[SafetyViolation] = field(default_factory=list)
    sanitized_content: Dict[str, Any] = field(default_factory=dict)
    blocked_content: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyRAGConfig:
    """Configuration for safety-enhanced RAG enforcement."""
    enable_content_filtering: bool = True
    enable_pii_detection: bool = True
    enable_toxicity_check: bool = True
    sanitize_blocked_content: bool = True
    log_violations: bool = True
    risk_threshold: str = "medium_risk"
    custom_patterns: Dict[str, str] = field(default_factory=dict)
    allowed_domains: Set[str] = field(default_factory=set)
    blocked_keywords: Set[str] = field(default_factory=set)
    log_level: str = "INFO"


class SafetyRAGContractsEnforcer:
    """Main class for safety-enhanced RAG contract enforcement."""

    def __init__(self, config: Optional[SafetyRAGConfig] = None):
        self.config = config or SafetyRAGConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.config.log_level)
        self._safety_checks = []
        self._load_safety_checks()

    def enforce_safety(self, operation: Dict[str, Any]) -> SafetyEnforcementResult:
        """Enforce safety contracts on a RAG operation.
        
        Args:
            operation: RAG operation data to validate
            
        Returns:
            SafetyEnforcementResult: Result of safety enforcement
        """
        self.logger.info(f"Enforcing safety on RAG operation: {operation.get('type', 'unknown')}")
        
        violations = []
        sanitized_content = {}
        blocked_content = []
        warnings = []
        overall_risk = SafetyRiskLevel.SAFE
        
        try:
            # Extract content from operation
            content_map = self._extract_content(operation)
            
            # Run safety checks on all content
            for content_type, content in content_map.items():
                if not content:
                    continue
                
                for check in self._safety_checks:
                    if content_type in check.content_types:
                        violation = self._run_safety_check(check, content, content_type)
                        
                        if violation:
                            violations.append(violation)
                            
                            # Update overall risk level
                            if self._risk_level_greater(violation.risk_level, overall_risk):
                                overall_risk = violation.risk_level
                            
                            # Take action based on check
                            if check.action == "block":
                                blocked_content.append(content_type.value)
                            elif check.action == "sanitize" and violation.sanitized_content:
                                sanitized_content[content_type.value] = violation.sanitized_content
                            elif check.action == "warn":
                                warnings.append(f"Safety warning: {check.name}")
            
            # Determine if operation is safe
            safe = overall_risk in [SafetyRiskLevel.SAFE, SafetyRiskLevel.LOW_RISK]
            
            result = SafetyEnforcementResult(
                safe=safe,
                risk_level=overall_risk,
                violations=violations,
                sanitized_content=sanitized_content,
                blocked_content=blocked_content,
                warnings=warnings,
                metadata={
                    "enforced_at": datetime.utcnow().isoformat(),
                    "checks_run": len(self._safety_checks),
                    "content_types_checked": list(content_map.keys()),
                    "enforcer": "SafetyRAGContractsEnforcer"
                }
            )
            
            # Log violations if enabled
            if self.config.log_violations and violations:
                self._log_safety_violations(operation, violations)
            
            self.logger.info(
                f"Safety enforcement completed: {overall_risk.value} risk level "
                f"({len(violations)} violations)"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Safety enforcement failed: {str(e)}")
            return SafetyEnforcementResult(
                safe=False,
                risk_level=SafetyRiskLevel.HIGH_RISK,
                violations=[SafetyViolation(
                    check_id="system_error",
                    check_name="System Error",
                    risk_level=SafetyRiskLevel.HIGH_RISK,
                    content_type=ContentType.TEXT,
                    detected_content=str(e)
                )],
                metadata={"error": str(e)}
            )

    def _extract_content(self, operation: Dict[str, Any]) -> Dict[ContentType, str]:
        """Extract all content from operation for safety checking."""
        content_map = {}
        
        # Extract query
        if "query" in operation:
            content_map[ContentType.QUERY] = str(operation["query"])
        
        # Extract documents
        if "documents" in operation:
            docs = operation["documents"]
            if isinstance(docs, list):
                content_map[ContentType.DOCUMENT] = " ".join(str(d) for d in docs)
            else:
                content_map[ContentType.DOCUMENT] = str(docs)
        
        # Extract response
        if "response" in operation:
            content_map[ContentType.RESPONSE] = str(operation["response"])
        
        # Extract metadata
        if "metadata" in operation:
            content_map[ContentType.METADATA] = str(operation["metadata"])
        
        # Extract general text content
        if "text" in operation:
            content_map[ContentType.TEXT] = str(operation["text"])
        
        return content_map

    def _load_safety_checks(self) -> None:
        """Load default safety checks."""
        # PII detection checks
        if self.config.enable_pii_detection:
            self._safety_checks.extend([
                SafetyCheck(
                    id="email_detection",
                    name="Email Address Detection",
                    risk_level=SafetyRiskLevel.MEDIUM_RISK,
                    content_types=[ContentType.QUERY, ContentType.DOCUMENT, ContentType.RESPONSE],
                    pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    action="sanitize",
                    description="Detects and sanitizes email addresses"
                ),
                SafetyCheck(
                    id="phone_detection",
                    name="Phone Number Detection",
                    risk_level=SafetyRiskLevel.MEDIUM_RISK,
                    content_types=[ContentType.QUERY, ContentType.DOCUMENT, ContentType.RESPONSE],
                    pattern=r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                    action="sanitize",
                    description="Detects and sanitizes phone numbers"
                ),
                SafetyCheck(
                    id="ssn_detection",
                    name="Social Security Number Detection",
                    risk_level=SafetyRiskLevel.HIGH_RISK,
                    content_types=[ContentType.QUERY, ContentType.DOCUMENT, ContentType.RESPONSE],
                    pattern=r'\b\d{3}-\d{2}-\d{4}\b',
                    action="block",
                    description="Blocks content containing SSN patterns"
                ),
                SafetyCheck(
                    id="credit_card_detection",
                    name="Credit Card Number Detection",
                    risk_level=SafetyRiskLevel.HIGH_RISK,
                    content_types=[ContentType.QUERY, ContentType.DOCUMENT, ContentType.RESPONSE],
                    pattern=r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                    action="block",
                    description="Blocks content containing credit card patterns"
                )
            ])
        
        # Toxicity checks
        if self.config.enable_toxicity_check:
            self._safety_checks.extend([
                SafetyCheck(
                    id="hate_speech",
                    name="Hate Speech Detection",
                    risk_level=SafetyRiskLevel.HIGH_RISK,
                    content_types=[ContentType.QUERY, ContentType.RESPONSE],
                    pattern=r'\b(hate|kill|harm|violence)\b',
                    action="block",
                    description="Blocks hate speech content"
                ),
                SafetyCheck(
                    id="inappropriate_content",
                    name="Inappropriate Content Detection",
                    risk_level=SafetyRiskLevel.MEDIUM_RISK,
                    content_types=[ContentType.QUERY, ContentType.RESPONSE],
                    pattern=r'\b(curse|swear|profanity)\b',
                    action="warn",
                    description="Warns about inappropriate content"
                )
            ])
        
        # Add custom patterns
        for check_id, pattern in self.config.custom_patterns.items():
            self._safety_checks.append(SafetyCheck(
                id=check_id,
                name=f"Custom Check: {check_id}",
                risk_level=SafetyRiskLevel.MEDIUM_RISK,
                content_types=[ContentType.QUERY, ContentType.DOCUMENT, ContentType.RESPONSE],
                pattern=pattern,
                action="warn",
                description="Custom safety check"
            ))

    def _run_safety_check(self, check: SafetyCheck, content: str, content_type: ContentType) -> Optional[SafetyViolation]:
        """Run a single safety check on content."""
        try:
            # Check if pattern matches
            matches = re.findall(check.pattern, content, re.IGNORECASE)
            
            if matches:
                # Determine action based on check configuration
                sanitized = None
                if check.action == "sanitize" and self.config.sanitize_blocked_content:
                    sanitized = self._sanitize_content(content, check.pattern)
                
                return SafetyViolation(
                    check_id=check.id,
                    check_name=check.name,
                    risk_level=check.risk_level,
                    content_type=content_type,
                    detected_content=str(matches[:3]),  # Limit to first 3 matches
                    sanitized_content=sanitized
                )
        except Exception as e:
            self.logger.warning(f"Failed to run safety check {check.id}: {str(e)}")
        
        return None

    def _sanitize_content(self, content: str, pattern: str) -> str:
        """Sanitize content by replacing matched patterns."""
        try:
            # Replace matches with placeholder
            sanitized = re.sub(pattern, "[REDACTED]", content, flags=re.IGNORECASE)
            return sanitized
        except:
            return "[SANITIZATION_FAILED]"

    def _risk_level_greater(self, level1: SafetyRiskLevel, level2: SafetyRiskLevel) -> bool:
        """Check if level1 is higher risk than level2."""
        risk_order = {
            SafetyRiskLevel.SAFE: 0,
            SafetyRiskLevel.LOW_RISK: 1,
            SafetyRiskLevel.MEDIUM_RISK: 2,
            SafetyRiskLevel.HIGH_RISK: 3,
            SafetyRiskLevel.BLOCKED: 4
        }
        return risk_order.get(level1, 0) > risk_order.get(level2, 0)

    def _log_safety_violations(self, operation: Dict[str, Any], violations: List[SafetyViolation]) -> None:
        """Log safety violations for audit."""
        for violation in violations:
            log_entry = {
                "timestamp": violation.timestamp.isoformat(),
                "operation_id": operation.get("id"),
                "check_id": violation.check_id,
                "risk_level": violation.risk_level.value,
                "content_type": violation.content_type.value,
                "detected_content": violation.detected_content
            }
            self.logger.warning(f"Safety violation: {log_entry}")

    def add_safety_check(self, check: SafetyCheck) -> None:
        """Add a custom safety check.
        
        Args:
            check: Safety check to add
        """
        self.logger.info(f"Adding safety check: {check.id}")
        self._safety_checks.append(check)

    def get_safety_summary(self) -> Dict[str, Any]:
        """Get summary of safety checks and configuration.
        
        Returns:
            Dict: Safety configuration summary
        """
        return {
            "total_safety_checks": len(self._safety_checks),
            "content_filtering_enabled": self.config.enable_content_filtering,
            "pii_detection_enabled": self.config.enable_pii_detection,
            "toxicity_check_enabled": self.config.enable_toxicity_check,
            "risk_threshold": self.config.risk_threshold,
            "blocked_keywords_count": len(self.config.blocked_keywords),
            "custom_patterns_count": len(self.config.custom_patterns)
        }


# Factory function for easy instantiation
def create_safety_rag_enforcer(
    enable_content_filtering: bool = True,
    enable_pii_detection: bool = True,
    enable_toxicity_check: bool = True,
    risk_threshold: str = "medium_risk",
    **kwargs
) -> SafetyRAGContractsEnforcer:
    """Create a configured safety RAG contracts enforcer."""
    config = SafetyRAGConfig(
        enable_content_filtering=enable_content_filtering,
        enable_pii_detection=enable_pii_detection,
        enable_toxicity_check=enable_toxicity_check,
        risk_threshold=risk_threshold,
        **kwargs
    )
    return SafetyRAGContractsEnforcer(config)


# Convenience function for direct usage
def enforce_rag_safety(
    operation: Dict[str, Any],
    enable_content_filtering: bool = True,
    enable_pii_detection: bool = True,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Enforce safety contracts on a RAG operation.
    
    Args:
        operation: RAG operation to validate
        enable_content_filtering: Whether to enable content filtering
        enable_pii_detection: Whether to enable PII detection
        config: Optional enforcer configuration overrides
        
    Returns:
        Dict: Safety enforcement result with violations and actions
    """
    # Create enforcer and execute
    enforcer_config = SafetyRAGConfig(
        enable_content_filtering=enable_content_filtering,
        enable_pii_detection=enable_pii_detection,
        **config or {}
    )
    enforcer = SafetyRAGContractsEnforcer(enforcer_config)
    result = enforcer.enforce_safety(operation)
    
    # Convert result to dict for JSON serialization
    return {
        "safe": result.safe,
        "risk_level": result.risk_level.value,
        "violations": [
            {
                "check_id": v.check_id,
                "check_name": v.check_name,
                "risk_level": v.risk_level.value,
                "content_type": v.content_type.value,
                "detected_content": v.detected_content,
                "sanitized_content": v.sanitized_content,
                "timestamp": v.timestamp.isoformat()
            }
            for v in result.violations
        ],
        "sanitized_content": result.sanitized_content,
        "blocked_content": result.blocked_content,
        "warnings": result.warnings,
        "metadata": result.metadata
    }
