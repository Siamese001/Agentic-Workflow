"""
Safety Validator Implementation for Safety Layer
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ValidationLevel(Enum):
    """Levels of validation severity"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """A validation issue found"""
    level: ValidationLevel
    message: str
    field: str
    value: Any
    suggestion: str
    timestamp: datetime
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ValidationResult:
    """Result of safety validation"""
    is_valid: bool
    issues: List[ValidationIssue]
    score: float
    timestamp: datetime
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class SafetyValidator:
    """Safety validation system for content and operations"""
    
    def __init__(self):
        self.validation_rules: Dict[str, Callable] = {}
        self.validation_history: List[ValidationResult] = []
        self.thresholds: Dict[str, float] = {
            "min_score": 0.7,
            "max_critical_issues": 0,
            "max_error_issues": 3,
            "max_warning_issues": 10
        }
        self.stats = {
            "total_validations": 0,
            "passed_validations": 0,
            "failed_validations": 0,
            "critical_issues_found": 0,
            "error_issues_found": 0,
            "warning_issues_found": 0
        }
        self.created_at = datetime.now()
    
    def add_validation_rule(self, rule_name: str, validator: Callable):
        """Add a validation rule"""
        self.validation_rules[rule_name] = validator
    
    def set_threshold(self, threshold_name: str, value: float):
        """Set a validation threshold"""
        self.thresholds[threshold_name] = value
    
    def validate_content(self, content: str, context: Dict[str, Any] = None) -> ValidationResult:
        """Validate content against all safety rules"""
        issues = []
        
        # Apply all validation rules
        for rule_name, validator in self.validation_rules.items():
            try:
                rule_issues = validator(content, context or {})
                issues.extend(rule_issues)
            except Exception:
                # Log validation error but continue
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Validation rule '{rule_name}' failed to execute",
                    field="validation_error",
                    value=None,
                    suggestion="Check validation rule implementation",
                    timestamp=datetime.now()
                ))
        
        # Calculate validation score
        score = self._calculate_score(issues)
        
        # Determine if validation passes
        is_valid = self._is_valid_result(issues, score)
        
        result = ValidationResult(
            is_valid=is_valid,
            issues=issues,
            score=score,
            timestamp=datetime.now()
        )
        
        self.validation_history.append(result)
        self._update_stats(issues, is_valid)
        
        return result
    
    def validate_operation(self, operation: str, parameters: Dict[str, Any], context: Dict[str, Any] = None) -> ValidationResult:
        """Validate an operation and its parameters"""
        issues = []
        
        # Validate operation name
        if not operation or not isinstance(operation, str):
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message="Operation name must be a non-empty string",
                field="operation",
                value=operation,
                suggestion="Provide a valid operation name",
                timestamp=datetime.now()
            ))
        
        # Validate parameters
        if not isinstance(parameters, dict):
            issues.append(ValidationIssue(
                level=ValidationLevel.ERROR,
                message="Parameters must be a dictionary",
                field="parameters",
                value=parameters,
                suggestion="Provide parameters as a dictionary",
                timestamp=datetime.now()
            ))
        
        # Apply operation-specific validation rules
        operation_rule = f"operation_{operation}"
        if operation_rule in self.validation_rules:
            try:
                rule_issues = self.validation_rules[operation_rule](parameters, context or {})
                issues.extend(rule_issues)
            except Exception:
                issues.append(ValidationIssue(
                    level=ValidationLevel.ERROR,
                    message=f"Operation validation rule for '{operation}' failed",
                    field="validation_error",
                    value=None,
                    suggestion="Check operation validation rule",
                    timestamp=datetime.now()
                ))
        
        # Calculate score and validity
        score = self._calculate_score(issues)
        is_valid = self._is_valid_result(issues, score)
        
        result = ValidationResult(
            is_valid=is_valid,
            issues=issues,
            score=score,
            timestamp=datetime.now()
        )
        
        self.validation_history.append(result)
        self._update_stats(issues, is_valid)
        
        return result
    
    def _calculate_score(self, issues: List[ValidationIssue]) -> float:
        """Calculate validation score based on issues"""
        if not issues:
            return 1.0
        
        # Weight issues by severity
        critical_count = sum(1 for issue in issues if issue.level == ValidationLevel.CRITICAL)
        error_count = sum(1 for issue in issues if issue.level == ValidationLevel.ERROR)
        warning_count = sum(1 for issue in issues if issue.level == ValidationLevel.WARNING)
        info_count = sum(1 for issue in issues if issue.level == ValidationLevel.INFO)
        
        # Deduct points based on severity
        score = 1.0
        score -= critical_count * 0.5
        score -= error_count * 0.2
        score -= warning_count * 0.1
        score -= info_count * 0.05
        
        return max(0.0, score)
    
    def _is_valid_result(self, issues: List[ValidationIssue], score: float) -> bool:
        """Determine if validation result is acceptable"""
        # Check score threshold
        if score < self.thresholds["min_score"]:
            return False
        
        # Check critical issues
        critical_count = sum(1 for issue in issues if issue.level == ValidationLevel.CRITICAL)
        if critical_count > self.thresholds["max_critical_issues"]:
            return False
        
        # Check error issues
        error_count = sum(1 for issue in issues if issue.level == ValidationLevel.ERROR)
        if error_count > self.thresholds["max_error_issues"]:
            return False
        
        # Check warning issues
        warning_count = sum(1 for issue in issues if issue.level == ValidationLevel.WARNING)
        if warning_count > self.thresholds["max_warning_issues"]:
            return False
        
        return True
    
    def _update_stats(self, issues: List[ValidationIssue], is_valid: bool):
        """Update validation statistics"""
        self.stats["total_validations"] += 1
        
        if is_valid:
            self.stats["passed_validations"] += 1
        else:
            self.stats["failed_validations"] += 1
        
        # Count issue types
        for issue in issues:
            if issue.level == ValidationLevel.CRITICAL:
                self.stats["critical_issues_found"] += 1
            elif issue.level == ValidationLevel.ERROR:
                self.stats["error_issues_found"] += 1
            elif issue.level == ValidationLevel.WARNING:
                self.stats["warning_issues_found"] += 1
    
    def get_validation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent validation history"""
        recent_validations = self.validation_history[-limit:]
        return [
            {
                "is_valid": result.is_valid,
                "score": result.score,
                "issue_count": len(result.issues),
                "issues": [
                    {
                        "level": issue.level.value,
                        "message": issue.message,
                        "field": issue.field,
                        "suggestion": issue.suggestion
                    }
                    for issue in result.issues
                ],
                "timestamp": result.timestamp.isoformat()
            }
            for result in recent_validations
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        total = self.stats["total_validations"]
        if total > 0:
            pass_rate = self.stats["passed_validations"] / total
        else:
            pass_rate = 0.0
        
        return {
            "stats": self.stats.copy(),
            "pass_rate": pass_rate,
            "rules_count": len(self.validation_rules),
            "thresholds": self.thresholds.copy(),
            "created_at": self.created_at.isoformat()
        }
    
    def add_common_rules(self):
        """Add common validation rules"""
        
        # Content length rule
        def validate_length(content: str, context: Dict[str, Any]) -> List[ValidationIssue]:
            issues = []
            if len(content) > 10000:
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="Content is very long",
                    field="content_length",
                    value=len(content),
                    suggestion="Consider splitting content into smaller chunks",
                    timestamp=datetime.now()
                ))
            return issues
        
        # Personal information rule
        def validate_personal_info(content: str, context: Dict[str, Any]) -> List[ValidationIssue]:
            import re
            issues = []
            
            # Email pattern
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if re.search(email_pattern, content):
                issues.append(ValidationIssue(
                    level=ValidationLevel.WARNING,
                    message="Email address detected in content",
                    field="personal_info",
                    value="email",
                    suggestion="Remove or mask personal information",
                    timestamp=datetime.now()
                ))
            
            return issues
        
        # Malicious content rule
        def validate_malicious_content(content: str, context: Dict[str, Any]) -> List[ValidationIssue]:
            issues = []
            malicious_patterns = [
                "drop table", "delete from", "insert into",
                "<script>", "javascript:", "eval(",
                "exec(", "system(", "shell_exec"
            ]
            
            content_lower = content.lower()
            for pattern in malicious_patterns:
                if pattern in content_lower:
                    issues.append(ValidationIssue(
                        level=ValidationLevel.CRITICAL,
                        message=f"Potentially malicious pattern detected: {pattern}",
                        field="malicious_content",
                        value=pattern,
                        suggestion="Remove malicious code patterns",
                        timestamp=datetime.now()
                    ))
            
            return issues
        
        # Add the rules
        self.add_validation_rule("length", validate_length)
        self.add_validation_rule("personal_info", validate_personal_info)
        self.add_validation_rule("malicious_content", validate_malicious_content)
    
    def clear_history(self):
        """Clear validation history"""
        self.validation_history.clear()
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "total_validations": 0,
            "passed_validations": 0,
            "failed_validations": 0,
            "critical_issues_found": 0,
            "error_issues_found": 0,
            "warning_issues_found": 0
        }
    
    def __str__(self):
        return f"SafetyValidator(rules={len(self.validation_rules)}, validations={self.stats['total_validations']})"
    
    def __repr__(self):
        return self.__str__()
