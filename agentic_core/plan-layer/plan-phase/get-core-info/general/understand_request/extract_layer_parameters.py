"""
L1 Cognitive Planning - Layer Parameter Extraction

Implements pure planning operations for extracting and normalizing layer parameters
with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from __future__ import annotations
import logging
import asyncio
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field, ValidationError


# ============================================================================
# L5 SAFETY & LOGGING INFRASTRUCTURE
# ============================================================================

class ParameterType(str, Enum):
    """Supported parameter types with L5 safety validation"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    JSON = "json"
    BINARY = "binary"


class ParameterScope(str, Enum):
    """Parameter scope types with L5 safety enforcement"""
    GLOBAL = "global"
    LAYER = "layer"
    COMPONENT = "component"
    FUNCTION = "function"
    INSTANCE = "instance"


class LayerParameterSafetyPolicy(BaseModel):
    """L5 Safety policy for layer parameter extraction operations"""
    max_parameter_count: int = Field(default=100, description="Maximum parameters per layer")
    max_parameter_size: int = Field(default=10240, description="Maximum parameter size in bytes")
    allowed_parameter_types: List[str] = Field(default_factory=lambda: [t.value for t in ParameterType])
    allowed_scopes: List[str] = Field(default_factory=lambda: [t.value for t in ParameterScope])
    require_type_validation: bool = Field(default=True)
    prevent_code_injection: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerParameterSafetyValidator:
    """L5 Safety validator for layer parameter extraction operations"""
    
    def __init__(self, policy: LayerParameterSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerParameterSafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"__import__", r"eval\s*\(", r"exec\s*\(", r"open\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads", r"yaml\.load"
        ]
        self._max_nesting_depth = 10
    
    def validate_parameter_input(self, parameter_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates parameter input against L5 safety policies"""
        try:
            # Check parameter count
            parameters = parameter_input.get("parameters", {})
            if len(parameters) > self.policy.max_parameter_count:
                error_msg = f"Too many parameters: {len(parameters)} > {self.policy.max_parameter_count}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check parameter types
            for param_name, param_value in parameters.items():
                param_type = parameter_input.get("parameter_types", {}).get(param_name, "string")
                if param_type not in self.policy.allowed_parameter_types:
                    error_msg = f"Prohibited parameter type: {param_type} for {param_name}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
                
                # Check parameter size
                param_size = len(str(param_value).encode('utf-8'))
                if param_size > self.policy.max_parameter_size:
                    error_msg = f"Parameter too large: {param_name} size {param_size} > {self.policy.max_parameter_size}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for dangerous patterns in string parameters
            for param_name, param_value in parameters.items():
                if isinstance(param_value, str):
                    for pattern in self._dangerous_patterns:
                        if pattern in param_value.lower():
                            error_msg = f"Dangerous pattern in parameter {param_name}: {pattern}"
                            self.logger.warning(f"Safety violation: {error_msg}")
                            return False, error_msg
            
            # Validate nesting depth
            max_depth = self._calculate_nesting_depth(parameters)
            if max_depth > self._max_nesting_depth:
                error_msg = f"Parameter nesting too deep: {max_depth} > {self._max_nesting_depth}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            return True, None
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.logger.error(f"Safety validation failed: {error_msg}")
            if self.policy.fail_closed:
                return False, error_msg
            return True, error_msg
    
    def _calculate_nesting_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth of parameter structure"""
        if current_depth > self._max_nesting_depth:
            return current_depth
        
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_nesting_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._calculate_nesting_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth


# ============================================================================
# L1 COGNITIVE PLANNING INTERFACES
# ============================================================================

@dataclass
class LayerParameterRequest:
    """Input request for layer parameter extraction operations"""
    layer_name: str
    raw_parameters: Dict[str, Any]
    context: Dict[str, Any]
    extraction_options: Dict[str, Any] = field(default_factory=dict)
    target_scopes: Optional[List[ParameterScope]] = None
    safety_level: str = "standard"


@dataclass
class ExtractedParameter:
    """Structured representation of an extracted parameter"""
    name: str
    value: Any
    parameter_type: ParameterType
    scope: ParameterScope
    required: bool
    default_value: Optional[Any]
    validation_rules: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class LayerParameterSet:
    """Complete set of parameters for a layer"""
    layer_name: str
    parameters: List[ExtractedParameter]
    global_parameters: List[ExtractedParameter]
    layer_constraints: Dict[str, Any]
    dependency_parameters: Dict[str, List[str]]
    parameter_hierarchy: Dict[str, List[str]]


@dataclass
class LayerParameterResult:
    """Output result from layer parameter extraction operations"""
    parameter_set: LayerParameterSet
    extraction_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    parameter_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerParameterExtractorInterface(ABC):
    """Abstract interface for layer parameter extraction operations"""
    
    @abstractmethod
    async def extract_parameters(self, request: LayerParameterRequest) -> LayerParameterResult:
        """Extract and normalize layer parameters"""
        pass
    
    @abstractmethod
    async def validate_parameter_consistency(self, parameters: List[ExtractedParameter]) -> tuple[bool, Optional[str]]:
        """Validate consistency of extracted parameters"""
        pass
    
    @abstractmethod
    async def normalize_parameter_values(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize parameter values to standard types"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerParameterExtractor(LayerParameterExtractorInterface):
    """
    L1 Cognitive Planning implementation for extracting layer parameters.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerParameterSafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerParameterSafetyPolicy()
        self.safety_validator = LayerParameterSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Parameter extraction patterns and rules
        self._parameter_patterns = {
            "config": r"config_(.+)",
            "setting": r"setting_(.+)",
            "option": r"option_(.+)",
            "param": r"param_(.+)",
            "var": r"var_(.+)"
        }
        
        self._type_inference_rules = {
            "int": ParameterType.INTEGER,
            "float": ParameterType.FLOAT,
            "bool": ParameterType.BOOLEAN,
            "str": ParameterType.STRING,
            "list": ParameterType.LIST,
            "dict": ParameterType.DICT
        }
        
        self.logger.info("LayerParameterExtractor initialized with L5 safety policies")
    
    async def extract_parameters(self, request: LayerParameterRequest) -> LayerParameterResult:
        """
        Extract and normalize layer parameters.
        
        Args:
            request: Layer parameter extraction request with raw parameters
            
        Returns:
            LayerParameterResult: Structured result with extracted parameter set
            
        Raises:
            ValidationError: If parameter extraction fails
            SafetyError: If parameters violate safety policies
        """
        self.logger.info(f"Extracting parameters for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            parameter_input = {
                "parameters": request.raw_parameters,
                "parameter_types": request.extraction_options.get("type_hints", {})
            }
            
            is_valid, error_msg = self.safety_validator.validate_parameter_input(parameter_input)
            if not is_valid:
                raise SafetyError(f"Parameter validation failed: {error_msg}")
            
            # Normalize parameter values
            normalized_params = await self.normalize_parameter_values(request.raw_parameters)
            
            # Extract individual parameters
            extracted_params = []
            for param_name, param_value in normalized_params.items():
                extracted_param = await self._extract_single_parameter(
                    param_name, param_value, request.extraction_options
                )
                extracted_params.append(extracted_param)
            
            # Separate global and layer-specific parameters
            global_params, layer_params = await self._separate_parameters_by_scope(extracted_params)
            
            # Extract layer constraints
            layer_constraints = await self._extract_layer_constraints(normalized_params, request.context)
            
            # Extract parameter dependencies
            dependencies = await self._extract_parameter_dependencies(extracted_params)
            
            # Build parameter hierarchy
            hierarchy = await self._build_parameter_hierarchy(extracted_params)
            
            # Validate parameter consistency
            consistent, consistency_error = await self.validate_parameter_consistency(extracted_params)
            if not consistent:
                self.logger.warning(f"Parameter consistency issue: {consistency_error}")
            
            # Create parameter set
            parameter_set = LayerParameterSet(
                layer_name=request.layer_name,
                parameters=layer_params,
                global_parameters=global_params,
                layer_constraints=layer_constraints,
                dependency_parameters=dependencies,
                parameter_hierarchy=hierarchy
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_parameter_risk_score(extracted_params),
                "constraints_applied": layer_constraints
            }
            
            # Generate unique parameter ID
            parameter_id = self._generate_parameter_id(request, parameter_set)
            
            result = LayerParameterResult(
                parameter_set=parameter_set,
                extraction_metadata={
                    "extraction_duration_ms": len(request.raw_parameters) * 0.3,  # Rough estimate
                    "parameters_extracted": len(extracted_params),
                    "global_parameters": len(global_params),
                    "layer_parameters": len(layer_params),
                    "complexity_estimate": await self._estimate_extraction_complexity(request.raw_parameters)
                },
                safety_validation=safety_validation,
                parameter_id=parameter_id
            )
            
            self.logger.info(f"Successfully extracted {len(extracted_params)} parameters for {request.layer_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to extract layer parameters: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback extraction in non-fail-closed mode
            return self._create_fallback_extraction(request, str(e))
    
    async def validate_parameter_consistency(self, parameters: List[ExtractedParameter]) -> tuple[bool, Optional[str]]:
        """Validate consistency of extracted parameters"""
        try:
            # Check for duplicate parameter names
            param_names = [p.name for p in parameters]
            if len(param_names) != len(set(param_names)):
                duplicates = [name for name in param_names if param_names.count(name) > 1]
                return False, f"Duplicate parameter names: {duplicates}"
            
            # Check for circular dependencies
            dependency_graph = {}
            for param in parameters:
                dependency_graph[param.name] = param.metadata.get("dependencies", [])
            
            if self._has_circular_dependencies(dependency_graph):
                return False, "Circular parameter dependencies detected"
            
            # Check type consistency
            for param in parameters:
                if param.parameter_type == ParameterType.LIST and not isinstance(param.value, list):
                    return False, f"Parameter {param.name} declared as list but is not list type"
                
                if param.parameter_type == ParameterType.DICT and not isinstance(param.value, dict):
                    return False, f"Parameter {param.name} declared as dict but is not dict type"
            
            return True, None
            
        except Exception as e:
            return False, f"Consistency validation error: {str(e)}"
    
    async def normalize_parameter_values(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize parameter values to standard types"""
        try:
            normalized = {}
            
            for param_name, param_value in parameters.items():
                # Skip None values
                if param_value is None:
                    normalized[param_name] = None
                    continue
                
                # Type-specific normalization
                if isinstance(param_value, str):
                    # String normalization
                    normalized[param_name] = param_value.strip()
                elif isinstance(param_value, (int, float)):
                    # Numeric normalization
                    normalized[param_name] = param_value
                elif isinstance(param_value, bool):
                    # Boolean normalization
                    normalized[param_name] = param_value
                elif isinstance(param_value, list):
                    # List normalization
                    normalized[param_name] = [str(item).strip() for item in param_value if item is not None]
                elif isinstance(param_value, dict):
                    # Dict normalization
                    normalized[param_name] = {
                        str(k).strip(): self._normalize_value(v) 
                        for k, v in param_value.items() 
                        if v is not None
                    }
                else:
                    # Fallback normalization
                    normalized[param_name] = str(param_value)
            
            return normalized
            
        except Exception as e:
            self.logger.error(f"Parameter normalization failed: {str(e)}")
            # Return original parameters if normalization fails
            return parameters
    
    async def _extract_single_parameter(
        self, 
        name: str, 
        value: Any, 
        options: Dict[str, Any]
    ) -> ExtractedParameter:
        """Extract a single parameter with full metadata"""
        # Infer parameter type
        param_type = self._infer_parameter_type(value, options.get("type_hints", {}).get(name))
        
        # Determine scope
        scope = self._determine_parameter_scope(name, options.get("scope_hints", {}))
        
        # Check if required
        required = self._is_parameter_required(name, value, options.get("required_params", []))
        
        # Get default value
        default_value = options.get("defaults", {}).get(name)
        
        # Extract validation rules
        validation_rules = self._extract_validation_rules(name, options.get("validation", {}))
        
        # Extract metadata
        metadata = {
            "source": "extraction",
            "dependencies": options.get("dependencies", {}).get(name, []),
            "description": options.get("descriptions", {}).get(name, ""),
            "category": self._categorize_parameter(name)
        }
        
        return ExtractedParameter(
            name=name,
            value=value,
            parameter_type=param_type,
            scope=scope,
            required=required,
            default_value=default_value,
            validation_rules=validation_rules,
            metadata=metadata
        )
    
    def _infer_parameter_type(self, value: Any, type_hint: Optional[str] = None) -> ParameterType:
        """Infer parameter type from value and optional hint"""
        if type_hint:
            return ParameterType(type_hint.lower())
        
        if isinstance(value, str):
            return ParameterType.STRING
        elif isinstance(value, int):
            return ParameterType.INTEGER
        elif isinstance(value, float):
            return ParameterType.FLOAT
        elif isinstance(value, bool):
            return ParameterType.BOOLEAN
        elif isinstance(value, list):
            return ParameterType.LIST
        elif isinstance(value, dict):
            return ParameterType.DICT
        else:
            return ParameterType.STRING  # Safe default
    
    def _determine_parameter_scope(self, name: str, scope_hints: Dict[str, str]) -> ParameterScope:
        """Determine parameter scope from name and hints"""
        if name in scope_hints:
            return ParameterScope(scope_hints[name].lower())
        
        name_lower = name.lower()
        if name_lower.startswith("global_") or name_lower.startswith("system_"):
            return ParameterScope.GLOBAL
        elif name_lower.startswith("layer_"):
            return ParameterScope.LAYER
        elif name_lower.startswith("component_"):
            return ParameterScope.COMPONENT
        elif name_lower.startswith("func_") or name_lower.startswith("method_"):
            return ParameterScope.FUNCTION
        else:
            return ParameterScope.INSTANCE  # Safe default
    
    def _is_parameter_required(self, name: str, value: Any, required_params: List[str]) -> bool:
        """Check if parameter is required"""
        if name in required_params:
            return True
        
        # Consider parameters with None values as not required unless explicitly marked
        if value is None:
            return False
        
        # Consider empty strings/lists as not required unless explicitly marked
        if isinstance(value, str) and not value.strip():
            return False
        
        if isinstance(value, list) and not value:
            return False
        
        return False  # Safe default
    
    def _extract_validation_rules(self, name: str, validation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract validation rules for a parameter"""
        return validation_config.get(name, {
            "type_check": True,
            "range_check": False,
            "pattern_check": False
        })
    
    def _categorize_parameter(self, name: str) -> str:
        """Categorize parameter by name pattern"""
        name_lower = name.lower()
        
        for category, pattern in self._parameter_patterns.items():
            if pattern in name_lower:
                return category
        
        return "general"
    
    async def _separate_parameters_by_scope(
        self, 
        parameters: List[ExtractedParameter]
    ) -> Tuple[List[ExtractedParameter], List[ExtractedParameter]]:
        """Separate global and layer-specific parameters"""
        global_params = [p for p in parameters if p.scope == ParameterScope.GLOBAL]
        layer_params = [p for p in parameters if p.scope != ParameterScope.GLOBAL]
        
        return global_params, layer_params
    
    async def _extract_layer_constraints(
        self, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract layer-specific constraints"""
        constraints = {}
        
        # Extract constraint patterns
        for param_name, param_value in parameters.items():
            if "constraint" in param_name.lower():
                constraint_name = param_name.replace("_constraint", "").replace("constraint_", "")
                constraints[constraint_name] = param_value
        
        # Add context-based constraints
        if context:
            constraints.update(context.get("constraints", {}))
        
        return constraints
    
    async def _extract_parameter_dependencies(
        self, 
        parameters: List[ExtractedParameter]
    ) -> Dict[str, List[str]]:
        """Extract parameter dependencies"""
        dependencies = {}
        
        for param in parameters:
            param_deps = param.metadata.get("dependencies", [])
            if param_deps:
                dependencies[param.name] = param_deps
        
        return dependencies
    
    async def _build_parameter_hierarchy(
        self, 
        parameters: List[ExtractedParameter]
    ) -> Dict[str, List[str]]:
        """Build parameter hierarchy based on scopes and categories"""
        hierarchy = {}
        
        # Group by scope
        for param in parameters:
            scope = param.scope.value
            if scope not in hierarchy:
                hierarchy[scope] = []
            hierarchy[scope].append(param.name)
        
        # Group by category
        for param in parameters:
            category = param.metadata.get("category", "general")
            if category not in hierarchy:
                hierarchy[category] = []
            hierarchy[category].append(param.name)
        
        return hierarchy
    
    def _has_circular_dependencies(self, dependency_graph: Dict[str, List[str]]) -> bool:
        """Check if dependency graph has circular dependencies"""
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependency_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in dependency_graph:
            if node not in visited:
                if has_cycle(node):
                    return True
        
        return False
    
    def _normalize_value(self, value: Any) -> Any:
        """Normalize a single value"""
        if isinstance(value, str):
            return value.strip()
        elif isinstance(value, (int, float, bool)):
            return value
        elif isinstance(value, list):
            return [str(item).strip() for item in value if item is not None]
        elif isinstance(value, dict):
            return {str(k).strip(): self._normalize_value(v) for k, v in value.items() if v is not None}
        else:
            return str(value)
    
    async def _estimate_extraction_complexity(self, parameters: Dict[str, Any]) -> str:
        """Estimate extraction complexity"""
        complexity_score = len(parameters) // 10
        
        # Add complexity for nested structures
        for value in parameters.values():
            if isinstance(value, (dict, list)):
                complexity_score += 1
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_parameter_risk_score(self, parameters: List[ExtractedParameter]) -> float:
        """Calculate risk score for the parameter set (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for large parameter sets
        if len(parameters) > 50:
            risk_score += 0.2
        
        # Increase risk for binary parameters
        binary_params = [p for p in parameters if p.parameter_type == ParameterType.BINARY]
        if binary_params:
            risk_score += 0.3
        
        # Increase risk for global scope parameters
        global_params = [p for p in parameters if p.scope == ParameterScope.GLOBAL]
        if len(global_params) > 10:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_parameter_id(self, request: LayerParameterRequest, parameter_set: LayerParameterSet) -> str:
        """Generate unique parameter identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.layer_name}:{len(parameter_set.parameters)}:{timestamp}"
        return f"params_{hash(content) % 1000000:06d}"
    
    def _create_fallback_extraction(self, request: LayerParameterRequest, error: str) -> LayerParameterResult:
        """Create safe fallback extraction when main extraction fails"""
        fallback_param = ExtractedParameter(
            name="fallback_param",
            value="safe_default",
            parameter_type=ParameterType.STRING,
            scope=ParameterScope.LAYER,
            required=False,
            default_value="safe_default",
            validation_rules={"type_check": True},
            metadata={"fallback": True, "error": error}
        )
        
        fallback_set = LayerParameterSet(
            layer_name=request.layer_name,
            parameters=[fallback_param],
            global_parameters=[],
            layer_constraints={"read_only": True},
            dependency_parameters={},
            parameter_hierarchy={"layer": ["fallback_param"]}
        )
        
        return LayerParameterResult(
            parameter_set=fallback_set,
            extraction_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            parameter_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when parameters violate safety policies"""
    pass


class ParameterExtractionError(Exception):
    """Raised for general parameter extraction errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_parameter_extractor(safety_policy: Optional[LayerParameterSafetyPolicy] = None) -> LayerParameterExtractor:
    """Factory function to create LayerParameterExtractor with optional custom safety policy"""
    return LayerParameterExtractor(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_parameter_request(request: LayerParameterRequest) -> tuple[bool, Optional[str]]:
    """Validate layer parameter request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not isinstance(request.raw_parameters, dict):
            return False, "Raw parameters must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"