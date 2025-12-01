"""
L5 Agentic Core - L2 Execution Layer - JSON Parser
Implements L2 Pure Execution Layer for safe JSON parsing operations
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from abc import ABC, abstractmethod
import json
import re

# Configure logging for L5 observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParseMode(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    PARSE = "parse"
    VALIDATE = "validate"
    EXTRACT_PATHS = "extract_paths"
    FLATTEN = "flatten"
    SCHEMA_INFERENCE = "schema_inference"
    TRANSFORM = "transform"

class ParseStatus(Enum):
    """L5 Parse status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    INVALID_JSON = "invalid_json"
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
class JSONPath:
    """L5 JSON path structure with full type safety"""
    path: str
    value: Any
    data_type: str
    path_type: str = "jsonpath"
    safety_validated: bool = False

@dataclass
class ParseResult:
    """L5 Parse result structure"""
    parse_mode: ParseMode
    original_data: str = ""
    parsed_data: Any = None
    paths: List[JSONPath] = field(default_factory=list)
    schema: Dict[str, Any] = field(default_factory=dict)
    flattened_data: Dict[str, Any] = field(default_factory=dict)
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

class JSONParser(ABC):
    """L5 Abstract base - ensures L2 pure execution behavior"""
    
    @abstractmethod
    def parse(self, json_data: str, mode: ParseMode, constraints: ParseConstraints) -> ParseResponse:
        """Parse JSON with L5 safety constraints"""
        pass
    
    @abstractmethod
    def validate_safety(self, json_data: str) -> bool:
        """L5 Safety validation - fail-closed by default"""
        pass

class JSONParserImpl(JSONParser):
    """
    L5 Implementation - L2 Pure Execution Layer
    Pure JSON parsing execution with comprehensive safety
    """
    
    def __init__(self, constraints: Optional[ParseConstraints] = None):
        self.constraints = constraints or ParseConstraints()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def parse(self, json_data: str, mode: ParseMode, constraints: Optional[ParseConstraints] = None) -> ParseResponse:
        """Parse JSON following L5 architecture principles"""
        parse_constraints = constraints or self.constraints
        parse_id = self._generate_parse_id()
        
        self.logger.info(f"Parsing JSON with mode: {mode.value}")
        
        # L5 Input validation
        self._validate_input(json_data, mode)
        
        # L5 Safety validation - fail-closed
        if not self.validate_safety(json_data):
            raise SecurityError("JSON data failed L5 safety validation")
        
        try:
            # Check input size
            if len(json_data) > parse_constraints.max_input_size:
                return ParseResponse(
                    parse_id=parse_id,
                    status=ParseStatus.TOO_LARGE,
                    error_message=f"JSON data too large: {len(json_data)} > {parse_constraints.max_input_size}",
                    safety_validated=False,
                    timestamp=self._get_timestamp()
                )
            
            # Parse based on mode
            if mode == ParseMode.PARSE:
                result = self._parse_json(json_data, parse_constraints)
            elif mode == ParseMode.VALIDATE:
                result = self._validate_json(json_data, parse_constraints)
            elif mode == ParseMode.EXTRACT_PATHS:
                result = self._extract_paths(json_data, parse_constraints)
            elif mode == ParseMode.FLATTEN:
                result = self._flatten_json(json_data, parse_constraints)
            elif mode == ParseMode.SCHEMA_INFERENCE:
                result = self._infer_schema(json_data, parse_constraints)
            elif mode == ParseMode.TRANSFORM:
                result = self._transform_json(json_data, parse_constraints)
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
            
            self.logger.info(f"JSON parsing completed: {mode.value}")
            return response
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return ParseResponse(
                parse_id=parse_id,
                status=ParseStatus.INVALID_JSON,
                error_message=f"Invalid JSON: {str(e)}",
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
        except Exception as e:
            self.logger.error(f"JSON parsing error: {e}")
            return ParseResponse(
                parse_id=parse_id,
                status=ParseStatus.FAILED,
                error_message=str(e),
                safety_validated=False,
                timestamp=self._get_timestamp()
            )
    
    def _parse_json(self, json_data: str, constraints: ParseConstraints) -> ParseResult:
        """Parse JSON into Python object"""
        parsed_data = json.loads(json_data)
        
        # Validate parsed data safety
        self._validate_data_safety(parsed_data, constraints)
        
        return ParseResult(
            parse_mode=ParseMode.PARSE,
            original_data=json_data,
            parsed_data=parsed_data,
            metadata={
                "data_type": type(parsed_data).__name__,
                "size": len(json_data),
                "keys_count": self._count_keys(parsed_data) if isinstance(parsed_data, dict) else 0
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _validate_json(self, json_data: str, constraints: ParseConstraints) -> ParseResult:
        """Validate JSON structure and content"""
        parsed_data = json.loads(json_data)
        
        # Perform comprehensive validation
        validation_errors = []
        
        # Check depth
        depth = self._calculate_depth(parsed_data)
        if depth > constraints.max_depth:
            validation_errors.append(f"JSON too deep: {depth} > {constraints.max_depth}")
        
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
        
        return ParseResult(
            parse_mode=ParseMode.VALIDATE,
            original_data=json_data,
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
    
    def _extract_paths(self, json_data: str, constraints: ParseConstraints) -> ParseResult:
        """Extract all JSON paths from data"""
        parsed_data = json.loads(json_data)
        paths = []
        
        def extract_paths_recursive(obj, current_path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{current_path}.{key}" if current_path else key
                    
                    # Validate path safety
                    if self._validate_path_safety(new_path, constraints):
                        path_obj = JSONPath(
                            path=new_path,
                            value=value,
                            data_type=type(value).__name__,
                            safety_validated=True
                        )
                        paths.append(path_obj)
                    
                    # Recurse for nested objects
                    if isinstance(value, (dict, list)):
                        extract_paths_recursive(value, new_path)
            
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    new_path = f"{current_path}[{i}]"
                    
                    # Validate path safety
                    if self._validate_path_safety(new_path, constraints):
                        path_obj = JSONPath(
                            path=new_path,
                            value=value,
                            data_type=type(value).__name__,
                            safety_validated=True
                        )
                        paths.append(path_obj)
                    
                    # Recurse for nested objects
                    if isinstance(value, (dict, list)):
                        extract_paths_recursive(value, new_path)
        
        extract_paths_recursive(parsed_data)
        
        return ParseResult(
            parse_mode=ParseMode.EXTRACT_PATHS,
            original_data=json_data,
            parsed_data=parsed_data,
            paths=paths,
            metadata={
                "path_count": len(paths),
                "unique_types": list(set(p.data_type for p in paths))
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _flatten_json(self, json_data: str, constraints: ParseConstraints) -> ParseResult:
        """Flatten JSON structure"""
        parsed_data = json.loads(json_data)
        flattened = {}
        
        def flatten_recursive(obj, current_path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{current_path}.{key}" if current_path else key
                    
                    if isinstance(value, (dict, list)):
                        flatten_recursive(value, new_path)
                    else:
                        flattened[new_path] = value
            
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    new_path = f"{current_path}[{i}]"
                    
                    if isinstance(value, (dict, list)):
                        flatten_recursive(value, new_path)
                    else:
                        flattened[new_path] = value
        
        flatten_recursive(parsed_data)
        
        return ParseResult(
            parse_mode=ParseMode.FLATTEN,
            original_data=json_data,
            parsed_data=parsed_data,
            flattened_data=flattened,
            metadata={
                "original_depth": self._calculate_depth(parsed_data),
                "flattened_keys": len(flattened)
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _infer_schema(self, json_data: str, constraints: ParseConstraints) -> ParseResult:
        """Infer JSON schema from data"""
        parsed_data = json.loads(json_data)
        schema = self._infer_schema_recursive(parsed_data)
        
        return ParseResult(
            parse_mode=ParseMode.SCHEMA_INFERENCE,
            original_data=json_data,
            parsed_data=parsed_data,
            schema=schema,
            metadata={
                "schema_type": schema.get("type", "unknown"),
                "inferred_properties": len(schema.get("properties", {})) if schema.get("type") == "object" else 0
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
    def _transform_json(self, json_data: str, constraints: ParseConstraints) -> ParseResult:
        """Transform JSON (basic transformations)"""
        parsed_data = json.loads(json_data)
        
        # Basic transformations
        transformed = {
            "original": parsed_data,
            "normalized": self._normalize_data(parsed_data),
            "keys_sorted": self._sort_keys(parsed_data)
        }
        
        return ParseResult(
            parse_mode=ParseMode.TRANSFORM,
            original_data=json_data,
            parsed_data=transformed,
            metadata={
                "transformations": ["original", "normalized", "keys_sorted"]
            },
            safety_validated=True,
            timestamp=self._get_timestamp()
        )
    
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
            
            # Simple schema merging (could be enhanced)
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
    
    def _calculate_depth(self, obj, current_depth=0) -> int:
        """Calculate maximum depth of JSON structure"""
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
        """Count total keys in JSON structure"""
        if isinstance(obj, dict):
            return len(obj) + sum(self._count_keys(v) for v in obj.values())
        elif isinstance(obj, list):
            return sum(self._count_keys(item) for item in obj)
        else:
            return 0
    
    def _find_max_string_length(self, obj) -> int:
        """Find maximum string length in JSON"""
        if isinstance(obj, str):
            return len(obj)
        elif isinstance(obj, dict):
            return max(self._find_max_string_length(v) for v in obj.values()) if obj else 0
        elif isinstance(obj, list):
            return max(self._find_max_string_length(item) for item in obj) if obj else 0
        else:
            return 0
    
    def _find_dangerous_content(self, obj) -> List[str]:
        """Find dangerous content in JSON"""
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
            raise ValueError(f"JSON too deep: {depth} > {constraints.max_depth}")
        
        # Check key count
        key_count = self._count_keys(obj)
        if key_count > constraints.max_keys:
            raise ValueError(f"Too many keys: {key_count} > {constraints.max_keys}")
        
        # Check for dangerous content
        if constraints.block_dangerous_content:
            dangerous_content = self._find_dangerous_content(obj)
            if dangerous_content:
                raise ValueError(f"Dangerous content found: {dangerous_content}")
    
    def _validate_path_safety(self, path: str, constraints: ParseConstraints) -> bool:
        """Validate individual path safety"""
        # Check path length
        if len(path) > 1000:
            return False
        
        # Check for suspicious characters
        if any(char in path for char in ['\0', '\r', '\n', '\t']):
            return False
        
        return True
    
    def validate_safety(self, json_data: str) -> bool:
        """L5 Safety validation with fail-closed behavior"""
        try:
            # Check data size
            if len(json_data) > self.constraints.max_input_size:
                self.logger.error("JSON data exceeds maximum size")
                return False
            
            # Check for dangerous patterns
            dangerous_patterns = ["<script>", "javascript:", "eval(", "exec(", "__import__"]
            data_lower = json_data.lower()
            for pattern in dangerous_patterns:
                if pattern in data_lower:
                    self.logger.error(f"Dangerous pattern detected: {pattern}")
                    return False
            
            # Check for suspicious content
            if json_data.count('\0') > 0:  # Null bytes
                self.logger.error("Null bytes detected in JSON")
                return False
            
            # Try to parse JSON to ensure it's valid
            json.loads(json_data)
            
            self.logger.info("JSON data passed L5 safety validation")
            return True
            
        except Exception as e:
            self.logger.error(f"Safety validation error: {e}")
            return False  # Fail-closed
    
    def _validate_input(self, json_data: str, mode: ParseMode) -> None:
        """L5 Input validation"""
        if not isinstance(json_data, str):
            raise ValueError("JSON data must be a string")
        
        if not isinstance(mode, ParseMode):
            raise ValueError("Mode must be a ParseMode enum")
        
        if not json_data.strip():
            raise ValueError("JSON data cannot be empty")
    
    def _generate_parse_id(self) -> str:
        """Generate unique parse ID"""
        import uuid
        return f"json_parse_{uuid.uuid4().hex[:8]}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for L5 observability"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

class SecurityError(Exception):
    """L5 Security exception for fail-closed behavior"""
    pass

# L5 Interface compliance
class JSONParserInterface:
    """L5 Interface - ensures contract compliance"""
    
    def __init__(self, parser: JSONParser):
        self._parser = parser
    
    def parse_json(self, json_data: str, mode: str = "parse", max_size: int = 100000) -> Dict[str, Any]:
        """L5 Interface method - executes safely"""
        try:
            parse_mode = ParseMode(mode)
            constraints = ParseConstraints(max_input_size=max_size)
            
            response = self._parser.parse(json_data, parse_mode, constraints)
            
            if response.result:
                return {
                    "success": response.status == ParseStatus.SUCCESS,
                    "parse_id": response.parse_id,
                    "parse_mode": response.result.parse_mode.value,
                    "parsed_data": response.result.parsed_data,
                    "paths": [
                        {
                            "path": path.path,
                            "value": str(path.value),
                            "data_type": path.data_type,
                            "safety_validated": path.safety_validated
                        }
                        for path in response.result.paths
                    ],
                    "schema": response.result.schema,
                    "flattened_data": response.result.flattened_data,
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
            self.logger.error(f"JSON parsing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "safety_validated": False
            }

# L5 Factory pattern
class JSONParserFactory:
    """L5 Factory for creating JSON parser instances"""
    
    @staticmethod
    def create_parser(constraints: Optional[ParseConstraints] = None) -> JSONParser:
        return JSONParserImpl(constraints)
    
    @staticmethod
    def create_interface(constraints: Optional[ParseConstraints] = None) -> JSONParserInterface:
        parser = JSONParserFactory.create_parser(constraints)
        return JSONParserInterface(parser)

# L5 Export for module usage
__all__ = [
    "ParseMode",
    "ParseStatus",
    "ParseConstraints",
    "JSONPath",
    "ParseResult",
    "ParseResponse",
    "JSONParser",
    "JSONParserImpl",
    "JSONParserInterface",
    "JSONParserFactory",
    "SecurityError"
]
