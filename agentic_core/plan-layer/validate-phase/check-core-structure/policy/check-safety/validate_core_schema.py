"""
L5 Agentic Core - Validate Phase - Validate Core Schema
Implements L5 Safety Layer for core schema validation with fail-closed behavior
"""

from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import re
import json
from abc import ABC, abstractmethod

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """L5 Validation severity levels for deterministic safety behavior"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class SchemaType(Enum):
    """L5 Schema types for validation routing"""
    CORE_QUERY = "core_query"
    LAYER_PARAMETER = "layer_parameter"
    SAFETY_CONSTRAINT = "safety_constraint"
    EXECUTION_CONTEXT = "execution_context"

@dataclass
class ValidationRule:
    """L5 Validation rule with fail-closed behavior"""
    name: str
    pattern: str
    severity: ValidationSeverity
    required: bool = True
    description: str = ""

@dataclass
class ValidationResult:
    """L5 Validation result with full context"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    schema_type: Optional[SchemaType] = None
    validation_timestamp: str = ""
    safety_level: str = "strict"

@dataclass
class CoreSchema:
    """L5 Core schema structure with type safety"""
    schema_type: SchemaType
    structure: Dict[str, Any]
    constraints: Dict[str, Any] = field(default_factory=dict)
    required_fields: Set[str] = field(default_factory=set)
    optional_fields: Set[str] = field(default_factory=set)

class SchemaValidator(ABC):
    """L5 Abstract base for schema validators - ensures L5 safety compliance"""
    
    @abstractmethod
    def validate(self, schema: CoreSchema, data: Dict[str, Any]) -> ValidationResult:
        """Validate data against schema with L5 safety constraints"""
        pass
    
    @abstractmethod
    def check_safety(self, data: Dict[str, Any]) -> bool:
        """L5 Safety check - fail-closed by default"""
        pass

class CoreSchemaValidator(SchemaValidator):
    """
    L5 Core Schema Validator - Implements L5 Safety Layer
    Fail-closed validation with comprehensive security checks
    """
    
    def __init__(self, safety_level: str = "strict"):
        self.safety_level = safety_level
        self.logger = logging.getLogger(self.__class__.__name__)
        self._validation_rules = self._initialize_validation_rules()
    
    def validate(self, schema: CoreSchema, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate data against core schema with L5 safety principles
        
        Args:
            schema: Core schema definition
            data: Data to validate
            
        Returns:
            ValidationResult: L5 structured validation result
            
        Raises:
            SecurityError: If validation fails critical safety checks
        """
        self.logger.info(f"Validating {schema.schema_type.value} schema against data")
        
        result = ValidationResult(
            schema_type=schema.schema_type,
            validation_timestamp=self._get_timestamp(),
            safety_level=self.safety_level
        )
        
        # L5 Pre-validation safety check
        if not self.check_safety(data):
            raise SecurityError("Data failed L5 pre-validation safety check")
        
        # Validate required fields
        self._validate_required_fields(schema, data, result)
        
        # Validate field types
        self._validate_field_types(schema, data, result)
        
        # Validate constraints
        self._validate_constraints(schema, data, result)
        
        # Apply validation rules
        self._apply_validation_rules(data, result)
        
        # L5 Post-validation safety check
        if result.errors and self.safety_level == "strict":
            raise SecurityError(f"Schema validation failed with {len(result.errors)} errors")
        
        result.is_valid = len(result.errors) == 0
        self.logger.info(f"Schema validation completed: {'PASSED' if result.is_valid else 'FAILED'}")
        
        return result
    
    def check_safety(self, data: Dict[str, Any]) -> bool:
        """
        L5 Safety check with fail-closed behavior
        
        Args:
            data: Data to check for safety
            
        Returns:
            bool: True if safe, False otherwise (fail-closed)
        """
        try:
            # Check for injection patterns
            if self._contains_dangerous_patterns(data):
                self.logger.error("Data contains dangerous patterns")
                return False
            
            # Check data size limits
            if self._exceeds_size_limits(data):
                self.logger.error("Data exceeds size limits")
                return False
            
            # Check for recursive structures
            if self._has_recursion(data):
                self.logger.error("Data contains dangerous recursion")
                return False
            
            self.logger.info("Data passed L5 safety check")
            return True
            
        except Exception as e:
            self.logger.error(f"Safety check error: {e}")
            return False  # Fail-closed behavior
    
    def _validate_required_fields(self, schema: CoreSchema, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate required fields are present"""
        for field in schema.required_fields:
            if field not in data:
                error_msg = f"Required field '{field}' is missing"
                result.errors.append(error_msg)
                self.logger.error(error_msg)
    
    def _validate_field_types(self, schema: CoreSchema, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate field types against schema"""
        for field, expected_type in schema.structure.items():
            if field in data:
                if not self._check_type(data[field], expected_type):
                    error_msg = f"Field '{field}' has incorrect type"
                    result.errors.append(error_msg)
                    self.logger.error(error_msg)
    
    def _validate_constraints(self, schema: CoreSchema, data: Dict[str, Any], result: ValidationResult) -> None:
        """Validate schema constraints"""
        for field, constraint in schema.constraints.items():
            if field in data:
                if not self._check_constraint(data[field], constraint):
                    error_msg = f"Field '{field}' violates constraint: {constraint}"
                    result.errors.append(error_msg)
                    self.logger.error(error_msg)
    
    def _apply_validation_rules(self, data: Dict[str, Any], result: ValidationResult) -> None:
        """Apply L5 validation rules"""
        data_str = json.dumps(data, default=str)
        
        for rule in self._validation_rules:
            if re.search(rule.pattern, data_str, re.IGNORECASE):
                if rule.severity == ValidationSeverity.ERROR:
                    result.errors.append(f"Validation rule violated: {rule.name}")
                elif rule.severity == ValidationSeverity.WARNING:
                    result.warnings.append(f"Validation warning: {rule.name}")
    
    def _check_type(self, value: Any, expected_type: Any) -> bool:
        """L5 Type checking with safety"""
        try:
            if isinstance(expected_type, str):
                type_map = {
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "dict": dict,
                    "list": list
                }
                expected_type = type_map.get(expected_type, str)
            
            return isinstance(value, expected_type)
        except Exception:
            return False  # Fail-closed
    
    def _check_constraint(self, value: Any, constraint: Dict[str, Any]) -> bool:
        """Check individual constraint"""
        try:
            if "min_length" in constraint:
                if len(str(value)) < constraint["min_length"]:
                    return False
            
            if "max_length" in constraint:
                if len(str(value)) > constraint["max_length"]:
                    return False
            
            if "pattern" in constraint:
                if not re.match(constraint["pattern"], str(value)):
                    return False
            
            return True
        except Exception:
            return False  # Fail-closed
    
    def _contains_dangerous_patterns(self, data: Dict[str, Any]) -> bool:
        """L5 Dangerous pattern detection"""
        dangerous_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"eval\s*\(",
            r"exec\s*\(",
            r"__import__",
            r"subprocess\.",
            r"os\.system",
            r"\.\./.*\.\.",
        ]
        
        data_str = json.dumps(data, default=str)
        for pattern in dangerous_patterns:
            if re.search(pattern, data_str, re.IGNORECASE):
                return True
        return False
    
    def _exceeds_size_limits(self, data: Dict[str, Any]) -> bool:
        """Check data size against L5 limits"""
        try:
            data_size = len(json.dumps(data, default=str))
            max_size = 1024 * 1024  # 1MB limit
            return data_size > max_size
        except Exception:
            return True  # Fail-closed
    
    def _has_recursion(self, data: Any, visited: Optional[Set[int]] = None) -> bool:
        """Check for dangerous recursion"""
        if visited is None:
            visited = set()
        
        try:
            obj_id = id(data)
            if obj_id in visited:
                return True
            
            visited.add(obj_id)
            
            if isinstance(data, dict):
                return any(self._has_recursion(v, visited.copy()) for v in data.values())
            elif isinstance(data, list):
                return any(self._has_recursion(item, visited.copy()) for item in data)
            
            return False
        except Exception:
            return True  # Fail-closed
    
    def _initialize_validation_rules(self) -> List[ValidationRule]:
        """Initialize L5 validation rules"""
        return [
            ValidationRule(
                name="no_sql_injection",
                pattern=r"(union|select|insert|update|delete|drop|create|alter)\s+",
                severity=ValidationSeverity.ERROR,
                description="Detect SQL injection patterns"
            ),
            ValidationRule(
                name="no_script_tags",
                pattern=r"<script[^>]*>",
                severity=ValidationSeverity.ERROR,
                description="Detect script tags"
            ),
            ValidationRule(
                name="no_eval_statements",
                pattern=r"eval\s*\(",
                severity=ValidationSeverity.ERROR,
                description="Detect eval statements"
            ),
            ValidationRule(
                name="suspicious_keywords",
                pattern=r"(password|secret|token|key)\s*[:=]",
                severity=ValidationSeverity.WARNING,
                description="Detect suspicious keywords"
            )
        ]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class CoreSchemaValidatorInterface:
    """L5 Interface for core schema validator - ensures contract compliance"""
    
    def __init__(self, validator: SchemaValidator):
        self._validator = validator
    
    def validate_schema(self, schema_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        L5 Interface method - validates schema safely
        
        Args:
            schema_type: String representation of schema type
            data: Data to validate
            
        Returns:
            Dict: Serializable validation result
            
        Raises:
            SecurityError: If validation fails critical safety checks
        """
        try:
            schema_enum = SchemaType(schema_type.lower())
            
            # Create default schema based on type
            schema = self._create_default_schema(schema_enum)
            
            result = self._validator.validate(schema, data)
            return {
                "is_valid": result.is_valid,
                "errors": result.errors,
                "warnings": result.warnings,
                "schema_type": result.schema_type.value if result.schema_type else None,
                "validation_timestamp": result.validation_timestamp,
                "safety_level": result.safety_level
            }
        except ValueError as e:
            raise SecurityError(f"Invalid schema type: {e}")
        except Exception as e:
            raise SecurityError(f"Schema validation failed: {e}")
    
    def _create_default_schema(self, schema_type: SchemaType) -> CoreSchema:
        """Create default schema based on type"""
        if schema_type == SchemaType.CORE_QUERY:
            return CoreSchema(
                schema_type=schema_type,
                structure={
                    "query_type": "str",
                    "parameters": "dict",
                    "constraints": "dict"
                },
                required_fields={"query_type", "parameters"},
                constraints={"max_depth": 5}
            )
        elif schema_type == SchemaType.LAYER_PARAMETER:
            return CoreSchema(
                schema_type=schema_type,
                structure={
                    "layer_name": "str",
                    "parameters": "dict"
                },
                required_fields={"layer_name", "parameters"}
            )
        else:
            # Generic schema for other types
            return CoreSchema(
                schema_type=schema_type,
                structure={"data": "dict"},
                required_fields={"data"}
            )

# L5 Factory for dependency injection
class CoreSchemaValidatorFactory:
    """L5 Factory for creating schema validators with proper configuration"""
    
    @staticmethod
    def create_validator(safety_level: str = "strict") -> CoreSchemaValidatorInterface:
        """Create configured schema validator"""
        validator = CoreSchemaValidator(safety_level)
        return CoreSchemaValidatorInterface(validator)

# L5 Main execution point
def validate_core_schema(schema_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    L5 Main function - validates core schema with full safety validation
    
    Args:
        schema_type: Type of schema to validate against
        data: Data to validate
        
    Returns:
        Dict: Validation result
        
    Raises:
        SecurityError: If validation fails any safety check
    """
    factory = CoreSchemaValidatorFactory()
    validator = factory.create_validator()
    return validator.validate_schema(schema_type, data)

if __name__ == "__main__":
    # L5 Test execution
    try:
        test_data = {
            "query_type": "core_registry",
            "parameters": {
                "registry_type": "core",
                "query_scope": "system"
            },
            "constraints": {"max_depth": 3}
        }
        result = validate_core_schema("core_query", test_data)
        logger.info(f"L5 Schema validation successful: {result}")
    except SecurityError as e:
        logger.error(f"L5 Security error: {e}")
    except Exception as e:
        logger.error(f"L5 Unexpected error: {e}")