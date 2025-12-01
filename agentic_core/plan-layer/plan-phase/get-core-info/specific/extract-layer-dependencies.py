"""
L1 Cognitive Planning - Layer Dependencies Extraction

Implements pure planning operations for extracting layer dependencies
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

class DependencyType(str, Enum):
    """Supported dependency types with L5 safety validation"""
    FUNCTIONAL = "functional"
    DATA = "data"
    SERVICE = "service"
    LIBRARY = "library"
    API = "api"
    CONFIGURATION = "configuration"


class DependencyDirection(str, Enum):
    """Dependency direction types with L5 safety enforcement"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"


class LayerDependenciesSafetyPolicy(BaseModel):
    """L5 Safety policy for layer dependencies extraction operations"""
    max_dependency_count: int = Field(default=100, description="Maximum dependencies per layer")
    max_dependency_depth: int = Field(default=5, description="Maximum dependency chain depth")
    allowed_dependency_types: List[str] = Field(default_factory=lambda: [t.value for t in DependencyType])
    allowed_directions: List[str] = Field(default_factory=lambda: [t.value for t in DependencyDirection])
    require_dependency_validation: bool = Field(default=True)
    prevent_circular_dependencies: bool = Field(default=True)
    sanitize_dependency_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerDependenciesSafetyValidator:
    """L5 Safety validator for layer dependencies extraction operations"""
    
    def __init__(self, policy: LayerDependenciesSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerDependenciesSafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"<script", r"javascript:", r"data:text/html",
            r"__import__", r"eval\s*\(", r"exec\s*\(",
            r"os\.system", r"subprocess\.", r"pickle\.loads"
        ]
        self._privileged_dependencies = [
            "system", "admin", "root", "kernel", "driver",
            "hardware", "bios", "firmware", "bootloader"
        ]
    
    def validate_dependencies_input(self, dependencies_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates dependencies input against L5 safety policies"""
        try:
            # Check dependency count
            layer_spec = dependencies_input.get("layer_spec", {})
            dependencies = layer_spec.get("dependencies", [])
            if len(dependencies) > self.policy.max_dependency_count:
                error_msg = f"Too many dependencies: {len(dependencies)} > {self.policy.max_dependency_count}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check dependency types
            for dep in dependencies:
                dep_type = dep.get("type", "")
                if dep_type not in self.policy.allowed_dependency_types:
                    error_msg = f"Prohibited dependency type: {dep_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(layer_spec).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for privileged dependencies
            for privileged in self._privileged_dependencies:
                if privileged in content_str:
                    self.logger.warning(f"Privileged dependency detected: {privileged}")
                    # Additional validation would be required in production
            
            # Validate dependency depth
            if self.policy.require_dependency_validation:
                max_depth = self._calculate_dependency_depth(dependencies)
                if max_depth > self.policy.max_dependency_depth:
                    error_msg = f"Dependency chain too deep: {max_depth} > {self.policy.max_dependency_depth}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            return True, None
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.logger.error(f"Safety validation failed: {error_msg}")
            if self.policy.fail_closed:
                return False, error_msg
            return True, error_msg
    
    def _calculate_dependency_depth(self, dependencies: List[Dict[str, Any]]) -> int:
        """Calculate maximum dependency chain depth"""
        try:
            dependency_graph = {}
            for dep in dependencies:
                dep_id = dep.get("id", "")
                sub_deps = dep.get("dependencies", [])
                dependency_graph[dep_id] = sub_deps
            
            def get_depth(node, visited=None):
                if visited is None:
                    visited = set()
                
                if node in visited:
                    return float('inf')  # Circular dependency
                
                visited.add(node)
                deps = dependency_graph.get(node, [])
                
                if not deps:
                    return 1
                
                max_dep_depth = 0
                for dep in deps:
                    dep_depth = get_depth(dep, visited.copy())
                    if dep_depth == float('inf'):
                        return float('inf')
                    max_dep_depth = max(max_dep_depth, dep_depth)
                
                return max_dep_depth + 1
            
            max_depth = 0
            for node in dependency_graph:
                depth = get_depth(node)
                if depth == float('inf'):
                    return float('inf')  # Circular dependency
                max_depth = max(max_depth, depth)
            
            return max_depth
            
        except Exception as e:
            self.logger.error(f"Dependency depth calculation failed: {str(e)}")
            return 0


# ============================================================================
# L1 COGNITIVE PLANNING INTERFACES
# ============================================================================

@dataclass
class LayerDependency:
    """Individual layer dependency specification"""
    id: str
    name: str
    type: DependencyType
    direction: DependencyDirection
    target_layer: str
    version: str
    required: bool
    metadata: Dict[str, Any]
    sub_dependencies: List[str]


@dataclass
class LayerDependenciesRequest:
    """Input request for layer dependencies extraction operations"""
    layer_name: str
    layer_spec: Dict[str, Any]
    extraction_options: Dict[str, Any]
    context: Dict[str, Any]
    dependency_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class ExtractedDependencies:
    """Structured representation of extracted layer dependencies"""
    layer_name: str
    functional_dependencies: List[LayerDependency]
    data_dependencies: List[LayerDependency]
    service_dependencies: List[LayerDependency]
    library_dependencies: List[LayerDependency]
    api_dependencies: List[LayerDependency]
    configuration_dependencies: List[LayerDependency]
    dependency_graph: Dict[str, List[str]]
    circular_dependencies: List[str]


@dataclass
class DependenciesExtractionResult:
    """Output result from layer dependencies extraction operations"""
    extracted_dependencies: ExtractedDependencies
    extraction_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    dependencies_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerDependenciesExtractorInterface(ABC):
    """Abstract interface for layer dependencies extraction operations"""
    
    @abstractmethod
    async def extract_dependencies(self, request: LayerDependenciesRequest) -> DependenciesExtractionResult:
        """Extract layer dependencies from specification"""
        pass
    
    @abstractmethod
    async def build_dependency_graph(self, dependencies: List[LayerDependency]) -> Dict[str, List[str]]:
        """Build dependency graph from extracted dependencies"""
        pass
    
    @abstractmethod
    async def detect_circular_dependencies(self, dependency_graph: Dict[str, List[str]]) -> List[str]:
        """Detect circular dependencies in the graph"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerDependenciesExtractor(LayerDependenciesExtractorInterface):
    """
    L1 Cognitive Planning implementation for extracting layer dependencies.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerDependenciesSafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerDependenciesSafetyPolicy()
        self.safety_validator = LayerDependenciesSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Dependency extraction patterns and rules
        self._extraction_patterns = {
            DependencyType.FUNCTIONAL: [
                r"depends\s+on\s+(\w+)", r"requires\s+(\w+)", r"needs\s+(\w+)",
                r"uses\s+(\w+)", r"calls\s+(\w+)"
            ],
            DependencyType.DATA: [
                r"reads\s+from\s+(\w+)", r"writes\s+to\s+(\w+)",
                r"data\s+source\s+(\w+)", r"data\s+sink\s+(\w+)"
            ],
            DependencyType.SERVICE: [
                r"service\s+(\w+)", r"microservice\s+(\w+)",
                r"api\s+service\s+(\w+)", r"external\s+service\s+(\w+)"
            ],
            DependencyType.LIBRARY: [
                r"library\s+(\w+)", r"package\s+(\w+)",
                r"module\s+(\w+)", r"import\s+(\w+)"
            ],
            DependencyType.API: [
                r"api\s+(\w+)", r"endpoint\s+(\w+)",
                r"rest\s+api\s+(\w+)", r"graphql\s+(\w+)"
            ],
            DependencyType.CONFIGURATION: [
                r"config\s+(\w+)", r"configuration\s+(\w+)",
                r"settings\s+(\w+)", r"environment\s+(\w+)"
            ]
        }
        
        self.logger.info("LayerDependenciesExtractor initialized with L5 safety policies")
    
    async def extract_dependencies(self, request: LayerDependenciesRequest) -> DependenciesExtractionResult:
        """
        Extract layer dependencies from specification.
        
        Args:
            request: Layer dependencies extraction request with layer specification
            
        Returns:
            DependenciesExtractionResult: Structured result with extracted dependencies and metadata
            
        Raises:
            ValidationError: If dependencies extraction fails
            SafetyError: If dependencies violate safety policies
        """
        self.logger.info(f"Extracting dependencies for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            dependencies_input = {
                "layer_spec": request.layer_spec
            }
            
            is_valid, error_msg = self.safety_validator.validate_dependencies_input(dependencies_input)
            if not is_valid:
                raise SafetyError(f"Dependencies safety validation failed: {error_msg}")
            
            # Extract dependencies from layer specification
            raw_dependencies = await self._extract_raw_dependencies(request.layer_spec)
            
            # Parse and structure dependencies
            parsed_dependencies = await self._parse_dependencies(raw_dependencies)
            
            # Categorize dependencies by type
            categorized_dependencies = await self._categorize_dependencies(parsed_dependencies)
            
            # Build dependency graph
            all_dependencies = []
            for dep_list in categorized_dependencies.values():
                all_dependencies.extend(dep_list)
            
            dependency_graph = await self.build_dependency_graph(all_dependencies)
            
            # Detect circular dependencies
            circular_dependencies = await self.detect_circular_dependencies(dependency_graph)
            
            # Create extracted dependencies structure
            extracted_dependencies = ExtractedDependencies(
                layer_name=request.layer_name,
                functional_dependencies=categorized_dependencies.get(DependencyType.FUNCTIONAL, []),
                data_dependencies=categorized_dependencies.get(DependencyType.DATA, []),
                service_dependencies=categorized_dependencies.get(DependencyType.SERVICE, []),
                library_dependencies=categorized_dependencies.get(DependencyType.LIBRARY, []),
                api_dependencies=categorized_dependencies.get(DependencyType.API, []),
                configuration_dependencies=categorized_dependencies.get(DependencyType.CONFIGURATION, []),
                dependency_graph=dependency_graph,
                circular_dependencies=circular_dependencies
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_dependencies_risk_score(extracted_dependencies),
                "security_flags": self._extract_security_flags(extracted_dependencies)
            }
            
            # Generate unique dependencies ID
            dependencies_id = self._generate_dependencies_id(request, extracted_dependencies)
            
            result = DependenciesExtractionResult(
                extracted_dependencies=extracted_dependencies,
                extraction_metadata={
                    "extraction_duration_ms": len(all_dependencies) * 2,  # Rough estimate
                    "total_dependencies": len(all_dependencies),
                    "dependency_types": list(categorized_dependencies.keys()),
                    "circular_dependencies_count": len(circular_dependencies),
                    "complexity_estimate": await self._estimate_extraction_complexity(request)
                },
                safety_validation=safety_validation,
                dependencies_id=dependencies_id
            )
            
            self.logger.info(f"Successfully extracted {len(all_dependencies)} dependencies for {request.layer_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to extract layer dependencies: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback extraction in non-fail-closed mode
            return self._create_fallback_extraction(request, str(e))
    
    async def build_dependency_graph(self, dependencies: List[LayerDependency]) -> Dict[str, List[str]]:
        """Build dependency graph from extracted dependencies"""
        try:
            dependency_graph = {}
            
            for dep in dependencies:
                dep_id = dep.id
                sub_deps = dep.sub_dependencies or []
                
                # Validate sub-dependencies exist
                valid_sub_deps = []
                for sub_dep in sub_deps:
                    if any(d.id == sub_dep for d in dependencies):
                        valid_sub_deps.append(sub_dep)
                    else:
                        self.logger.warning(f"Sub-dependency {sub_dep} not found for dependency {dep_id}")
                
                dependency_graph[dep_id] = valid_sub_deps
            
            return dependency_graph
            
        except Exception as e:
            self.logger.error(f"Dependency graph building failed: {str(e)}")
            return {}
    
    async def detect_circular_dependencies(self, dependency_graph: Dict[str, List[str]]) -> List[str]:
        """Detect circular dependencies in the graph"""
        try:
            circular_deps = []
            visited = set()
            rec_stack = set()
            
            def has_cycle(node, path=None):
                if path is None:
                    path = []
                
                visited.add(node)
                rec_stack.add(node)
                path.append(node)
                
                for neighbor in dependency_graph.get(node, []):
                    if neighbor not in visited:
                        if has_cycle(neighbor, path.copy()):
                            return True
                    elif neighbor in rec_stack:
                        # Found circular dependency
                        cycle_start = path.index(neighbor)
                        cycle = path[cycle_start:] + [neighbor]
                        circular_deps.append(" -> ".join(cycle))
                        return True
                
                rec_stack.remove(node)
                return False
            
            for node in dependency_graph:
                if node not in visited:
                    has_cycle(node)
            
            return circular_deps
            
        except Exception as e:
            self.logger.error(f"Circular dependency detection failed: {str(e)}")
            return []
    
    async def _extract_raw_dependencies(self, layer_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract raw dependencies from layer specification"""
        raw_deps = []
        
        try:
            # Extract from explicit dependencies section
            explicit_deps = layer_spec.get("dependencies", [])
            if isinstance(explicit_deps, list):
                raw_deps.extend(explicit_deps)
            
            # Extract from imports section
            imports = layer_spec.get("imports", [])
            if isinstance(imports, list):
                for imp in imports:
                    raw_deps.append({
                        "name": imp,
                        "type": "library",
                        "direction": "outbound"
                    })
            
            # Extract from services section
            services = layer_spec.get("services", [])
            if isinstance(services, list):
                for service in services:
                    raw_deps.append({
                        "name": service.get("name", ""),
                        "type": "service",
                        "direction": "outbound"
                    })
            
            # Extract from APIs section
            apis = layer_spec.get("apis", [])
            if isinstance(apis, list):
                for api in apis:
                    raw_deps.append({
                        "name": api.get("name", ""),
                        "type": "api",
                        "direction": "outbound"
                    })
            
            # Extract from configuration section
            config = layer_spec.get("configuration", {})
            config_deps = config.get("dependencies", [])
            if isinstance(config_deps, list):
                for dep in config_deps:
                    raw_deps.append({
                        "name": dep,
                        "type": "configuration",
                        "direction": "outbound"
                    })
            
        except Exception as e:
            self.logger.error(f"Raw dependency extraction failed: {str(e)}")
        
        return raw_deps
    
    async def _parse_dependencies(self, raw_dependencies: List[Dict[str, Any]]) -> List[LayerDependency]:
        """Parse raw dependency data into structured dependencies"""
        parsed = []
        
        for i, raw_dep in enumerate(raw_dependencies):
            try:
                dependency = LayerDependency(
                    id=raw_dep.get("id", f"dep_{i:03d}"),
                    name=raw_dep.get("name", ""),
                    type=DependencyType(raw_dep.get("type", "functional")),
                    direction=DependencyDirection(raw_dep.get("direction", "outbound")),
                    target_layer=raw_dep.get("target_layer", ""),
                    version=raw_dep.get("version", "1.0.0"),
                    required=raw_dep.get("required", True),
                    metadata=raw_dep.get("metadata", {}),
                    sub_dependencies=raw_dep.get("sub_dependencies", [])
                )
                parsed.append(dependency)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse dependency {i}: {str(e)}")
                # Create safe fallback dependency
                fallback_dep = LayerDependency(
                    id=f"fallback_dep_{i:03d}",
                    name=f"parsing_failed_{i}",
                    type=DependencyType.FUNCTIONAL,
                    direction=DependencyDirection.OUTBOUND,
                    target_layer="unknown",
                    version="1.0.0",
                    required=False,
                    metadata={"fallback": True, "error": str(e)},
                    sub_dependencies=[]
                )
                parsed.append(fallback_dep)
        
        return parsed
    
    async def _categorize_dependencies(
        self, 
        dependencies: List[LayerDependency]
    ) -> Dict[DependencyType, List[LayerDependency]]:
        """Categorize dependencies by type"""
        categorized = {dep_type: [] for dep_type in DependencyType}
        
        for dep in dependencies:
            categorized[dep.type].append(dep)
        
        return categorized
    
    async def _estimate_extraction_complexity(self, request: LayerDependenciesRequest) -> str:
        """Estimate extraction complexity"""
        complexity_score = len(str(request.layer_spec)) // 1000
        
        # Add complexity for explicit dependencies
        explicit_deps = len(request.layer_spec.get("dependencies", []))
        complexity_score += explicit_deps // 5
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_dependencies_risk_score(self, dependencies: ExtractedDependencies) -> float:
        """Calculate risk score for the dependencies (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Count total dependencies
        all_dependencies = []
        for dep_list in [
            dependencies.functional_dependencies,
            dependencies.data_dependencies,
            dependencies.service_dependencies,
            dependencies.library_dependencies,
            dependencies.api_dependencies,
            dependencies.configuration_dependencies
        ]:
            all_dependencies.extend(dep_list)
        
        # Increase risk for large dependency sets
        if len(all_dependencies) > 50:
            risk_score += 0.2
        
        # Increase risk for circular dependencies
        if dependencies.circular_dependencies:
            risk_score += 0.3
        
        # Increase risk for service dependencies (external dependencies)
        if len(dependencies.service_dependencies) > 5:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _extract_security_flags(self, dependencies: ExtractedDependencies) -> List[str]:
        """Extract security flags from dependencies"""
        security_flags = []
        
        all_dependencies = []
        for dep_list in [
            dependencies.functional_dependencies,
            dependencies.data_dependencies,
            dependencies.service_dependencies,
            dependencies.library_dependencies,
            dependencies.api_dependencies,
            dependencies.configuration_dependencies
        ]:
            all_dependencies.extend(dep_list)
        
        # Check for external service dependencies
        if dependencies.service_dependencies:
            security_flags.append("external_service_dependencies")
        
        # Check for API dependencies
        if dependencies.api_dependencies:
            security_flags.append("api_dependencies")
        
        # Check for circular dependencies
        if dependencies.circular_dependencies:
            security_flags.append("circular_dependencies")
        
        return security_flags
    
    def _generate_dependencies_id(self, request: LayerDependenciesRequest, dependencies: ExtractedDependencies) -> str:
        """Generate unique dependencies identifier"""
        timestamp = datetime.now().isoformat()
        total_deps = sum(len(dep_list) for dep_list in [
            dependencies.functional_dependencies,
            dependencies.data_dependencies,
            dependencies.service_dependencies,
            dependencies.library_dependencies,
            dependencies.api_dependencies,
            dependencies.configuration_dependencies
        ])
        content = f"{request.layer_name}:{total_deps}:{len(dependencies.circular_dependencies)}:{timestamp}"
        return f"deps_{hash(content) % 1000000:06d}"
    
    def _create_fallback_extraction(self, request: LayerDependenciesRequest, error: str) -> DependenciesExtractionResult:
        """Create safe fallback extraction when main extraction fails"""
        fallback_dep = LayerDependency(
            id="fallback_dep_001",
            name="fallback_dependency",
            type=DependencyType.FUNCTIONAL,
            direction=DependencyDirection.OUTBOUND,
            target_layer="unknown",
            version="1.0.0",
            required=False,
            metadata={"fallback": True, "error": error},
            sub_dependencies=[]
        )
        
        fallback_dependencies = ExtractedDependencies(
            layer_name=request.layer_name,
            functional_dependencies=[fallback_dep],
            data_dependencies=[],
            service_dependencies=[],
            library_dependencies=[],
            api_dependencies=[],
            configuration_dependencies=[],
            dependency_graph={},
            circular_dependencies=[]
        )
        
        return DependenciesExtractionResult(
            extracted_dependencies=fallback_dependencies,
            extraction_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            dependencies_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when dependencies violate safety policies"""
    pass


class DependenciesExtractionError(Exception):
    """Raised for general dependencies extraction errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_dependencies_extractor(safety_policy: Optional[LayerDependenciesSafetyPolicy] = None) -> LayerDependenciesExtractor:
    """Factory function to create LayerDependenciesExtractor with optional custom safety policy"""
    return LayerDependenciesExtractor(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_dependencies_request(request: LayerDependenciesRequest) -> tuple[bool, Optional[str]]:
    """Validate layer dependencies request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not isinstance(request.layer_spec, dict):
            return False, "Layer specification must be a dictionary"
        
        if not isinstance(request.extraction_options, dict):
            return False, "Extraction options must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
