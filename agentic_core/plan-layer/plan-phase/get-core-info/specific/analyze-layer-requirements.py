"""
L1 Cognitive Planning - Layer Requirements Analysis

Implements pure planning operations for analyzing layer-specific requirements
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

class RequirementType(str, Enum):
    """Supported requirement types with L5 safety validation"""
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    DEPENDENCY = "dependency"
    INTERFACE = "interface"


class RequirementPriority(str, Enum):
    """Requirement priority levels with L5 safety enforcement"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


class LayerRequirementsSafetyPolicy(BaseModel):
    """L5 Safety policy for layer requirements analysis operations"""
    max_requirement_count: int = Field(default=200, description="Maximum requirements per layer")
    max_dependency_depth: int = Field(default=5, description="Maximum dependency chain depth")
    allowed_requirement_types: List[str] = Field(default_factory=lambda: [t.value for t in RequirementType])
    allowed_priorities: List[str] = Field(default_factory=lambda: [t.value for t in RequirementPriority])
    require_dependency_validation: bool = Field(default=True)
    prevent_circular_dependencies: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerRequirementsSafetyValidator:
    """L5 Safety validator for layer requirements analysis operations"""
    
    def __init__(self, policy: LayerRequirementsSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerRequirementsSafetyValidator")
        
        # Pre-compiled patterns for safety validation
        self._dangerous_patterns = [
            r"system\s*\(", r"exec\s*\(", r"eval\s*\(",
            r"os\.system", r"subprocess\.", r"__import__"
        ]
        self._privileged_operations = [
            "admin", "root", "sudo", "escalate", "privilege"
        ]
    
    def validate_requirements_input(self, requirements_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates requirements input against L5 safety policies"""
        try:
            # Check requirement count
            requirements = requirements_input.get("requirements", [])
            if len(requirements) > self.policy.max_requirement_count:
                error_msg = f"Too many requirements: {len(requirements)} > {self.policy.max_requirement_count}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check requirement types
            for req in requirements:
                req_type = req.get("type", "")
                if req_type not in self.policy.allowed_requirement_types:
                    error_msg = f"Prohibited requirement type: {req_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
                
                # Check priority
                priority = req.get("priority", "")
                if priority not in self.policy.allowed_priorities:
                    error_msg = f"Prohibited requirement priority: {priority}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(requirements).lower()
            for pattern in self._dangerous_patterns:
                if pattern in content_str:
                    error_msg = f"Dangerous pattern detected: {pattern}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check for privileged operations
            for privileged in self._privileged_operations:
                if privileged in content_str:
                    self.logger.warning(f"Privileged operation detected: {privileged}")
                    # Additional validation would be required in production
            
            # Validate dependency depth
            if self.policy.require_dependency_validation:
                max_depth = self._calculate_dependency_depth(requirements)
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
    
    def _calculate_dependency_depth(self, requirements: List[Dict[str, Any]]) -> int:
        """Calculate maximum dependency chain depth"""
        try:
            dependency_graph = {}
            for req in requirements:
                req_id = req.get("id", "")
                dependencies = req.get("dependencies", [])
                dependency_graph[req_id] = dependencies
            
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
class LayerRequirement:
    """Individual layer requirement specification"""
    id: str
    type: RequirementType
    priority: RequirementPriority
    description: str
    criteria: Dict[str, Any]
    dependencies: List[str]
    constraints: Dict[str, Any]
    validation_rules: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class LayerRequirementsRequest:
    """Input request for layer requirements analysis operations"""
    layer_name: str
    layer_type: str
    raw_requirements: List[Dict[str, Any]]
    context: Dict[str, Any]
    analysis_options: Dict[str, Any] = field(default_factory=dict)
    dependency_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class AnalyzedRequirements:
    """Structured representation of analyzed layer requirements"""
    layer_name: str
    functional_requirements: List[LayerRequirement]
    performance_requirements: List[LayerRequirement]
    security_requirements: List[LayerRequirement]
    compliance_requirements: List[LayerRequirement]
    dependency_requirements: List[LayerRequirement]
    interface_requirements: List[LayerRequirement]
    requirement_graph: Dict[str, List[str]]
    critical_path: List[str]


@dataclass
class RequirementsValidationResult:
    """Result of requirements analysis validation"""
    is_valid: bool
    validation_errors: List[str]
    warnings: List[str]
    compliance_score: float
    security_flags: List[str]
    dependency_issues: List[str]


@dataclass
class LayerRequirementsResult:
    """Output result from layer requirements analysis operations"""
    analyzed_requirements: AnalyzedRequirements
    validation_result: RequirementsValidationResult
    analysis_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    requirements_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerRequirementsAnalyzerInterface(ABC):
    """Abstract interface for layer requirements analysis operations"""
    
    @abstractmethod
    async def analyze_requirements(self, request: LayerRequirementsRequest) -> LayerRequirementsResult:
        """Analyze layer requirements and structure them"""
        pass
    
    @abstractmethod
    async def validate_requirement_consistency(self, requirements: AnalyzedRequirements) -> RequirementsValidationResult:
        """Validate consistency and completeness of requirements"""
        pass
    
    @abstractmethod
    async def build_dependency_graph(self, requirements: List[LayerRequirement]) -> Dict[str, List[str]]:
        """Build dependency graph from requirements"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerRequirementsAnalyzer(LayerRequirementsAnalyzerInterface):
    """
    L1 Cognitive Planning implementation for analyzing layer requirements.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerRequirementsSafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerRequirementsSafetyPolicy()
        self.safety_validator = LayerRequirementsSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Requirements analysis patterns and rules
        self._requirement_patterns = {
            RequirementType.FUNCTIONAL: [
                r"must\s+(.+)", r"shall\s+(.+)", r"will\s+(.+)",
                r"required\s+to\s+(.+)", r"needs\s+to\s+(.+)"
            ],
            RequirementType.PERFORMANCE: [
                r"response\s+time", r"throughput", r"latency",
                r"performance", r"scalability", r"capacity"
            ],
            RequirementType.SECURITY: [
                r"security", r"authentication", r"authorization",
                r"encryption", r"access\s+control", r"audit"
            ],
            RequirementType.COMPLIANCE: [
                r"compliance", r"regulation", r"standard",
                r"policy", r"governance", r"audit"
            ],
            RequirementType.DEPENDENCY: [
                r"depends\s+on", r"requires\s+(.+)", r"needs\s+(.+)",
                r"prerequisite", r"dependency"
            ],
            RequirementType.INTERFACE: [
                r"interface", r"api", r"protocol", r"format",
                r"communication", r"message", r"contract"
            ]
        }
        
        self.logger.info("LayerRequirementsAnalyzer initialized with L5 safety policies")
    
    async def analyze_requirements(self, request: LayerRequirementsRequest) -> LayerRequirementsResult:
        """
        Analyze layer requirements and structure them.
        
        Args:
            request: Layer requirements analysis request with raw requirements
            
        Returns:
            LayerRequirementsResult: Structured result with analyzed requirements and validation
            
        Raises:
            ValidationError: If requirements analysis fails
            SafetyError: If requirements violate safety policies
        """
        self.logger.info(f"Analyzing requirements for layer {request.layer_name} of type {request.layer_type}")
        
        try:
            # L5 Safety validation
            requirements_input = {
                "requirements": request.raw_requirements,
                "layer_type": request.layer_type
            }
            
            is_valid, error_msg = self.safety_validator.validate_requirements_input(requirements_input)
            if not is_valid:
                raise SafetyError(f"Requirements validation failed: {error_msg}")
            
            # Parse and structure individual requirements
            parsed_requirements = await self._parse_raw_requirements(request.raw_requirements)
            
            # Categorize requirements by type
            categorized_requirements = await self._categorize_requirements(parsed_requirements)
            
            # Build dependency graph
            all_requirements = []
            for req_list in categorized_requirements.values():
                all_requirements.extend(req_list)
            
            dependency_graph = await self.build_dependency_graph(all_requirements)
            
            # Analyze critical path
            critical_path = await self._analyze_critical_path(dependency_graph, all_requirements)
            
            # Create analyzed requirements structure
            analyzed_requirements = AnalyzedRequirements(
                layer_name=request.layer_name,
                functional_requirements=categorized_requirements.get(RequirementType.FUNCTIONAL, []),
                performance_requirements=categorized_requirements.get(RequirementType.PERFORMANCE, []),
                security_requirements=categorized_requirements.get(RequirementType.SECURITY, []),
                compliance_requirements=categorized_requirements.get(RequirementType.COMPLIANCE, []),
                dependency_requirements=categorized_requirements.get(RequirementType.DEPENDENCY, []),
                interface_requirements=categorized_requirements.get(RequirementType.INTERFACE, []),
                requirement_graph=dependency_graph,
                critical_path=critical_path
            )
            
            # Validate requirements consistency
            validation_result = await self.validate_requirement_consistency(analyzed_requirements)
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_requirements_risk_score(analyzed_requirements),
                "security_flags": validation_result.security_flags
            }
            
            # Generate unique requirements ID
            requirements_id = self._generate_requirements_id(request, analyzed_requirements)
            
            result = LayerRequirementsResult(
                analyzed_requirements=analyzed_requirements,
                validation_result=validation_result,
                analysis_metadata={
                    "analysis_duration_ms": len(request.raw_requirements) * 2,  # Rough estimate
                    "total_requirements": len(all_requirements),
                    "requirement_types": list(categorized_requirements.keys()),
                    "dependency_count": len(dependency_graph),
                    "complexity_estimate": await self._estimate_analysis_complexity(request)
                },
                safety_validation=safety_validation,
                requirements_id=requirements_id
            )
            
            self.logger.info(f"Successfully analyzed {len(all_requirements)} requirements for {request.layer_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze layer requirements: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback analysis in non-fail-closed mode
            return self._create_fallback_analysis(request, str(e))
    
    async def validate_requirement_consistency(self, requirements: AnalyzedRequirements) -> RequirementsValidationResult:
        """Validate consistency and completeness of requirements"""
        try:
            errors = []
            warnings = []
            security_flags = []
            dependency_issues = []
            
            # Check for duplicate requirement IDs
            all_requirements = []
            for req_list in [
                requirements.functional_requirements,
                requirements.performance_requirements,
                requirements.security_requirements,
                requirements.compliance_requirements,
                requirements.dependency_requirements,
                requirements.interface_requirements
            ]:
                all_requirements.extend(req_list)
            
            req_ids = [req.id for req in all_requirements]
            if len(req_ids) != len(set(req_ids)):
                duplicates = [req_id for req_id in req_ids if req_ids.count(req_id) > 1]
                errors.append(f"Duplicate requirement IDs: {duplicates}")
            
            # Validate dependency graph
            for req_id, dependencies in requirements.requirement_graph.items():
                for dep_id in dependencies:
                    if dep_id not in req_ids:
                        dependency_issues.append(f"Missing dependency: {dep_id} required by {req_id}")
            
            # Check for circular dependencies
            if self._has_circular_dependencies(requirements.requirement_graph):
                dependency_issues.append("Circular dependencies detected in requirement graph")
            
            # Security validation
            all_req_text = " ".join([req.description for req in all_requirements]).lower()
            for pattern in self._dangerous_patterns:
                if pattern in all_req_text:
                    security_flags.append(f"dangerous_content:{pattern}")
            
            # Check for privileged operations
            for privileged in self._privileged_operations:
                if privileged in all_req_text:
                    security_flags.append(f"privileged_operation:{privileged}")
            
            # Calculate compliance score
            compliance_score = 1.0
            if errors:
                compliance_score -= 0.5
            if warnings:
                compliance_score -= 0.1 * len(warnings)
            if security_flags:
                compliance_score -= 0.2 * len(security_flags)
            if dependency_issues:
                compliance_score -= 0.3 * len(dependency_issues)
            
            compliance_score = max(0.0, compliance_score)
            
            return RequirementsValidationResult(
                is_valid=len(errors) == 0 and len(dependency_issues) == 0,
                validation_errors=errors,
                warnings=warnings,
                compliance_score=compliance_score,
                security_flags=security_flags,
                dependency_issues=dependency_issues
            )
            
        except Exception as e:
            return RequirementsValidationResult(
                is_valid=False,
                validation_errors=[f"Validation error: {str(e)}"],
                warnings=[],
                compliance_score=0.0,
                security_flags=["validation_failed"],
                dependency_issues=[]
            )
    
    async def build_dependency_graph(self, requirements: List[LayerRequirement]) -> Dict[str, List[str]]:
        """Build dependency graph from requirements"""
        try:
            dependency_graph = {}
            
            for req in requirements:
                req_id = req.id
                dependencies = req.dependencies or []
                
                # Validate dependencies exist
                valid_deps = []
                for dep in dependencies:
                    if any(r.id == dep for r in requirements):
                        valid_deps.append(dep)
                    else:
                        self.logger.warning(f"Dependency {dep} not found for requirement {req_id}")
                
                dependency_graph[req_id] = valid_deps
            
            return dependency_graph
            
        except Exception as e:
            self.logger.error(f"Dependency graph building failed: {str(e)}")
            return {}
    
    async def _parse_raw_requirements(self, raw_requirements: List[Dict[str, Any]]) -> List[LayerRequirement]:
        """Parse raw requirement data into structured requirements"""
        parsed = []
        
        for i, raw_req in enumerate(raw_requirements):
            try:
                # Extract requirement type
                req_type = RequirementType(raw_req.get("type", "functional"))
                
                # Extract priority
                priority = RequirementPriority(raw_req.get("priority", "medium"))
                
                # Create structured requirement
                requirement = LayerRequirement(
                    id=raw_req.get("id", f"req_{i:03d}"),
                    type=req_type,
                    priority=priority,
                    description=raw_req.get("description", ""),
                    criteria=raw_req.get("criteria", {}),
                    dependencies=raw_req.get("dependencies", []),
                    constraints=raw_req.get("constraints", {}),
                    validation_rules=raw_req.get("validation_rules", {}),
                    metadata=raw_req.get("metadata", {})
                )
                
                parsed.append(requirement)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse requirement {i}: {str(e)}")
                # Create safe fallback requirement
                fallback_req = LayerRequirement(
                    id=f"fallback_req_{i:03d}",
                    type=RequirementType.FUNCTIONAL,
                    priority=RequirementPriority.LOW,
                    description=f"Parsing failed: {str(e)}",
                    criteria={},
                    dependencies=[],
                    constraints={},
                    validation_rules={},
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_req)
        
        return parsed
    
    async def _categorize_requirements(
        self, 
        requirements: List[LayerRequirement]
    ) -> Dict[RequirementType, List[LayerRequirement]]:
        """Categorize requirements by type"""
        categorized = {req_type: [] for req_type in RequirementType}
        
        for req in requirements:
            categorized[req.type].append(req)
        
        return categorized
    
    async def _analyze_critical_path(
        self, 
        dependency_graph: Dict[str, List[str]], 
        requirements: List[LayerRequirement]
    ) -> List[str]:
        """Analyze critical path through dependency graph"""
        try:
            # Simple critical path analysis - find longest dependency chain
            def get_longest_path(node, visited=None):
                if visited is None:
                    visited = set()
                
                if node in visited:
                    return []  # Circular dependency
                
                visited.add(node)
                deps = dependency_graph.get(node, [])
                
                if not deps:
                    return [node]
                
                longest_path = []
                for dep in deps:
                    path = get_longest_path(dep, visited.copy())
                    if len(path) > len(longest_path):
                        longest_path = path
                
                return [node] + longest_path
            
            critical_path = []
            for node in dependency_graph:
                path = get_longest_path(node)
                if len(path) > len(critical_path):
                    critical_path = path
            
            return critical_path
            
        except Exception as e:
            self.logger.error(f"Critical path analysis failed: {str(e)}")
            return []
    
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
    
    async def _estimate_analysis_complexity(self, request: LayerRequirementsRequest) -> str:
        """Estimate analysis complexity"""
        complexity_score = len(request.raw_requirements) // 10
        
        # Add complexity for dependencies
        total_deps = sum(len(req.get("dependencies", [])) for req in request.raw_requirements)
        complexity_score += total_deps // 5
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_requirements_risk_score(self, requirements: AnalyzedRequirements) -> float:
        """Calculate risk score for the requirements (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Count total requirements
        all_requirements = []
        for req_list in [
            requirements.functional_requirements,
            requirements.performance_requirements,
            requirements.security_requirements,
            requirements.compliance_requirements,
            requirements.dependency_requirements,
            requirements.interface_requirements
        ]:
            all_requirements.extend(req_list)
        
        # Increase risk for large requirement sets
        if len(all_requirements) > 100:
            risk_score += 0.2
        
        # Increase risk for complex dependencies
        total_deps = sum(len(deps) for deps in requirements.requirement_graph.values())
        if total_deps > 50:
            risk_score += 0.2
        
        # Increase risk for security requirements (they're critical)
        if len(requirements.security_requirements) > 10:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _generate_requirements_id(self, request: LayerRequirementsRequest, requirements: AnalyzedRequirements) -> str:
        """Generate unique requirements identifier"""
        timestamp = datetime.now().isoformat()
        total_reqs = sum(len(req_list) for req_list in [
            requirements.functional_requirements,
            requirements.performance_requirements,
            requirements.security_requirements,
            requirements.compliance_requirements,
            requirements.dependency_requirements,
            requirements.interface_requirements
        ])
        content = f"{request.layer_name}:{request.layer_type}:{total_reqs}:{timestamp}"
        return f"reqs_{hash(content) % 1000000:06d}"
    
    def _create_fallback_analysis(self, request: LayerRequirementsRequest, error: str) -> LayerRequirementsResult:
        """Create safe fallback analysis when main analysis fails"""
        fallback_req = LayerRequirement(
            id="fallback_req_001",
            type=RequirementType.FUNCTIONAL,
            priority=RequirementPriority.LOW,
            description="Fallback requirement due to analysis failure",
            criteria={},
            dependencies=[],
            constraints={},
            validation_rules={},
            metadata={"fallback": True, "error": error}
        )
        
        fallback_requirements = AnalyzedRequirements(
            layer_name=request.layer_name,
            functional_requirements=[fallback_req],
            performance_requirements=[],
            security_requirements=[],
            compliance_requirements=[],
            dependency_requirements=[],
            interface_requirements=[],
            requirement_graph={},
            critical_path=[]
        )
        
        fallback_validation = RequirementsValidationResult(
            is_valid=True,
            validation_errors=[],
            warnings=["Using fallback requirements analysis"],
            compliance_score=0.5,
            security_flags=["fallback_mode"],
            dependency_issues=[]
        )
        
        return LayerRequirementsResult(
            analyzed_requirements=fallback_requirements,
            validation_result=fallback_validation,
            analysis_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            requirements_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when requirements violate safety policies"""
    pass


class RequirementsAnalysisError(Exception):
    """Raised for general requirements analysis errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_requirements_analyzer(safety_policy: Optional[LayerRequirementsSafetyPolicy] = None) -> LayerRequirementsAnalyzer:
    """Factory function to create LayerRequirementsAnalyzer with optional custom safety policy"""
    return LayerRequirementsAnalyzer(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_requirements_request(request: LayerRequirementsRequest) -> tuple[bool, Optional[str]]:
    """Validate layer requirements request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not request.layer_type or not request.layer_type.strip():
            return False, "Layer type cannot be empty"
        
        if not isinstance(request.raw_requirements, list):
            return False, "Raw requirements must be a list"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
