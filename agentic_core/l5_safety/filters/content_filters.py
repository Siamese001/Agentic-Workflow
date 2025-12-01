"""
L5 Agentic Core - L5 Safety Layer - Content Filters
Implements L5 Safety Layer for input/output content sanitization and validation
"""

from typing import Dict, List, Optional, Any, Union, Pattern
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import re
import uuid
import time

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FilterType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    INPUT_SANITIZATION = "input_sanitization"
    OUTPUT_SANITIZATION = "output_sanitization"
    INJECTION_PROTECTION = "injection_protection"
    PII_DETECTION = "pii_detection"
    CONTENT_VALIDATION = "content_validation"

class FilterAction(Enum):
    """L5 Filter action enumeration"""
    ALLOW = "allow"
    BLOCK = "block"
    SANITIZE = "sanitize"
    QUARANTINE = "quarantine"
    LOG_ONLY = "log_only"

@dataclass
class FilterConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_content_length: int = 100000  # 100KB
    require_sanitization: bool = True
    block_injection_attempts: bool = True
    detect_pii: bool = True
    fail_on_uncertain: bool = True
    safety_level: str = "strict"

@dataclass
class FilterRule:
    """L5 Filter rule structure with full type safety"""
    rule_id: str
    rule_type: FilterType
    pattern: str
    action: FilterAction
    description: str = ""
    severity: str = "medium"  # "low", "medium", "high", "critical"
    enabled: bool = True
    created_at: str = ""
    safety_validated: bool = False

@dataclass
class FilterResult:
    """L5 Filter result structure"""
    filter_id: str
    original_content: str = ""
    filtered_content: str = ""
    violations: List[Dict[str, Any]] = field(default_factory=list)
    action_taken: FilterAction = FilterAction.ALLOW
    safety_score: float = 1.0  # 0.0 (unsafe) to 1.0 (safe)
    processing_time: float = 0.0
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class FilterOperation:
    """L5 Filter operation structure"""
    operation_id: str
    operation_type: str  # "filter", "validate", "sanitize"
    content: str = ""
    filter_type: FilterType = FilterType.INPUT_SANITIZATION
    result: Optional[FilterResult] = None
    error_message: str = ""
    timestamp: str = ""

class ContentFilter(ABC):
    """L5 Abstract base - ensures L5 safety behavior"""
    
    @abstractmethod
    def filter_content(self, content: str, filter_type: FilterType, constraints: FilterConstraints) -> FilterOperation:
        """Filter content with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, content: str, filter_type: FilterType) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class ContentFilterImpl(ContentFilter):
    """
    L5 Implementation - L5 Safety Layer
    Pure content filtering execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[FilterConstraints] = None):
        self.constraints = constraints or FilterConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize default filter rules
        self.filter_rules: Dict[FilterType, List[FilterRule]] = {
            FilterType.INPUT_SANITIZATION: self._get_input_sanitization_rules(),
            FilterType.OUTPUT_SANITIZATION: self._get_output_sanitization_rules(),
            FilterType.INJECTION_PROTECTION: self._get_injection_protection_rules(),
            FilterType.PII_DETECTION: self._get_pii_detection_rules(),
            FilterType.CONTENT_VALIDATION: self._get_content_validation_rules()
        }
        
        # Compile regex patterns for performance
        self.compiled_patterns: Dict[str, Pattern] = {}
        self._compile_patterns()
    
    def filter_content(self, content: str, filter_type: FilterType, constraints: Optional[FilterConstraints] = None) -> FilterOperation:
        """Filter content following L5 architecture principles"""
        filter_constraints = constraints or self.constraints
        operation_id = self._generate_operation_id()
        
        self.logger.info(f"Filtering content with type: {filter_type.value}")
        
        # L5 Input validation
        self._validate_filter_input(content, filter_type)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(content, filter_type):
            raise SecurityError("Content filtering failed L5 safety validation")
        
        start_time = time.time()
        
        try:
            # Check content length
            if len(content) > filter_constraints.max_content_length:
                return FilterOperation(
                    operation_id=operation_id,
                    operation_type="filter",
                    content=content,
                    filter_type=filter_type,
                    error_message=f"Content too long: {len(content)} > {filter_constraints.max_content_length}",
                    timestamp=self._get_timestamp()
                )
            
            # Apply filters based on type
            violations = []
            filtered_content = content
            action_taken = FilterAction.ALLOW
            
            rules = self.filter_rules.get(filter_type, [])
            
            for rule in rules:
                if not rule.enabled:
                    continue
                
                rule_result = self._apply_rule(content, rule, filter_constraints)
                if rule_result["violation"]:
                    violations.append({
                        "rule_id": rule.rule_id,
                        "pattern": rule.pattern,
                        "action": rule.action.value,
                        "severity": rule.severity,
                        "description": rule.description,
                        "matches": rule_result["matches"]
                    })
                    
                    # Determine action based on rule severity and action
                    if rule.action in [FilterAction.BLOCK, FilterAction.QUARANTINE]:
                        action_taken = rule.action
                        break  # Stop on first blocking violation
                    elif rule.action == FilterAction.SANITIZE:
                        filtered_content = rule_result["sanitized_content"]
                        action_taken = FilterAction.SANITIZE
            
            # Calculate safety score
            safety_score = self._calculate_safety_score(violations, len(content))
            
            # Fail-closed if uncertain
            if filter_constraints.fail_on_uncertain and safety_score < 0.5:
                action_taken = FilterAction.BLOCK
            
            # Create filter result
            processing_time = time.time() - start_time
            filter_result = FilterResult(
                filter_id=self._generate_filter_id(),
                original_content=content,
                filtered_content=filtered_content,
                violations=violations,
                action_taken=action_taken,
                safety_score=safety_score,
                processing_time=processing_time,
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
            
            # Create operation result
            operation = FilterOperation(
                operation_id=operation_id,
                operation_type="filter",
                content=content,
                filter_type=filter_type,
                result=filter_result,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Content filtered successfully: {action_taken.value} (score: {safety_score:.2f})")
            return operation
            
        except Exception as e:
            self.logger.error(f"Content filtering error: {e}")
            return FilterOperation(
                operation_id=operation_id,
                operation_type="filter",
                content=content,
                filter_type=filter_type,
                error_message=str(e),
                timestamp=self._get_timestamp()
            )
    
    def _apply_rule(self, content: str, rule: FilterRule, constraints: FilterConstraints) -> Dict[str, Any]:
        """Apply individual filter rule"""
        result = {
            "violation": False,
            "matches": [],
            "sanitized_content": content
        }
        
        try:
            # Get compiled pattern
            pattern = self.compiled_patterns.get(rule.pattern)
            if not pattern:
                self.logger.warning(f"Pattern not compiled: {rule.pattern}")
                return result
            
            # Find matches
            matches = list(pattern.finditer(content))
            
            if matches:
                result["violation"] = True
                result["matches"] = [match.group() for match in matches]
                
                # Apply sanitization if required
                if rule.action == FilterAction.SANITIZE:
                    result["sanitized_content"] = pattern.sub("[FILTERED]", content)
        
        except Exception as e:
            self.logger.error(f"Rule application error: {e}")
        
        return result
    
    def _calculate_safety_score(self, violations: List[Dict[str, Any]], content_length: int) -> float:
        """Calculate safety score based on violations"""
        if not violations:
            return 1.0
        
        # Weight violations by severity
        severity_weights = {"low": 0.1, "medium": 0.3, "high": 0.6, "critical": 1.0}
        total_penalty = 0.0
        
        for violation in violations:
            severity = violation.get("severity", "medium")
            weight = severity_weights.get(severity, 0.3)
            total_penalty += weight
        
        # Normalize score
        score = max(0.0, 1.0 - total_penalty)
        return score
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for performance"""
        for filter_type, rules in self.filter_rules.items():
            for rule in rules:
                try:
                    pattern = re.compile(rule.pattern, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                    self.compiled_patterns[rule.pattern] = pattern
                except re.error as e:
                    self.logger.error(f"Failed to compile pattern {rule.pattern}: {e}")
    
    def _get_input_sanitization_rules(self) -> List[FilterRule]:
        """Get input sanitization rules"""
        return [
            FilterRule(
                rule_id="input_script_tags",
                rule_type=FilterType.INPUT_SANITIZATION,
                pattern=r'<script[^>]*>.*?</script>',
                action=FilterAction.BLOCK,
                description="Block script tags",
                severity="critical",
                safety_validated=True
            ),
            FilterRule(
                rule_id="input_javascript_urls",
                rule_type=FilterType.INPUT_SANITIZATION,
                pattern=r'javascript:[^\\s]*',
                action=FilterAction.BLOCK,
                description="Block JavaScript URLs",
                severity="critical",
                safety_validated=True
            ),
            FilterRule(
                rule_id="input_html_entities",
                rule_type=FilterType.INPUT_SANITIZATION,
                pattern=r'[<>&"\']',
                action=FilterAction.SANITIZE,
                description="Sanitize HTML entities",
                severity="medium",
                safety_validated=True
            )
        ]
    
    def _get_output_sanitization_rules(self) -> List[FilterRule]:
        """Get output sanitization rules"""
        return [
            FilterRule(
                rule_id="output_sensitive_info",
                rule_type=FilterType.OUTPUT_SANITIZATION,
                pattern=r'(password|secret|token|key)\s*[:=]\s*[\\w\\-]+',
                action=FilterAction.SANITIZE,
                description="Sanitize sensitive information",
                severity="high",
                safety_validated=True
            ),
            FilterRule(
                rule_id="output_debug_info",
                rule_type=FilterType.OUTPUT_SANITIZATION,
                pattern=r'(debug|trace|stack trace|error details)[:\\s]*[^\\n]*',
                action=FilterAction.SANITIZE,
                description="Sanitize debug information",
                severity="medium",
                safety_validated=True
            )
        ]
    
    def _get_injection_protection_rules(self) -> List[FilterRule]:
        """Get injection protection rules"""
        return [
            FilterRule(
                rule_id="sql_injection",
                rule_type=FilterType.INJECTION_PROTECTION,
                pattern=r'(?i)(union|select|insert|update|delete|drop|exec|script)',
                action=FilterAction.BLOCK,
                description="Block SQL injection attempts",
                severity="critical",
                safety_validated=True
            ),
            FilterRule(
                rule_id="command_injection",
                rule_type=FilterType.INJECTION_PROTECTION,
                pattern=r'[;&|`$(){}\\[\\]]',
                action=FilterAction.BLOCK,
                description="Block command injection attempts",
                severity="critical",
                safety_validated=True
            ),
            FilterRule(
                rule_id="eval_injection",
                rule_type=FilterType.INJECTION_PROTECTION,
                pattern=r'(?i)(eval|exec|system|shell_exec|passthru)',
                action=FilterAction.BLOCK,
                description="Block eval injection attempts",
                severity="critical",
                safety_validated=True
            )
        ]
    
    def _get_pii_detection_rules(self) -> List[FilterRule]:
        """Get PII detection rules"""
        return [
            FilterRule(
                rule_id="email_addresses",
                rule_type=FilterType.PII_DETECTION,
                pattern=r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b',
                action=FilterAction.SANITIZE,
                description="Detect and sanitize email addresses",
                severity="high",
                safety_validated=True
            ),
            FilterRule(
                rule_id="phone_numbers",
                rule_type=FilterType.PII_DETECTION,
                pattern=r'\\b(?:\\+?1[-.\\s]?)?\\(?([0-9]{3})\\)?[-.\\s]?([0-9]{3})[-.\\s]?([0-9]{4})\\b',
                action=FilterAction.SANITIZE,
                description="Detect and sanitize phone numbers",
                severity="high",
                safety_validated=True
            ),
            FilterRule(
                rule_id="ssn_pattern",
                rule_type=FilterType.PII_DETECTION,
                pattern=r'\\b\\d{3}-\\d{2}-\\d{4}\\b',
                action=FilterAction.BLOCK,
                description="Block SSN patterns",
                severity="critical",
                safety_validated=True
            ),
            FilterRule(
                rule_id="credit_card",
                rule_type=FilterType.PII_DETECTION,
                pattern=r'\\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\\b',
                action=FilterAction.BLOCK,
                description="Block credit card numbers",
                severity="critical",
                safety_validated=True
            )
        ]
    
    def _get_content_validation_rules(self) -> List[FilterRule]:
        """Get content validation rules"""
        return [
            FilterRule(
                rule_id="null_bytes",
                rule_type=FilterType.CONTENT_VALIDATION,
                pattern=r'\\x00',
                action=FilterAction.BLOCK,
                description="Block null bytes",
                severity="high",
                safety_validated=True
            ),
            FilterRule(
                rule_id="control_characters",
                rule_type=FilterType.CONTENT_VALIDATION,
                pattern=r'[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x7f]',
                action=FilterAction.SANITIZE,
                description="Sanitize control characters",
                severity="medium",
                safety_validated=True
            ),
            FilterRule(
                rule_id="unicode_exploits",
                rule_type=FilterType.CONTENT_VALIDATION,
                pattern=r'[\\u202e\\u200e\\u200f]',
                action=FilterAction.SANITIZE,
                description="Sanitize Unicode exploit characters",
                severity="medium",
                safety_validated=True
            )
        ]
    
    def validate_safety(self, content: str, filter_type: FilterType) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check content safety
            if not content:
                return True  # Empty content is safe
            
            # Check for extremely dangerous patterns
            dangerous_patterns = [
                r'(?i)<script[^>]*>.*?</script>',
                r'(?i)javascript:[^\\s]*',
                r'(?i)eval\\s*\\(',
                r'(?i)exec\\s*\\(',
                r'(?i)system\\s*\\('
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self.logger.error(f"Dangerous pattern detected: {pattern}")
                    return False
            
            # Check content length
            if len(content) > self.constraints.max_content_length:
                self.logger.error("Content exceeds maximum length")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_filter_input(self, content: str, filter_type: FilterType) -> None:
        """L5 Filter input validation"""
        if not isinstance(content, str):
            raise ValueError("Content must be a string")
        
        if not isinstance(filter_type, FilterType):
            raise ValueError("Filter type must be a FilterType enum")
    
    def _generate_operation_id(self) -> str:
        """Generate unique operation ID"""
        return f"filter_op_{uuid.uuid4().hex[:8]}"
    
    def _generate_filter_id(self) -> str:
        """Generate unique filter ID"""
        return f"filter_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class ContentFilterInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, filter: ContentFilter):
        self._filter = filter
    
    def filter_content(self, content: str, filter_type: str = "input_sanitization", max_length: int = 100000) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            ft_type = FilterType(filter_type)
            constraints = FilterConstraints(max_content_length=max_length)
            
            operation = self._filter.filter_content(content, ft_type, constraints)
            
            if operation.result:
                return {
                    "success": operation.error_message == "",
                    "operation_id": operation.operation_id,
                    "operation_type": operation.operation_type,
                    "filter_type": operation.filter_type.value,
                    "original_content": operation.result.original_content,
                    "filtered_content": operation.result.filtered_content,
                    "violations": operation.result.violations,
                    "action_taken": operation.result.action_taken.value,
                    "safety_score": operation.result.safety_score,
                    "processing_time": operation.result.processing_time,
                    "safety_validated": operation.result.safety_validated,
                    "timestamp": operation.result.timestamp
                }
            else:
                return {
                    "success": False,
                    "error": operation.error_message,
                    "safety_validated": False
                }
        except Exception as e:
            self.logger.error(f"Content filtering failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class ContentFilterFactory:
    """L5 Factory for creating content filter instances"""
    
    @staticmethod
    def create_filter(constraints: Optional[FilterConstraints] = None) -> ContentFilter:
        return ContentFilterImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[FilterConstraints] = None) -> ContentFilterInterface:
        filter = ContentFilterFactory.create_filter(constraints)
        return ContentFilterInterface(filter)

# L5 Export for module usage
__all__ = [
    "FilterType",
    "FilterAction",
    "FilterConstraints",
    "FilterRule",
    "FilterResult",
    "FilterOperation",
    "ContentFilter",
    "ContentFilterImpl",
    "ContentFilterInterface",
    "ContentFilterFactory",
    "SecurityError"
]
