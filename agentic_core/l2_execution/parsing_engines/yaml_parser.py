"""
L5 Agentic Core - L2 Execution Layer - YAML Parser
Implements L2 Pure Execution Layer for safe YAML parsing operations
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import re

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParseMode(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    PARSE = "parse"
    VALIDATE = "validate"
    EXTRACT_KEYS = "extract_keys"
    SCHEMA_INFERENCE = "schema_inference"
    TRANSFORM = "transform"
    MERGE = "merge"

class ParseStatus(Enum):
    """L5 Parse status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    INVALID_YAML = "invalid_yaml"
    TOO_DEEP = "too_deep"
    TOO_LARGE = "too_large"
    SAFETY_VIOLATION = "safety_violation"

@dataclass
class ParseConstraints:
    """L5 Safety constraints - fail-closed behavior"""
    max_input_size: int = 100000  # 100KB
    max_depth: int = 10
    max_keys: int = 1000
    max_string_length: int = 10000
    allowed_types: List[str] = field(default_factory=lambda: ["object", "array", "string", "number", "boolean", "null"])
    block_dangerous_content: bool = True
    safety_level: str = "strict"

@dataclass
class YAMLKey:
    """L5 YAML key structure with full type safety"""
    key_path: str
    value: Any
    data_type: str
    line_number: int = 0
    safety_validated: bool = False

@dataclass
class ParseResult:
    """L5 Parse result structure"""
    parse_mode: ParseMode
    original_data: str = ""
    parsed_data: Any = None
    keys: List[YAMLKey] = field(default_factory=list)
    schema: Dict[str, Any] = field(default_factory=dict)
    transformed_data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    safety_validated: bool = False
    timestamp: str = ""

@dataclass
class ParseResponse:
    """L5 Parse response structure"""
    parse_id: str
    status: ParseStatus
    result: Optional[ParseResult] = None
    error_message: str = ""
    safety_validated: bool = False
    timestamp: str = ""

class YAMLParser(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def parse(self, yaml_data: str, mode: ParseMode, constraints: ParseConstraints) -> ParseResponse:
        """Parse YAML with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, yaml_data: str) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class YAMLParserImpl(YAMLParser):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure YAML parsing execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[ParseConstraints] = None):
        self.constraints = constraints or ParseConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def parse(self, yaml_data: str, mode: ParseMode, constraints: Optional[ParseConstraints] = None) -> ParseResponse:
        """Parse YAML following L5 architecture principles"""
        parse_constraints = constraints or self.constraints
        parse_id = self._generate_parse_id()
        
        self.logger.info(f"Parsing YAML with mode: {mode.value}")
        
        # L5 Input validation
        self._validate_input(yaml_data, mode)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(yaml_data):
            raise SecurityError("YAML data failed L5 safety validation")
        
        try:
            # Check input size
            if len(yaml_data) > parse_constraints.max_input_size:
                return ParseResponse(
                    parse_id=parse_id,
                    status=ParseStatus.TOO_LARGE,
                    error_message=f"YAML data too large: {len(yaml_data)} > {parse_constraints.max_input_size}",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            # Parse based on mode
            if mode == ParseMode.PARSE:
                result = self._parse_yaml(yaml_data, parse_constraints)
            elif mode == ParseMode.VALIDATE:
                result = self._validate_yaml(yaml_data, parse_constraints)
            elif mode == ParseMode.EXTRACT_KEYS:
                result = self._extract_keys(yaml_data, parse_constraints)
            elif mode == ParseMode.SCHEMA_INFERENCE:
                result = self._infer_schema(yaml_data, parse_constraints)
            elif mode == ParseMode.TRANSFORM:
                result = self._transform_yaml(yaml_data, parse_constraints)
            elif mode == ParseMode.MERGE:
                result = self._merge_yaml(yaml_data, parse_constraints)
            else:
                raise ValueError(f"Unsupported parse mode: {mode}")
            
            # Create parse response
            response = ParseResponse(
                parse_id=parse_id,
                status=ParseStatus.SUCCESS,
                result=result,
                safety_validated=True,
                timestamp=self._get_timestamp()
            )
            
            self.logger.info(f"YAML parsing completed: {mode.value}")
            return response
            
        except Exception as e:
            self.logger.error(f"YAML parsing error: {e}")
            return ParseResponse(
                parse_id=parse_id,
                status=ParseStatus.FAILED,
                error_message=str(e),
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
    
    def _parse_yaml(self, yaml_data: str, constraints: ParseConstraints) -> ParseResult:
        """Parse YAML into Python object"""
        parsed_data = self._safe_yaml_load(yaml_data)
        
        # Validate parsed data safety
        self._validate_data_safety(parsed_data, constraints)
        
        return ParseResult(
            parse_mode=ParseMode.PARSE,
            original_data=yaml_data,
            parsed_data=parsed_data,
            metadata={
                "data_type": type(parsed_data).__name__,
                "size": len(yaml_data),
                "keys_count": self._count_keys(parsed_data) if isinstance(parsed_data, dict) else 0
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _validate_yaml(self, yaml_data: str, constraints: ParseConstraints) -> ParseResult:
        """Validate YAML structure and content"""
        parsed_data = self._safe_yaml_load(yaml_data)
        
        # Perform comprehensive validation
        validation_errors = []
        
        # Check depth
        depth = self._calculate_depth(parsed_data)
        if depth > constraints.max_depth:
            validation_errors.append(f"YAML too deep: {depth} > {constraints.max_depth}")
        
        # Check key count
        key_count = self._count_keys(parsed_data)
        if key_count > constraints.max_keys:
            validation_errors.append(f"Too many keys: {key_count} > {constraints.max_keys}")
        
        # Check string lengths
        max_string_len = self._find_max_string_length(parsed_data)
        if max_string_len > constraints.max_string_length:
            validation_errors.append(f"String too long: {max_string_len} > {constraints.max_string_length}")
        
        # Check for dangerous content
        if constraints.block_dangerous_content:
            dangerous_content = self._find_dangerous_content(parsed_data)
            if dangerous_content:
                validation_errors.append(f"Dangerous content found: {dangerous_content}")
        
        # Validate YAML syntax
        syntax_errors = self._validate_yaml_syntax(yaml_data)
        validation_errors.extend(syntax_errors)
        
        return ParseResult(
            parse_mode=ParseMode.VALIDATE,
            original_data=yaml_data,
            parsed_data=parsed_data,
            metadata={
                "validation_errors": validation_errors,
                "depth": depth,
                "key_count": key_count,
                "max_string_length": max_string_len,
                "is_valid": len(validation_errors) == 0
            },
            safety_validated=len(validation_errors) == 0,
            timestamp=self._get_timestamp()
        )
    
    def _extract_keys(self, yaml_data: str, constraints: ParseConstraints) -> ParseResult:
        """Extract all YAML keys with line numbers"""
        parsed_data = self._safe_yaml_load(yaml_data)
        keys = []
        
        def extract_keys_recursive(obj, current_path="", line_number=1):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{current_path}.{key}" if current_path else key
                    
                    # Find line number for this key
                    key_line = self._find_key_line(yaml_data, key)
                    
                    # Validate key safety
                    if self._validate_key_safety(key, constraints):
                        key_obj = YAMLKey(
                            key_path=new_path,
                            value=value,
                            data_type=type(value).__name__,
                            line_number=key_line,
                            safety_validated=True
                        )
                        keys.append(key_obj)
                    
                    # Recurse for nested objects
                    if isinstance(value, (dict, list)):
                        extract_keys_recursive(value, new_path, key_line)
            
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    new_path = f"{current_path}[{i}]"
                    
                    # Validate key safety (for list indices)
                    if self._validate_key_safety(str(i), constraints):
                        key_obj = YAMLKey(
                            key_path=new_path,
                            value=value,
                            data_type=type(value).__name__,
                            line_number=line_number,
                            safety_validated=True
                        )
                        keys.append(key_obj)
                    
                    # Recurse for nested objects
                    if isinstance(value, (dict, list)):
                        extract_keys_recursive(value, new_path, line_number)
        
        extract_keys_recursive(parsed_data)
        
        return ParseResult(
            parse_mode=ParseMode.EXTRACT_KEYS,
            original_data=yaml_data,
            parsed_data=parsed_data,
            keys=keys,
            metadata={
                "key_count": len(keys),
                "unique_types": list(set(k.data_type for k in keys))
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _infer_schema(self, yaml_data: str, constraints: ParseConstraints) -> ParseResult:
        """Infer YAML schema from data"""
        parsed_data = self._safe_yaml_load(yaml_data)
        schema = self._infer_schema_recursive(parsed_data)
        
        return ParseResult(
            parse_mode=ParseMode.SCHEMA_INFERENCE,
            original_data=yaml_data,
            parsed_data=parsed_data,
            schema=schema,
            metadata={
                "schema_type": schema.get("type", "unknown"),
                "inferred_properties": len(schema.get("properties", {})) if schema.get("type") == "object" else 0
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _transform_yaml(self, yaml_data: str, constraints: ParseConstraints) -> ParseResult:
        """Transform YAML (basic transformations)"""
        parsed_data = self._safe_yaml_load(yaml_data)
        
        # Basic transformations
        transformed = {
            "original": parsed_data,
            "normalized": self._normalize_data(parsed_data),
            "keys_sorted": self._sort_keys(parsed_data)
        }
        
        return ParseResult(
            parse_mode=ParseMode.TRANSFORM,
            original_data=yaml_data,
            parsed_data=parsed_data,
            transformed_data=transformed,
            metadata={
                "transformations": ["original", "normalized", "keys_sorted"]
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _merge_yaml(self, yaml_data: str, constraints: ParseConstraints) -> ParseResult:
        """Merge YAML with default values (placeholder implementation)"""
        parsed_data = self._safe_yaml_load(yaml_data)
        
        # Simple merge with default structure
        default_structure = {
            "version": "1.0",
            "metadata": {},
            "config": {}
        }
        
        merged = self._deep_merge(default_structure, parsed_data)
        
        return ParseResult(
            parse_mode=ParseMode.MERGE,
            original_data=yaml_data,
            parsed_data=parsed_data,
            transformed_data=merged,
            metadata={
                "merge_strategy": "deep_merge",
                "default_keys": list(default_structure.keys())
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _safe_yaml_load(self, yaml_data: str) -> Any:
        """Safely load YAML with basic parsing"""
        # Simple YAML parser implementation (for safety)
        # In production, use PyYAML with safe loading
        lines = yaml_data.split('\n')
        result = {}
        current_context = [result]
        indent_stack = [0]
        
        for line_num, line in enumerate(lines, 1):
            line = line.rstrip()
            if not line or line.strip().startswith('#'):
                continue
            
            # Calculate indentation
            indent = len(line) - len(line.lstrip())
            
            # Find the right context level
            while len(indent_stack) > 1 and indent <= indent_stack[-1]:
                current_context.pop()
                indent_stack.pop()
            
            stripped = line.strip()
            
            # Parse key-value pairs
            if ':' in stripped:
                key, value = stripped.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Parse value
                parsed_value = self._parse_yaml_value(value)
                
                # Add to current context
                current_context[-1][key] = parsed_value
                
                # If value is empty, prepare for nested structure
                if not value:
                    current_context[-1][key] = {}
                    current_context.append(current_context[-1][key])
                    indent_stack.append(indent + 2)
        
        return result
    
    def _parse_yaml_value(self, value: str) -> Any:
        """Parse individual YAML value"""
        if not value:
            return {}
        
        # Boolean values
        if value.lower() in ['true', 'yes', 'on']:
            return True
        elif value.lower() in ['false', 'no', 'off']:
            return False
        
        # Null values
        elif value.lower() in ['null', 'none', '~']:
            return None
        
        # Numbers
        elif value.isdigit():
            return int(value)
        elif re.match(r'^-?\d+$', value):
            return int(value)
        elif re.match(r'^-?\d+\.\d+$', value):
            return float(value)
        
        # Strings (remove quotes if present)
        elif (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        else:
            return value
    
    def _infer_schema_recursive(self, obj) -> Dict[str, Any]:
        """Recursively infer schema from object"""
        if isinstance(obj, dict):
            properties = {}
            for key, value in obj.items():
                properties[key] = self._infer_schema_recursive(value)
            
            return {
                "type": "object",
                "properties": properties,
                "required": list(obj.keys())
            }
        
        elif isinstance(obj, list):
            if not obj:
                return {"type": "array", "items": {}}
            
            # Infer schema from first few items
            item_schemas = [self._infer_schema_recursive(item) for item in obj[:5]]
            
            if item_schemas:
                merged_schema = item_schemas[0]
                return {"type": "array", "items": merged_schema}
            else:
                return {"type": "array", "items": {}}
        
        elif isinstance(obj, str):
            return {"type": "string"}
        
        elif isinstance(obj, bool):
            return {"type": "boolean"}
        
        elif isinstance(obj, int):
            return {"type": "integer"}
        
        elif isinstance(obj, float):
            return {"type": "number"}
        
        elif obj is None:
            return {"type": "null"}
        
        else:
            return {"type": "unknown"}
    
    def _normalize_data(self, obj) -> Any:
        """Normalize data (basic normalization)"""
        if isinstance(obj, dict):
            return {k.lower(): self._normalize_data(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._normalize_data(item) for item in obj]
        elif isinstance(obj, str):
            return obj.strip().lower()
        else:
            return obj
    
    def _sort_keys(self, obj) -> Any:
        """Sort dictionary keys"""
        if isinstance(obj, dict):
            return {k: self._sort_keys(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [self._sort_keys(item) for item in obj]
        else:
            return obj
    
    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _find_key_line(self, yaml_data: str, key: str) -> int:
        """Find line number for a key in YAML"""
        lines = yaml_data.split('\n')
        for i, line in enumerate(lines, 1):
            if line.strip().startswith(f"{key}:"):
                return i
        return 0
    
    def _validate_yaml_syntax(self, yaml_data: str) -> List[str]:
        """Validate YAML syntax"""
        errors = []
        lines = yaml_data.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.rstrip()
            if not line or line.strip().startswith('#'):
                continue
            
            # Check for unescaped special characters
            if ':' in line and not line.strip().startswith('#'):
                key_part = line.split(':', 1)[0]
                if any(char in key_part for char in ['{', '}', '[', ']', ',', '#', '&', '*', '!', '|', '>', '\'', '"', '%', '@', '`']):
                    errors.append(f"Line {line_num}: Unescaped special character in key")
            
            # Check indentation consistency
            if line.startswith('\t'):
                errors.append(f"Line {line_num}: Tabs not allowed for indentation")
        
        return errors
    
    def _calculate_depth(self, obj, current_depth=0) -> int:
        """Calculate maximum depth of YAML structure"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
    
    def _count_keys(self, obj) -> int:
        """Count total keys in YAML structure"""
        if isinstance(obj, dict):
            return len(obj) + sum(self._count_keys(v) for v in obj.values())
        elif isinstance(obj, list):
            return sum(self._count_keys(item) for item in obj)
        else:
            return 0
    
    def _find_max_string_length(self, obj) -> int:
        """Find maximum string length in YAML"""
        if isinstance(obj, str):
            return len(obj)
        elif isinstance(obj, dict):
            return max(self._find_max_string_length(v) for v in obj.values()) if obj else 0
        elif isinstance(obj, list):
            return max(self._find_max_string_length(item) for item in obj) if obj else 0
        else:
            return 0
    
    def _find_dangerous_content(self, obj) -> List[str]:
        """Find dangerous content in YAML"""
        dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
        dangerous_content = []
        
        def check_content(value, path=""):
            if isinstance(value, str):
                value_lower = value.lower()
                for pattern in dangerous_patterns:
                    if pattern in value_lower:
                        dangerous_content.append(f"{path}: {pattern}")
            elif isinstance(value, dict):
                for k, v in value.items():
                    check_content(v, f"{path}.{k}" if path else k)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    check_content(item, f"{path}[{i}]")
        
        check_content(obj)
        return dangerous_content
    
    def _validate_data_safety(self, obj, constraints: ParseConstraints) -> None:
        """Validate parsed data safety"""
        # Check depth
        depth = self._calculate_depth(obj)
        if depth > constraints.max_depth:
            raise ValueError(f"YAML too deep: {depth} > {constraints.max_depth}")
        
        # Check key count
        key_count = self._count_keys(obj)
        if key_count > constraints.max_keys:
            raise ValueError(f"Too many keys: {key_count} > {constraints.max_keys}")
        
        # Check for dangerous content
        if constraints.block_dangerous_content:
            dangerous_content = self._find_dangerous_content(obj)
            if dangerous_content:
                raise ValueError(f"Dangerous content found: {dangerous_content}")
    
    def _validate_key_safety(self, key: str, constraints: ParseConstraints) -> bool:
        """Validate individual key safety"""
        # Check key length
        if len(key) > 100:
            return False
        
        # Check for suspicious characters
        if any(char in key for char in ['\0', '\r', '\n', '\t']):
            return False
        
        return True
    
    def validate_safety(self, yaml_data: str) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check data size
            if len(yaml_data) > self.constraints.max_input_size:
                self.logger.error("YAML data exceeds maximum size")
                return False
            
            # Check for dangerous patterns
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
            data_lower = yaml_data.lower()
            for pattern in dangerous_patterns:
                if pattern in data_lower:
                    self.logger.error(f"Dangerous pattern detected: {pattern}")
                    return False
            
            # Check for suspicious content
            if yaml_data.count('\0') > 0:  # Null bytes
                self.logger.error("Null bytes detected in YAML")
                return False
            
            # Try to parse YAML to ensure it's valid
            self._safe_yaml_load(yaml_data)
            
            self.logger.info("YAML data passed L5 safety validation")
            return True
            
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, yaml_data: str, mode: ParseMode) -> None:
        """L5 Input validation"""
        if not isinstance(yaml_data, str):
            raise ValueError("YAML data must be a string")
        
        if not isinstance(mode, ParseMode):
            raise ValueError("Mode must be a ParseMode enum")
        
        if not yaml_data.strip():
            raise ValueError("YAML data cannot be empty")
    
    def _generate_parse_id(self) -> str:
        """Generate unique parse ID"""
        import uuid
        return f"yaml_parse_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class YAMLParserInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, parser: YAMLParser):
        self._parser = parser
    
    def parse_yaml(self, yaml_data: str, mode: str = "parse", max_size: int = 100000) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            parse_mode = ParseMode(mode)
            constraints = ParseConstraints(max_input_size=max_size)
            
            response = self._parser.parse(yaml_data, parse_mode, constraints)
            
            if response.result:
                return {
                    "success": response.status == ParseStatus.SUCCESS,
                    "parse_id": response.parse_id,
                    "parse_mode": response.result.parse_mode.value,
                    "parsed_data": response.result.parsed_data,
                    "keys": [
                        {
                            "key_path": key.key_path,
                            "value": str(key.value),
                            "data_type": key.data_type,
                            "line_number": key.line_number,
                            "safety_validated": key.safety_validated
                        }
                        for key in response.result.keys
                    ],
                    "schema": response.result.schema,
                    "transformed_data": response.result.transformed_data,
                    "metadata": response.result.metadata,
                    "safety_validated": response.result.safety_validated,
                    "timestamp": response.result.timestamp
                }
            else:
                return {
                    "success": False,
                    "error": response.error_message,
                    "status": response.status.value,
                    "safety_validated": response.safety_validated
                }
        except Exception as e:
            self.logger.error(f"YAML parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class YAMLParserFactory:
    """L5 Factory for creating YAML parser instances"""
    
    @staticmethod
    def create_parser(constraints: Optional[ParseConstraints] = None) -> YAMLParser:
        return YAMLParserImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[ParseConstraints] = None) -> YAMLParserInterface:
        parser = YAMLParserFactory.create_parser(constraints)
        return YAMLParserInterface(parser)

# L5 Export for module usage
__all__ = [
    "ParseMode",
    "ParseStatus",
    "ParseConstraints",
    "YAMLKey",
    "ParseResult",
    "ParseResponse",
    "YAMLParser",
    "YAMLParserImpl",
    "YAMLParserInterface",
    "YAMLParserFactory",
    "SecurityError"
]
