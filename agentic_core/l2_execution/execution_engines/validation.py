"""
L5 Agentic Core - L2 Execution Layer - Validation Engine
Implements L2 Pure Execution Layer for comprehensive input/output validation
"""

from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import re
import json

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    SCHEMA = "schema"
    TYPE = "type"
    RANGE = "range"
    PATTERN = "pattern"
    CUSTOM = "custom"
    SAFETY = "safety"

class ValidationStatus(Enum):
    """L5 Validation status enumeration"""
    VALID = "valid"
    INVALID = "invalid"
    ERROR = "error"
    BLOCKED = "blocked"

@dataclass
class ValidationConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_input_size: int = 100000  # 100KB
    max_validation_time: float = 5.0
    require_safety_check: bool = True
    block_dangerous_content: bool = True
    safety_level: str = "strict"

@dataclass
class ValidationRule:
    """L5 Validation rule structure with full type safety"""
    rule_id: str
    validation_type: ValidationType
    field_path: str  # JSONPath-like field path
    parameters: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    required: bool = True

@dataclass
class ValidationResult:
    """L5 Validation result structure"""
    rule_id: str
    field_path: str
    status: ValidationStatus
    error_message: str = ""
    actual_value: Any = None
    expected_value: Any = None
    timestamp: str = ""

@dataclass
class ValidationReport:
    """L5 Validation report structure"""
    validation_id: str
    input_data: Any
    overall_status: ValidationStatus
    results: List[ValidationResult] = field(default_factory=list)
    blocked_content: List[str] = field(default_factory=list)
    safety_validated: bool = False
    validation_time: float = 0.0
    timestamp: str = ""

class ValidationEngine(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def validate(self, data: Any, rules: List[ValidationRule], constraints: ValidationConstraints) -> ValidationReport:
        """Validate data with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, data: Any) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class ValidationEngineImpl(ValidationEngine):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure validation execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[ValidationConstraints] = None):
        self.constraints = constraints or ValidationConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.custom_validators: Dict[str, Callable] = {}
        self._initialize_default_validators()
    
    def _initialize_default_validators(self):
        """Initialize default validation functions"""
        self.custom_validators.update({
            "email": self._validate_email,
            "url": self._validate_url,
            "phone": self._validate_phone,
            "json": self._validate_json,
            "safe_string": self._validate_safe_string,
            "positive_number": self._validate_positive_number,
            "non_empty_string": self._validate_non_empty_string
        })
    
    def validate(self, data: Any, rules: List[ValidationRule], constraints: Optional[ValidationConstraints] = None) -> ValidationReport:
        """Validate data following L5 architecture principles"""
        validation_constraints = constraints or self.constraints
        validation_id = self._generate_validation_id()
        
        self.logger.info(f"Validating data with {len(rules)} rules")
        
        # L5 Input validation
        self._validate_input(data, rules)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(data):
            raise SecurityError("Data failed L5 safety validation")
        
        start_time = time.time()
        results = []
        blocked_content = []
        
        try:
            # Check input size
            if len(str(data)) > validation_constraints.max_input_size:
                return ValidationReport(
                    validation_id=validation_id,
                    input_data=data,
                    overall_status=ValidationStatus.BLOCKED,
                    results=[],
                    blocked_content=["Input too large"],
                    safety_validated=False,
                    validation_time=time.time() - start_time,
                    timestamp=self._get_timestamp()
                )
            
            # Apply validation rules
            for rule in rules:
                result = self._apply_validation_rule(data, rule, validation_constraints)
                results.append(result)
                
                # Collect blocked content
                if result.status == ValidationStatus.BLOCKED:
                    blocked_content.append(f"{rule.field_path}: {result.error_message}")
            
            # Determine overall status
            if any(r.status == ValidationStatus.BLOCKED for r in results):
                overall_status = ValidationStatus.BLOCKED
            elif any(r.status == ValidationStatus.INVALID for r in results):
                overall_status = ValidationStatus.INVALID
            elif any(r.status == ValidationStatus.ERROR for r in results):
                overall_status = ValidationStatus.ERROR
            else:
                overall_status = ValidationStatus.VALID
            
            # Create validation report
            report = ValidationReport(
                validation_id=validation_id,
                input_data=data,
                overall_status=overall_status,
                results=results,
                blocked_content=blocked_content,
                safety_validated=True,
                validation_time=time.time() - start_time,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"Validation completed: {overall_status.value}")
            return report
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return ValidationReport(
                validation_id=validation_id,
                input_data=data,
                overall_status=ValidationStatus.ERROR,
                results=[],
                blocked_content=blocked_content,
                safety_validated=False,
                validation_time=time.time() - start_time,
                timestamp=self._get_timestamp()
            )
    
    def _apply_validation_rule(self, data: Any, rule: ValidationRule, constraints: ValidationConstraints) -> ValidationResult:
        """Apply a single validation rule"""
        try:
            # Extract field value using field path
            field_value = self._extract_field_value(data, rule.field_path)
            
            # Apply validation based on type
            if rule.validation_type == ValidationType.SCHEMA:
                return self._validate_schema(field_value, rule)
            elif rule.validation_type == ValidationType.TYPE:
                return self._validate_type(field_value, rule)
            elif rule.validation_type == ValidationType.RANGE:
                return self._validate_range(field_value, rule)
            elif rule.validation_type == ValidationType.PATTERN:
                return self._validate_pattern(field_value, rule)
            elif rule.validation_type == ValidationType.CUSTOM:
                return self._validate_custom(field_value, rule)
            elif rule.validation_type == ValidationType.SAFETY:
                return self._validate_safety_rule(field_value, rule)
            else:
                return ValidationResult(
                    rule_id=rule.rule_id,
                    field_path=rule.field_path,
                    status=ValidationStatus.ERROR,
                    error_message=f"Unknown validation type: {rule.validation_type}",
                    actual_value=field_value,
                    timestamp=self._get_timestamp()
                )
                
        except Exception as e:
            return ValidationResult(
                rule_id=rule.rule_id,
                field_path=rule.field_path,
                status=ValidationStatus.ERROR,
                error_message=f"Validation error: {str(e)}",
                timestamp=self._get_timestamp()
            )
    
    def _extract_field_value(self, data: Any, field_path: str) -> Any:
        """Extract field value using JSONPath-like syntax"""
        if not field_path or field_path == "$":
            return data
        
        # Simple path extraction (can be enhanced with full JSONPath support)
        parts = field_path.split('.')
        current = data
        
        for part in parts:
            if part.startswith('[') and part.endswith(']'):
                # Array access
                index = int(part[1:-1])
                if isinstance(current, list) and 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                # Object property access
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return None
        
        return current
    
    def _validate_schema(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate against schema"""
        schema = rule.parameters.get("schema", {})
        
        # Basic schema validation
        if "type" in schema:
            expected_type = schema["type"]
            if expected_type == "string" and not isinstance(value, str):
                return ValidationResult(
                    rule_id=rule.rule_id,
                    field_path=rule.field_path,
                    status=ValidationStatus.INVALID,
                    error_message=f"Expected string, got {type(value).__name__}",
                    actual_value=value,
                    expected_value=expected_type,
                    timestamp=self._get_timestamp()
                )
            elif expected_type == "number" and not isinstance(value, (int, float)):
                return ValidationResult(
                    rule_id=rule.rule_id,
                    field_path=rule.field_path,
                    status=ValidationStatus.INVALID,
                    error_message=f"Expected number, got {type(value).__name__}",
                    actual_value=value,
                    expected_value=expected_type,
                    timestamp=self._get_timestamp()
                )
        
        # Length validation
        if "min_length" in schema and isinstance(value, str):
            if len(value) < schema["min_length"]:
                return ValidationResult(
                    rule_id=rule.rule_id,
                    field_path=rule.field_path,
                    status=ValidationStatus.INVALID,
                    error_message=f"String too short: {len(value)} < {schema['min_length']}",
                    actual_value=value,
                    timestamp=self._get_timestamp()
                )
        
        if "max_length" in schema and isinstance(value, str):
            if len(value) > schema["max_length"]:
                return ValidationResult(
                    rule_id=rule.rule_id,
                    field_path=rule.field_path,
                    status=ValidationStatus.INVALID,
                    error_message=f"String too long: {len(value)} > {schema['max_length']}",
                    actual_value=value,
                    timestamp=self._get_timestamp()
                )
        
        return ValidationResult(
            rule_id=rule.rule_id,
            field_path=rule.field_path,
            status=ValidationStatus.VALID,
            actual_value=value,
            timestamp=self._get_timestamp()
        )
    
    def _validate_type(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate type"""
        expected_type = rule.parameters.get("type", "string")
        
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_map.get(expected_type, str)
        
        if isinstance(value, expected_python_type):
            return ValidationResult(
                rule_id=rule.rule_id,
                field_path=rule.field_path,
                status=ValidationStatus.VALID,
                actual_value=value,
                timestamp=self._get_timestamp()
            )
        else:
            return ValidationResult(
                rule_id=rule.rule_id,
                field_path=rule.field_path,
                status=ValidationStatus.INVALID,
                error_message=f"Expected {expected_type}, got {type(value).__name__}",
                actual_value=value,
                expected_value=expected_type,
                timestamp=self._get_timestamp()
            )
    
    def _validate_range(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate range"""
        if not isinstance(value, (int, float)):
            return ValidationResult(
                rule_id=rule.rule_id,
                field_path=rule.field_path,
                status=ValidationStatus.INVALID,
                error_message="Range validation requires numeric value",
                actual_value=value,
                timestamp=self._get_timestamp()
            )
        
        min_val = rule.parameters.get("min")
        max_val = rule.parameters.get("max")
        
        if min_val is not None and value < min_val:
            return ValidationResult(
                rule_id=rule.rule_id,
                field_path=rule.field_path,
                status=ValidationStatus.INVALID,
                error_message=f"Value {value} below minimum {min_val}",
                actual_value=value,
                expected_value=f">= {min_val}",
                timestamp=self._get_timestamp()
            )
        
        if max_val is not None and value > max_val:
            return ValidationResult(
                rule_id=rule.rule_id,
                field_path=rule.field_path,
                status=ValidationStatus.INVALID,
                error_message=f"Value {value} above maximum {max_val}",
                actual_value=value,
                expected_value=f"<= {max_val}",
                timestamp=self._get_timestamp()
            )
        
        return ValidationResult(
            rule_id=rule.rule_id,
            field_path=rule.field_path,
            status=ValidationStatus.VALID,
            actual_value=value,
            timestamp=self._get_timestamp()
        )
    
    def _validate_pattern(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate pattern"""
        if not isinstance(value, str):
            return ValidationResult(
                rule_id=rule.rule_id,
                field_path=rule.field_path,
                status=ValidationStatus.INVALID,
                error_message="Pattern validation requires string value",
                actual_value=value,
                timestamp=self._get_timestamp()
            )
        
        pattern = rule.parameters.get("pattern", "")
        
        try:
            if re.match(pattern, value):
                return ValidationResult(
                    rule_id=rule.rule_id,
                    field_path=rule.field_path,
                    status=ValidationStatus.VALID,
                    actual_value=value,
                    timestamp=self._get_timestamp()
                )
            else:
                return ValidationResult(
                    rule_id=rule.rule_id,
                    field_path=rule.field_path,
                    status=ValidationStatus.INVALID,
                    error_message=f"Value '{value}' does not match pattern '{pattern}'",
                    actual_value=value,
                    expected_value=pattern,
                    timestamp=self._get_timestamp()
                )
        except re.error as e:
            return ValidationResult(
                rule_id=rule.rule_id,
                field_path=rule.field_path,
                status=ValidationStatus.ERROR,
                error_message=f"Invalid regex pattern: {str(e)}",
                actual_value=value,
                timestamp=self._get_timestamp()
            )
    
    def _validate_custom(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate using custom validator"""
        validator_name = rule.parameters.get("validator", "")
        
        if validator_name not in self.custom_validators:
            return ValidationResult(
                rule_id=rule.rule_id,
                field_path=rule.field_path,
                status=ValidationStatus.ERROR,
                error_message=f"Unknown custom validator: {validator_name}",
                actual_value=value,
                timestamp=self._get_timestamp()
            )
        
        try:
            validator = self.custom_validators[validator_name]
            is_valid = validator(value, rule.parameters)
            
            if is_valid:
                return ValidationResult(
                    rule_id=rule.rule_id,
                    field_path=rule.field_path,
                    status=ValidationStatus.VALID,
                    actual_value=value,
                    timestamp=self._get_timestamp()
                )
            else:
                return ValidationResult(
                    rule_id=rule.rule_id,
                    field_path=rule.field_path,
                    status=ValidationStatus.INVALID,
                    error_message=f"Custom validation failed: {validator_name}",
                    actual_value=value,
                    timestamp=self._get_timestamp()
                )
        except Exception as e:
            return ValidationResult(
                rule_id=rule.rule_id,
                field_path=rule.field_path,
                status=ValidationStatus.ERROR,
                error_message=f"Custom validator error: {str(e)}",
                actual_value=value,
                timestamp=self._get_timestamp()
            )
    
    def _validate_safety_rule(self, value: Any, rule: ValidationRule) -> ValidationResult:
        """Validate safety rules"""
        if isinstance(value, str):
            # Check for dangerous patterns
            dangerous_patterns = [
                "<script>", "javascript:", "eval(", "exec(", "__import__",
                "drop table", "delete from", "insert into", "update set"
            ]
            
            value_lower = value.lower()
            for pattern in dangerous_patterns:
                if pattern in value_lower:
                    return ValidationResult(
                        rule_id=rule.rule_id,
                        field_path=rule.field_path,
                        status=ValidationStatus.BLOCKED,
                        error_message=f"Dangerous pattern detected: {pattern}",
                        actual_value=value,
                        timestamp=self._get_timestamp()
                    )
        
        return ValidationResult(
            rule_id=rule.rule_id,
            field_path=rule.field_path,
            status=ValidationStatus.VALID,
            actual_value=value,
            timestamp=self._get_timestamp()
        )
    
    # Custom validator implementations
    def _validate_email(self, value: Any, params: Dict[str, Any]) -> bool:
        """Validate email format"""
        if not isinstance(value, str):
            return False
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, value) is not None
    
    def _validate_url(self, value: Any, params: Dict[str, Any]) -> bool:
        """Validate URL format"""
        if not isinstance(value, str):
            return False
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(url_pattern, value) is not None
    
    def _validate_phone(self, value: Any, params: Dict[str, Any]) -> bool:
        """Validate phone number format"""
        if not isinstance(value, str):
            return False
        phone_pattern = r'^\+?1?-?\.?\s?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
        return re.match(phone_pattern, value) is not None
    
    def _validate_json(self, value: Any, params: Dict[str, Any]) -> bool:
        """Validate JSON format"""
        if not isinstance(value, str):
            return False
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False
    
    def _validate_safe_string(self, value: Any, params: Dict[str, Any]) -> bool:
        """Validate string is safe (no dangerous content)"""
        if not isinstance(value, str):
            return False
        dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
        value_lower = value.lower()
        return not any(pattern in value_lower for pattern in dangerous_patterns)
    
    def _validate_positive_number(self, value: Any, params: Dict[str, Any]) -> bool:
        """Validate positive number"""
        return isinstance(value, (int, float)) and value > 0
    
    def _validate_non_empty_string(self, value: Any, params: Dict[str, Any]) -> bool:
        """Validate non-empty string"""
        return isinstance(value, str) and len(value.strip()) > 0
    
    def validate_safety(self, data: Any) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check data size
            if len(str(data)) > self.constraints.max_input_size:
                self.logger.error("Data exceeds maximum size")
                return False
            
            # Check for dangerous patterns in strings
            if isinstance(data, str):
                dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
                data_lower = data.lower()
                for pattern in dangerous_patterns:
                    if pattern in data_lower:
                        self.logger.error(f"Dangerous pattern detected: {pattern}")
                        return False
            
            # Recursively check dictionaries and lists
            elif isinstance(data, dict):
                for key, value in data.items():
                    if not self.validate_safety(key) or not self.validate_safety(value):
                        return False
            
            elif isinstance(data, list):
                for item in data:
                    if not self.validate_safety(item):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, data: Any, rules: List[ValidationRule]) -> None:
        """L5 Input validation"""
        if not isinstance(rules, list):
            raise ValueError("Rules must be a list")
        
        if not rules:
            raise ValueError("Rules cannot be empty")
        
        for rule in rules:
            if not isinstance(rule, ValidationRule):
                raise ValueError("Each rule must be a ValidationRule object")
    
    def _generate_validation_id(self) -> str:
        """Generate unique validation ID"""
        import uuid
        return f"validation_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class ValidationEngineInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, engine: ValidationEngine):
        self._engine = engine
    
    def validate_data(self, data: Any, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            # Convert rule dictionaries to ValidationRule objects
            validation_rules = []
            for rule_dict in rules:
                validation_rules.append(ValidationRule(
                    rule_id=rule_dict.get("rule_id", ""),
                    validation_type=ValidationType(rule_dict.get("validation_type", "type")),
                    field_path=rule_dict.get("field_path", "$"),
                    parameters=rule_dict.get("parameters", {}),
                    error_message=rule_dict.get("error_message", ""),
                    required=rule_dict.get("required", True)
                ))
            
            constraints = ValidationConstraints()
            report = self._engine.validate(data, validation_rules, constraints)
            
            return {
                "success": report.overall_status == ValidationStatus.VALID,
                "validation_id": report.validation_id,
                "overall_status": report.overall_status.value,
                "result_count": len(report.results),
                "results": [
                    {
                        "rule_id": result.rule_id,
                        "field_path": result.field_path,
                        "status": result.status.value,
                        "error_message": result.error_message,
                        "actual_value": str(result.actual_value) if result.actual_value is not None else None,
                        "expected_value": str(result.expected_value) if result.expected_value is not None else None
                    }
                    for result in report.results
                ],
                "blocked_content": report.blocked_content,
                "safety_validated": report.safety_validated,
                "validation_time": report.validation_time,
                "timestamp": report.timestamp
            }
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class ValidationEngineFactory:
    """L5 Factory for creating validation engine instances"""
    
    @staticmethod
    def create_engine(constraints: Optional[ValidationConstraints] = None) -> ValidationEngine:
        return ValidationEngineImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[ValidationConstraints] = None) -> ValidationEngineInterface:
        engine = ValidationEngineFactory.create_engine(constraints)
        return ValidationEngineInterface(engine)

# L5 Export for module usage
__all__ = [
    "ValidationType",
    "ValidationStatus",
    "ValidationConstraints",
    "ValidationRule",
    "ValidationResult",
    "ValidationReport",
    "ValidationEngine",
    "ValidationEngineImpl",
    "ValidationEngineInterface",
    "ValidationEngineFactory",
    "SecurityError"
]
