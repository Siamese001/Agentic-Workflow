"""
L1 Cognitive Planning - Layer Interfaces Mapping

Implements pure planning operations for mapping layer interfaces
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

class InterfaceType(str, Enum):
    """Supported interface types with L5 safety validation"""
    API = "api"
    SERVICE = "service"
    EVENT = "event"
    DATA = "data"
    CONFIGURATION = "configuration"
    MESSAGING = "messaging"


class InterfaceDirection(str, Enum):
    """Interface direction types with L5 safety enforcement"""
    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"


class LayerInterfacesSafetyPolicy(BaseModel):
    """L5 Safety policy for layer interfaces mapping operations"""
    max_interface_count: int = Field(default=50, description="Maximum interfaces per layer")
    max_parameter_count: int = Field(default=20, description="Maximum parameters per interface")
    allowed_interface_types: List[str] = Field(default_factory=lambda: [t.value for t in InterfaceType])
    allowed_directions: List[str] = Field(default_factory=lambda: [t.value for t in InterfaceDirection])
    require_interface_validation: bool = Field(default=True)
    prevent_interface_injection: bool = Field(default=True)
    sanitize_interface_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerInterfacesSafetyValidator:
    """L5 Safety validator for layer interfaces mapping operations"""
    
    def __init__(self, policy: LayerInterfacesSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerInterfacesSafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads"
        ]
        self._injection_patterns = [
            r"\${", r"%{", r"{{", r"\[\[",  # Template injection
            r"union\s+select", r"drop\s+table",  # SQL injection
            r"<\?php", r"<%", r"@\s*import"  # Code injection
        ]
    
    def validate_interfaces_input(self, interfaces_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates interfaces input against L5 safety policies"""
        try:
            # Check interface count
            layer_spec = interfaces_input.get("layer_spec", {})
            interfaces = layer_spec.get("interfaces", [])
            if len(interfaces) > self.policy.max_interface_count:
                error_msg = f"Too many interfaces: {len(interfaces)} > {self.policy.max_interface_count}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check interface types
            for interface in interfaces:
                interface_type = interface.get("type", "")
                if interface_type not in self.policy.allowed_interface_types:
                    error_msg = f"Prohibited interface type: {interface_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
                
                # Check parameter count
                parameters = interface.get("parameters", [])
                if len(parameters) > self.policy.max_parameter_count:
                    error_msg = f"Too many parameters: {len(parameters)} > {self.policy.max_parameter_count}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(layer_spec).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for injection patterns
            for pattern in self._injection_patterns:
                if pattern in content_str:
                    error_msg = f"Injection pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            return True, None
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.logger.error(f"Safety validation failed: {error_msg}")
            if self.policy.fail_closed:
                return False, error_msg
            return True, error_msg


# ============================================================================
# L1 COGNITIVE PLANNING INTERFACES
# ============================================================================

@dataclass
class InterfaceParameter:
    """Individual interface parameter specification"""
    name: str
    type: str
    required: bool
    default_value: Optional[Any]
    validation_rules: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class LayerInterface:
    """Individual layer interface specification"""
    id: str
    name: str
    type: InterfaceType
    direction: InterfaceDirection
    description: str
    parameters: List[InterfaceParameter]
    return_type: Optional[str]
    endpoint: Optional[str]
    protocol: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class LayerInterfacesRequest:
    """Input request for layer interfaces mapping operations"""
    layer_name: str
    layer_spec: Dict[str, Any]
    mapping_options: Dict[str, Any]
    context: Dict[str, Any]
    interface_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class MappedInterfaces:
    """Structured representation of mapped layer interfaces"""
    layer_name: str
    api_interfaces: List[LayerInterface]
    service_interfaces: List[LayerInterface]
    event_interfaces: List[LayerInterface]
    data_interfaces: List[LayerInterface]
    configuration_interfaces: List[LayerInterface]
    messaging_interfaces: List[LayerInterface]
    interface_graph: Dict[str, List[str]]
    interface_dependencies: Dict[str, List[str]]


@dataclass
class InterfacesMappingResult:
    """Output result from layer interfaces mapping operations"""
    mapped_interfaces: MappedInterfaces
    mapping_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    interfaces_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerInterfacesMapperInterface(ABC):
    """Abstract interface for layer interfaces mapping operations"""
    
    @abstractmethod
    async def map_interfaces(self, request: LayerInterfacesRequest) -> InterfacesMappingResult:
        """Map layer interfaces from specification"""
        pass
    
    @abstractmethod
    async def build_interface_graph(self, interfaces: List[LayerInterface]) -> Dict[str, List[str]]:
        """Build interface graph from mapped interfaces"""
        pass
    
    @abstractmethod
    async def validate_interface_consistency(self, interfaces: List[LayerInterface]) -> List[str]:
        """Validate interface consistency and completeness"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerInterfacesMapper(LayerInterfacesMapperInterface):
    """
    L1 Cognitive Planning implementation for mapping layer interfaces.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerInterfacesSafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerInterfacesSafetyPolicy()
        self.safety_validator = LayerInterfacesSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Interface mapping patterns and rules
        self._mapping_patterns = {
            InterfaceType.API: [
                r"api\s+(\w+)", r"endpoint\s+(\w+)", r"rest\s+(\w+)",
                r"get\s+(\w+)", r"post\s+(\w+)", r"put\s+(\w+)", r"delete\s+(\w+)"
            ],
            InterfaceType.SERVICE: [
                r"service\s+(\w+)", r"microservice\s+(\w+)",
                r"rpc\s+(\w+)", r"grpc\s+(\w+)"
            ],
            InterfaceType.EVENT: [
                r"event\s+(\w+)", r"publisher\s+(\w+)", r"subscriber\s+(\w+)",
                r"emit\s+(\w+)", r"listen\s+(\w+)"
            ],
            InterfaceType.DATA: [
                r"data\s+(\w+)", r"database\s+(\w+)", r"storage\s+(\w+)",
                r"query\s+(\w+)", r"insert\s+(\w+)", r"update\s+(\w+)"
            ],
            InterfaceType.CONFIGURATION: [
                r"config\s+(\w+)", r"settings\s+(\w+)", r"properties\s+(\w+)",
                r"environment\s+(\w+)", r"preferences\s+(\w+)"
            ],
            InterfaceType.MESSAGING: [
                r"message\s+(\w+)", r"queue\s+(\w+)", r"topic\s+(\w+)",
                r"channel\s+(\w+)", r"broker\s+(\w+)"
            ]
        }
        
        self.logger.info("LayerInterfacesMapper initialized with L5 safety policies")
    
    async def map_interfaces(self, request: LayerInterfacesRequest) -> InterfacesMappingResult:
        """
        Map layer interfaces from specification.
        
        Args:
            request: Layer interfaces mapping request with layer specification
            
        Returns:
            InterfacesMappingResult: Structured result with mapped interfaces and metadata
            
        Raises:
            ValidationError: If interfaces mapping fails
            SafetyError: If interfaces violate safety policies
        """
        self.logger.info(f"Mapping interfaces for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            interfaces_input = {
                "layer_spec": request.layer_spec
            }
            
            is_valid, error_msg = self.safety_validator.validate_interfaces_input(interfaces_input)
            if not is_valid:
                raise SafetyError(f"Interfaces safety validation failed: {error_msg}")
            
            # Extract interfaces from layer specification
            raw_interfaces = await self._extract_raw_interfaces(request.layer_spec)
            
            # Parse and structure interfaces
            parsed_interfaces = await self._parse_interfaces(raw_interfaces)
            
            # Categorize interfaces by type
            categorized_interfaces = await self._categorize_interfaces(parsed_interfaces)
            
            # Build interface graph
            all_interfaces = []
            for interface_list in categorized_interfaces.values():
                all_interfaces.extend(interface_list)
            
            interface_graph = await self.build_interface_graph(all_interfaces)
            
            # Analyze interface dependencies
            interface_dependencies = await self._analyze_interface_dependencies(all_interfaces)
            
            # Validate interface consistency
            consistency_issues = await self.validate_interface_consistency(all_interfaces)
            
            # Create mapped interfaces structure
            mapped_interfaces = MappedInterfaces(
                layer_name=request.layer_name,
                api_interfaces=categorized_interfaces.get(InterfaceType.API, []),
                service_interfaces=categorized_interfaces.get(InterfaceType.SERVICE, []),
                event_interfaces=categorized_interfaces.get(InterfaceType.EVENT, []),
                data_interfaces=categorized_interfaces.get(InterfaceType.DATA, []),
                configuration_interfaces=categorized_interfaces.get(InterfaceType.CONFIGURATION, []),
                messaging_interfaces=categorized_interfaces.get(InterfaceType.MESSAGING, []),
                interface_graph=interface_graph,
                interface_dependencies=interface_dependencies
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_interfaces_risk_score(mapped_interfaces),
                "security_flags": self._extract_security_flags(mapped_interfaces),
                "consistency_issues": consistency_issues
            }
            
            # Generate unique interfaces ID
            interfaces_id = self._generate_interfaces_id(request, mapped_interfaces)
            
            result = InterfacesMappingResult(
                mapped_interfaces=mapped_interfaces,
                mapping_metadata={
                    "mapping_duration_ms": len(all_interfaces) * 3,  # Rough estimate
                    "total_interfaces": len(all_interfaces),
                    "interface_types": list(categorized_interfaces.keys()),
                    "consistency_issues_count": len(consistency_issues),
                    "complexity_estimate": await self._estimate_mapping_complexity(request)
                },
                safety_validation=safety_validation,
                interfaces_id=interfaces_id
            )
            
            self.logger.info(f"Successfully mapped {len(all_interfaces)} interfaces for {request.layer_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to map layer interfaces: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback mapping in non-fail-closed mode
            return self._create_fallback_mapping(request, str(e))
    
    async def build_interface_graph(self, interfaces: List[LayerInterface]) -> Dict[str, List[str]]:
        """Build interface graph from mapped interfaces"""
        try:
            interface_graph = {}
            
            for interface in interfaces:
                interface_id = interface.id
                dependencies = interface.metadata.get("dependencies", [])
                
                # Validate dependencies exist
                valid_dependencies = []
                for dep in dependencies:
                    if any(i.id == dep for i in interfaces):
                        valid_dependencies.append(dep)
                    else:
                        self.logger.warning(f"Interface dependency {dep} not found for interface {interface_id}")
                
                interface_graph[interface_id] = valid_dependencies
            
            return interface_graph
            
        except Exception as e:
            self.logger.error(f"Interface graph building failed: {str(e)}")
            return {}
    
    async def validate_interface_consistency(self, interfaces: List[LayerInterface]) -> List[str]:
        """Validate interface consistency and completeness"""
        try:
            issues = []
            
            # Check for duplicate interface names
            interface_names = [i.name for i in interfaces]
            if len(interface_names) != len(set(interface_names)):
                duplicates = [name for name in interface_names if interface_names.count(name) > 1]
                issues.append(f"Duplicate interface names: {duplicates}")
            
            # Check for duplicate interface IDs
            interface_ids = [i.id for i in interfaces]
            if len(interface_ids) != len(set(interface_ids)):
                duplicates = [i_id for i_id in interface_ids if interface_ids.count(i_id) > 1]
                issues.append(f"Duplicate interface IDs: {duplicates}")
            
            # Check API interfaces have endpoints
            api_interfaces = [i for i in interfaces if i.type == InterfaceType.API]
            for api in api_interfaces:
                if not api.endpoint:
                    issues.append(f"API interface {api.name} missing endpoint")
            
            # Check service interfaces have protocols
            service_interfaces = [i for i in interfaces if i.type == InterfaceType.SERVICE]
            for service in service_interfaces:
                if not service.protocol:
                    issues.append(f"Service interface {service.name} missing protocol")
            
            # Check parameter consistency
            for interface in interfaces:
                for param in interface.parameters:
                    if not param.type:
                        issues.append(f"Interface {interface.name} parameter {param.name} missing type")
            
            return issues
            
        except Exception as e:
            self.logger.error(f"Interface consistency validation failed: {str(e)}")
            return [f"Validation error: {str(e)}"]
    
    async def _extract_raw_interfaces(self, layer_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract raw interfaces from layer specification"""
        raw_interfaces = []
        
        try:
            # Extract from explicit interfaces section
            explicit_interfaces = layer_spec.get("interfaces", [])
            if isinstance(explicit_interfaces, list):
                raw_interfaces.extend(explicit_interfaces)
            
            # Extract from APIs section
            apis = layer_spec.get("apis", [])
            if isinstance(apis, list):
                for api in apis:
                    raw_interfaces.append({
                        "name": api.get("name", ""),
                        "type": "api",
                        "direction": api.get("direction", "bidirectional"),
                        "endpoint": api.get("endpoint", ""),
                        "protocol": api.get("protocol", "http"),
                        "parameters": api.get("parameters", [])
                    })
            
            # Extract from services section
            services = layer_spec.get("services", [])
            if isinstance(services, list):
                for service in services:
                    raw_interfaces.append({
                        "name": service.get("name", ""),
                        "type": "service",
                        "direction": service.get("direction", "bidirectional"),
                        "protocol": service.get("protocol", "grpc"),
                        "parameters": service.get("parameters", [])
                    })
            
            # Extract from events section
            events = layer_spec.get("events", [])
            if isinstance(events, list):
                for event in events:
                    raw_interfaces.append({
                        "name": event.get("name", ""),
                        "type": "event",
                        "direction": event.get("direction", "output"),
                        "parameters": event.get("parameters", [])
                    })
            
            # Extract from data sources section
            data_sources = layer_spec.get("data_sources", [])
            if isinstance(data_sources, list):
                for data_source in data_sources:
                    raw_interfaces.append({
                        "name": data_source.get("name", ""),
                        "type": "data",
                        "direction": data_source.get("direction", "bidirectional"),
                        "parameters": data_source.get("parameters", [])
                    })
            
        except Exception as e:
            self.logger.error(f"Raw interface extraction failed: {str(e)}")
        
        return raw_interfaces
    
    async def _parse_interfaces(self, raw_interfaces: List[Dict[str, Any]]) -> List[LayerInterface]:
        """Parse raw interface data into structured interfaces"""
        parsed = []
        
        for i, raw_interface in enumerate(raw_interfaces):
            try:
                # Parse parameters
                parameters = []
                raw_params = raw_interface.get("parameters", [])
                for j, raw_param in enumerate(raw_params):
                    param = InterfaceParameter(
                        name=raw_param.get("name", f"param_{j}"),
                        type=raw_param.get("type", "string"),
                        required=raw_param.get("required", False),
                        default_value=raw_param.get("default_value"),
                        validation_rules=raw_param.get("validation_rules", {}),
                        metadata=raw_param.get("metadata", {})
                    )
                    parameters.append(param)
                
                interface = LayerInterface(
                    id=raw_interface.get("id", f"interface_{i:03d}"),
                    name=raw_interface.get("name", ""),
                    type=InterfaceType(raw_interface.get("type", "api")),
                    direction=InterfaceDirection(raw_interface.get("direction", "bidirectional")),
                    description=raw_interface.get("description", ""),
                    parameters=parameters,
                    return_type=raw_interface.get("return_type"),
                    endpoint=raw_interface.get("endpoint"),
                    protocol=raw_interface.get("protocol"),
                    metadata=raw_interface.get("metadata", {})
                )
                parsed.append(interface)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse interface {i}: {str(e)}")
                # Create safe fallback interface
                fallback_interface = LayerInterface(
                    id=f"fallback_interface_{i:03d}",
                    name=f"parsing_failed_{i}",
                    type=InterfaceType.API,
                    direction=InterfaceDirection.BIDIRECTIONAL,
                    description=f"Parsing failed: {str(e)}",
                    parameters=[],
                    return_type=None,
                    endpoint=None,
                    protocol=None,
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_interface)
        
        return parsed
    
    async def _categorize_interfaces(
        self, 
        interfaces: List[LayerInterface]
    ) -> Dict[InterfaceType, List[LayerInterface]]:
        """Categorize interfaces by type"""
        categorized = {interface_type: [] for interface_type in InterfaceType}
        
        for interface in interfaces:
            categorized[interface.type].append(interface)
        
        return categorized
    
    async def _analyze_interface_dependencies(self, interfaces: List[LayerInterface]) -> Dict[str, List[str]]:
        """Analyze interface dependencies"""
        try:
            dependencies = {}
            
            for interface in interfaces:
                interface_id = interface.id
                interface_deps = []
                
                # Analyze parameter dependencies
                for param in interface.parameters:
                    if "reference" in param.metadata:
                        interface_deps.append(param.metadata["reference"])
                
                # Analyze metadata dependencies
                metadata_deps = interface.metadata.get("dependencies", [])
                interface_deps.extend(metadata_deps)
                
                dependencies[interface_id] = interface_deps
            
            return dependencies
            
        except Exception as e:
            self.logger.error(f"Interface dependency analysis failed: {str(e)}")
            return {}
    
    async def _estimate_mapping_complexity(self, request: LayerInterfacesRequest) -> str:
        """Estimate mapping complexity"""
        complexity_score = len(str(request.layer_spec)) // 1000
        
        # Add complexity for explicit interfaces
        explicit_interfaces = len(request.layer_spec.get("interfaces", []))
        complexity_score += explicit_interfaces // 3
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_interfaces_risk_score(self, interfaces: MappedInterfaces) -> float:
        """Calculate risk score for the interfaces (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Count total interfaces
        all_interfaces = []
        for interface_list in [
            interfaces.api_interfaces,
            interfaces.service_interfaces,
            interfaces.event_interfaces,
            interfaces.data_interfaces,
            interfaces.configuration_interfaces,
            interfaces.messaging_interfaces
        ]:
            all_interfaces.extend(interface_list)
        
        # Increase risk for large interface sets
        if len(all_interfaces) > 30:
            risk_score += 0.2
        
        # Increase risk for API interfaces (external exposure)
        if len(interfaces.api_interfaces) > 10:
            risk_score += 0.1
        
        # Increase risk for service interfaces (distributed complexity)
        if len(interfaces.service_interfaces) > 5:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _extract_security_flags(self, interfaces: MappedInterfaces) -> List[str]:
        """Extract security flags from interfaces"""
        security_flags = []
        
        # Check for API interfaces (potential external exposure)
        if interfaces.api_interfaces:
            security_flags.append("api_interfaces")
        
        # Check for service interfaces (distributed system complexity)
        if interfaces.service_interfaces:
            security_flags.append("service_interfaces")
        
        # Check for messaging interfaces (potential message injection)
        if interfaces.messaging_interfaces:
            security_flags.append("messaging_interfaces")
        
        return security_flags
    
    def _generate_interfaces_id(self, request: LayerInterfacesRequest, interfaces: MappedInterfaces) -> str:
        """Generate unique interfaces identifier"""
        timestamp = datetime.now().isoformat()
        total_interfaces = sum(len(interface_list) for interface_list in [
            interfaces.api_interfaces,
            interfaces.service_interfaces,
            interfaces.event_interfaces,
            interfaces.data_interfaces,
            interfaces.configuration_interfaces,
            interfaces.messaging_interfaces
        ])
        content = f"{request.layer_name}:{total_interfaces}:{timestamp}"
        return f"interfaces_{hash(content) % 1000000:06d}"
    
    def _create_fallback_mapping(self, request: LayerInterfacesRequest, error: str) -> InterfacesMappingResult:
        """Create safe fallback mapping when main mapping fails"""
        fallback_interface = LayerInterface(
            id="fallback_interface_001",
            name="fallback_interface",
            type=InterfaceType.API,
            direction=InterfaceDirection.BIDIRECTIONAL,
            description="Fallback interface due to mapping failure",
            parameters=[],
            return_type=None,
            endpoint=None,
            protocol=None,
            metadata={"fallback": True, "error": error}
        )
        
        fallback_interfaces = MappedInterfaces(
            layer_name=request.layer_name,
            api_interfaces=[fallback_interface],
            service_interfaces=[],
            event_interfaces=[],
            data_interfaces=[],
            configuration_interfaces=[],
            messaging_interfaces=[],
            interface_graph={},
            interface_dependencies={}
        )
        
        return InterfacesMappingResult(
            mapped_interfaces=fallback_interfaces,
            mapping_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            interfaces_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when interfaces violate safety policies"""
    
    def __init__(self, message: str, policy_violation: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.policy_violation = policy_violation
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.policy_violation:
            return f"[SAFETY_VIOLATION: {self.policy_violation}] {base_msg}"
        return f"[SAFETY_ERROR] {base_msg}"


class InterfacesMappingError(Exception):
    """Raised for general interfaces mapping errors"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, operation: Optional[str] = None, interface_type: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code or "INTERFACES_MAPPING_ERROR"
        self.operation = operation
        self.interface_type = interface_type
        self.context = context or {}
        self.timestamp = datetime.now()
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        op_info = f" in {self.operation}" if self.operation else ""
        type_info = f" for {self.interface_type}" if self.interface_type else ""
        return f"[{self.error_code}]{op_info}{type_info} {base_msg}"


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_interfaces_mapper(safety_policy: Optional[LayerInterfacesSafetyPolicy] = None) -> LayerInterfacesMapper:
    """Factory function to create LayerInterfacesMapper with optional custom safety policy"""
    return LayerInterfacesMapper(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_interfaces_request(request: LayerInterfacesRequest) -> tuple[bool, Optional[str]]:
    """Validate layer interfaces request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not isinstance(request.layer_spec, dict):
            return False, "Layer specification must be a dictionary"
        
        if not isinstance(request.mapping_options, dict):
            return False, "Mapping options must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
