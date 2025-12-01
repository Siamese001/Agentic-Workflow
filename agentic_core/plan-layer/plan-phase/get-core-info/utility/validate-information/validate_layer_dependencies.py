"""
L1 Cognitive Planning - Layer Dependencies Validation

Implements pure planning operations for validating layer dependencies
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

class DependencyValidationType(str, Enum):
    """Supported dependency validation types with L5 safety validation"""
    STRUCTURAL = "structural"
    VERSION = "version"
    COMPATIBILITY = "compatibility"
    SECURITY = "security"
    CIRCULAR = "circular"
    TRANSITIVE = "transitive"


class ValidationSeverity(str, Enum):
    """Validation severity levels with L5 safety enforcement"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class LayerDependenciesSafetyPolicy(BaseModel):
    """L5 Safety policy for layer dependencies validation operations"""
    max_dependency_count: int = Field(default=100, description="Maximum dependencies per layer")
    max_validation_depth: int = Field(default=10, description="Maximum validation nesting depth")
    allowed_validation_types: List[str] = Field(default_factory=lambda: [t.value for t in DependencyValidationType])
    allowed_severities: List[str] = Field(default_factory=lambda: [t.value for t in ValidationSeverity])
    require_circular_dependency_check: bool = Field(default=True)
    prevent_dependency_injection: bool = Field(default=True)
    sanitize_dependency_data: bool = Field(default=True)
    safety_checks_enabled: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class LayerDependenciesSafetyValidator:
    """L5 Safety validator for layer dependencies validation operations"""
    
    def __init__(self, policy: LayerDependenciesSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.LayerDependenciesSafetyValidator")
        
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
    
    def validate_dependencies_input(self, dependencies_input: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validates dependencies input against L5 safety policies"""
        try:
            # Check dependency count
            dependencies = dependencies_input.get("dependencies", [])
            if len(dependencies) > self.policy.max_dependency_count:
                error_msg = f"Too many dependencies: {len(dependencies)} > {self.policy.max_dependency_count}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check validation types
            validation_rules = dependencies_input.get("validation_rules", [])
            for rule in validation_rules:
                rule_type = rule.get("type", "")
                if rule_type not in self.policy.allowed_validation_types:
                    error_msg = f"Prohibited validation type: {rule_type}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check validation depth
            max_depth = self._calculate_dependencies_depth(dependencies)
            if max_depth > self.policy.max_validation_depth:
                error_msg = f"Dependencies nesting too deep: {max_depth} > {self.policy.max_validation_depth}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check for dangerous patterns
            content_str = str(dependencies).lower()
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
    
    def _calculate_dependencies_depth(self, dependencies: List[Dict[str, Any]]) -> int:
        """Calculate maximum nesting depth of dependencies"""
        try:
            def get_depth(dep, current_depth=0):
                if current_depth > self.policy.max_validation_depth:
                    return current_depth
                
                sub_deps = dep.get("sub_dependencies", [])
                if not sub_deps:
                    return current_depth + 1
                
                max_sub_depth = 0
                for sub_dep in sub_deps:
                    sub_depth = get_depth(sub_dep, current_depth + 1)
                    max_sub_depth = max(max_sub_depth, sub_depth)
                
                return max_sub_depth
            
            return max((get_depth(dep) for dep in dependencies), default=0)
            
        except Exception as e:
            self.logger.error(f"Dependencies depth calculation failed: {str(e)}")
            return 0


# ============================================================================
# L1 COGNITIVE PLANNING INTERFACES
# ============================================================================

@dataclass
class DependencyValidationRule:
    """Individual dependency validation rule specification"""
    id: str
    validation_type: DependencyValidationType
    severity: ValidationSeverity
    criteria: Dict[str, Any]
    error_message: str
    metadata: Dict[str, Any]


@dataclass
class LayerDependenciesValidationRequest:
    """Input request for layer dependencies validation operations"""
    layer_name: str
    dependencies: List[Dict[str, Any]]
    validation_rules: List[Dict[str, Any]]
    validation_options: Dict[str, Any]
    context: Dict[str, Any]
    dependency_constraints: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"


@dataclass
class DependencyValidationError:
    """Individual dependency validation error"""
    dependency_id: str
    rule_id: str
    validation_type: DependencyValidationType
    error_category: str
    error_message: str
    actual_value: Any
    expected_value: Any
    severity: ValidationSeverity


@dataclass
class DependenciesValidationResult:
    """Result of layer dependencies validation"""
    is_valid: bool
    validation_errors: List[DependencyValidationError]
    validation_warnings: List[DependencyValidationError]
    circular_dependencies: List[str]
    missing_dependencies: List[str]
    validation_summary: Dict[str, Any]
    security_flags: List[str]


@dataclass
class LayerDependenciesValidationResult:
    """Output result from layer dependencies validation operations"""
    validation_result: DependenciesValidationResult
    validated_dependencies: List[Dict[str, Any]]
    validation_metadata: Dict[str, Any]
    safety_validation: Dict[str, Any]
    dependencies_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class LayerDependenciesValidatorInterface(ABC):
    """Abstract interface for layer dependencies validation operations"""
    
    @abstractmethod
    async def validate_dependencies(self, request: LayerDependenciesValidationRequest) -> LayerDependenciesValidationResult:
        """Validate layer dependencies against rules and criteria"""
        pass
    
    @abstractmethod
    async def detect_circular_dependencies(self, dependencies: List[Dict[str, Any]]) -> List[str]:
        """Detect circular dependencies in the dependency graph"""
        pass
    
    @abstractmethod
    async def validate_dependency_versions(self, dependencies: List[Dict[str, Any]]) -> List[DependencyValidationError]:
        """Validate dependency versions and constraints"""
        pass


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerDependenciesValidator(LayerDependenciesValidatorInterface):
    """
    L1 Cognitive Planning implementation for validating layer dependencies.
    
    Provides pure planning operations without execution, following L5 safety
    principles and comprehensive logging for fail-closed architecture.
    """
    
    def __init__(self, safety_policy: Optional[LayerDependenciesSafetyPolicy] = None):
        self.safety_policy = safety_policy or LayerDependenciesSafetyPolicy()
        self.safety_validator = LayerDependenciesSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Dependency validation patterns and rules
        self._validation_patterns = {
            DependencyValidationType.STRUCTURAL: {
                "required_fields": self._validate_required_fields,
                "field_types": self._validate_field_types,
                "dependency_format": self._validate_dependency_format
            },
            DependencyValidationType.VERSION: {
                "semantic_versioning": self._validate_semantic_versioning,
                "version_constraints": self._validate_version_constraints,
                "version_compatibility": self._validate_version_compatibility
            },
            DependencyValidationType.COMPATIBILITY: {
                "interface_compatibility": self._validate_interface_compatibility,
                "protocol_compatibility": self._validate_protocol_compatibility,
                "data_format_compatibility": self._validate_data_format_compatibility
            },
            DependencyValidationType.SECURITY: {
                "trusted_sources": self._validate_trusted_sources,
                "security_policies": self._validate_security_policies,
                "vulnerability_check": self._validate_vulnerability_check
            },
            DependencyValidationType.CIRCULAR: {
                "circular_detection": self._validate_circular_detection,
                "cycle_analysis": self._validate_cycle_analysis
            },
            DependencyValidationType.TRANSITIVE: {
                "transitive_analysis": self._validate_transitive_analysis,
                "dependency_depth": self._validate_dependency_depth
            }
        }
        
        self.logger.info("LayerDependenciesValidator initialized with L5 safety policies")
    
    async def validate_dependencies(self, request: LayerDependenciesValidationRequest) -> LayerDependenciesValidationResult:
        """
        Validate layer dependencies against rules and criteria.
        
        Args:
            request: Layer dependencies validation request with dependencies and validation rules
            
        Returns:
            LayerDependenciesValidationResult: Structured result with validation outcome and details
            
        Raises:
            ValidationError: If dependencies validation fails
            SafetyError: If dependencies violate safety policies
        """
        self.logger.info(f"Validating dependencies for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            dependencies_input = {
                "dependencies": request.dependencies,
                "validation_rules": request.validation_rules
            }
            
            is_valid, error_msg = self.safety_validator.validate_dependencies_input(dependencies_input)
            if not is_valid:
                raise SafetyError(f"Dependencies safety validation failed: {error_msg}")
            
            # Sanitize dependencies if required
            sanitized_dependencies = request.dependencies
            if self.safety_policy.sanitize_dependency_data:
                sanitized_dependencies = await self._sanitize_dependencies(request.dependencies)
            
            # Parse validation rules
            parsed_rules = await self._parse_validation_rules(request.validation_rules)
            
            # Execute validation rules
            validation_errors = []
            for rule in parsed_rules:
                rule_errors = await self._execute_validation_rule(sanitized_dependencies, rule)
                validation_errors.extend(rule_errors)
            
            # Detect circular dependencies
            circular_dependencies = await self.detect_circular_dependencies(sanitized_dependencies)
            
            # Check for missing dependencies
            missing_dependencies = await self._detect_missing_dependencies(sanitized_dependencies)
            
            # Separate errors and warnings based on severity
            error_list = [e for e in validation_errors if e.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]]
            warning_list = [e for e in validation_errors if e.severity in [ValidationSeverity.WARNING, ValidationSeverity.INFO]]
            
            # Determine overall validity
            is_dependencies_valid = len(error_list) == 0 and len(circular_dependencies) == 0
            
            # Generate validation summary
            validation_summary = await self._generate_validation_summary(
                request.layer_name,
                validation_errors,
                circular_dependencies,
                missing_dependencies
            )
            
            # Extract security flags
            security_flags = self._extract_security_flags(validation_errors)
            
            # Create validation result
            validation_result = DependenciesValidationResult(
                is_valid=is_dependencies_valid,
                validation_errors=error_list,
                validation_warnings=warning_list,
                circular_dependencies=circular_dependencies,
                missing_dependencies=missing_dependencies,
                validation_summary=validation_summary,
                security_flags=security_flags
            )
            
            # Generate safety validation metadata
            safety_validation = {
                "validated_at": datetime.now().isoformat(),
                "safety_level": request.safety_level,
                "risk_score": self._calculate_dependencies_risk_score(validation_result),
                "security_flags": security_flags
            }
            
            # Generate unique dependencies ID
            dependencies_id = self._generate_dependencies_id(request, validation_result)
            
            result = LayerDependenciesValidationResult(
                validation_result=validation_result,
                validated_dependencies=sanitized_dependencies,
                validation_metadata={
                    "layer_name": request.layer_name,
                    "rules_applied": len(parsed_rules),
                    "total_dependencies": len(sanitized_dependencies),
                    "circular_dependencies_count": len(circular_dependencies),
                    "complexity_estimate": await self._estimate_validation_complexity(request)
                },
                safety_validation=safety_validation,
                dependencies_id=dependencies_id
            )
            
            self.logger.info(f"Successfully validated dependencies for {request.layer_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to validate layer dependencies: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback validation in non-fail-closed mode
            return self._create_fallback_validation(request, str(e))
    
    async def detect_circular_dependencies(self, dependencies: List[Dict[str, Any]]) -> List[str]:
        """Detect circular dependencies in the dependency graph"""
        try:
            # Build dependency graph
            dependency_graph = {}
            for dep in dependencies:
                dep_id = dep.get("id", "")
                sub_deps = dep.get("sub_dependencies", [])
                dependency_graph[dep_id] = sub_deps
            
            # Detect cycles using DFS
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
    
    async def validate_dependency_versions(self, dependencies: List[Dict[str, Any]]) -> List[DependencyValidationError]:
        """Validate dependency versions and constraints"""
        errors = []
        
        for dep in dependencies:
            try:
                dep_id = dep.get("id", "")
                version = dep.get("version", "")
                version_constraint = dep.get("version_constraint", "")
                
                # Validate semantic versioning
                if not self._is_valid_semver(version):
                    error = DependencyValidationError(
                        dependency_id=dep_id,
                        rule_id="version_validation",
                        validation_type=DependencyValidationType.VERSION,
                        error_category="invalid_version",
                        error_message=f"Invalid semantic version: {version}",
                        actual_value=version,
                        expected_value="semantic version (x.y.z)",
                        severity=ValidationSeverity.ERROR
                    )
                    errors.append(error)
                
                # Validate version constraint
                if version_constraint and not self._is_valid_version_constraint(version_constraint):
                    error = DependencyValidationError(
                        dependency_id=dep_id,
                        rule_id="version_constraint_validation",
                        validation_type=DependencyValidationType.VERSION,
                        error_category="invalid_constraint",
                        error_message=f"Invalid version constraint: {version_constraint}",
                        actual_value=version_constraint,
                        expected_value="valid constraint (>=, <=, ~, ^)",
                        severity=ValidationSeverity.WARNING
                    )
                    errors.append(error)
                
            except Exception as e:
                self.logger.error(f"Dependency version validation failed for {dep.get('id', 'unknown')}: {str(e)}")
                error = DependencyValidationError(
                    dependency_id=dep.get("id", "unknown"),
                    rule_id="version_validation_error",
                    validation_type=DependencyValidationType.VERSION,
                    error_category="validation_error",
                    error_message=f"Version validation error: {str(e)}",
                    actual_value=str(e),
                    expected_value="success",
                    severity=ValidationSeverity.ERROR
                )
                errors.append(error)
        
        return errors
    
    async def _parse_validation_rules(self, raw_rules: List[Dict[str, Any]]) -> List[DependencyValidationRule]:
        """Parse raw validation rule data into structured rules"""
        parsed = []
        
        for i, raw_rule in enumerate(raw_rules):
            try:
                rule = DependencyValidationRule(
                    id=raw_rule.get("id", f"rule_{i:03d}"),
                    validation_type=DependencyValidationType(raw_rule.get("validation_type", "structural")),
                    severity=ValidationSeverity(raw_rule.get("severity", "error")),
                    criteria=raw_rule.get("criteria", {}),
                    error_message=raw_rule.get("error_message", "Dependency validation failed"),
                    metadata=raw_rule.get("metadata", {})
                )
                parsed.append(rule)
                
            except Exception as e:
                self.logger.warning(f"Failed to parse validation rule {i}: {str(e)}")
                # Create safe fallback rule
                fallback_rule = DependencyValidationRule(
                    id=f"fallback_rule_{i:03d}",
                    validation_type=DependencyValidationType.STRUCTURAL,
                    severity=ValidationSeverity.WARNING,
                    criteria={},
                    error_message=f"Parsing failed: {str(e)}",
                    metadata={"fallback": True, "error": str(e)}
                )
                parsed.append(fallback_rule)
        
        return parsed
    
    async def _execute_validation_rule(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Execute individual validation rule"""
        errors = []
        
        try:
            # Get validation function for rule type
            type_patterns = self._validation_patterns.get(rule.validation_type, {})
            validation_func = type_patterns.get(rule.criteria.get("validation_function", ""))
            
            if validation_func:
                # Apply validation function
                rule_errors = await validation_func(dependencies, rule)
                errors.extend(rule_errors)
            else:
                # Unknown validation function
                error = DependencyValidationError(
                    dependency_id="multiple",
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="unknown_validation",
                    error_message=f"Unknown validation function: {rule.criteria.get('validation_function')}",
                    actual_value=None,
                    expected_value=None,
                    severity=ValidationSeverity.WARNING
                )
                errors.append(error)
                
        except Exception as e:
            self.logger.error(f"Failed to execute validation rule {rule.id}: {str(e)}")
            error = DependencyValidationError(
                dependency_id="multiple",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="rule_execution_error",
                error_message=f"Rule execution failed: {str(e)}",
                actual_value=str(e),
                expected_value="success",
                severity=ValidationSeverity.ERROR
            )
            errors.append(error)
        
        return errors
    
    async def _sanitize_dependencies(self, dependencies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sanitize dependency content for safety"""
        sanitized = []
        
        for dep in dependencies:
            sanitized_dep = dep.copy()
            
            # Remove dangerous content from string fields
            for key, value in sanitized_dep.items():
                if isinstance(value, str):
                    # Remove script tags and dangerous content
                    sanitized_value = value.replace("<script", "").replace("</script>", "")
                    sanitized_dep[key] = sanitized_value
            
            sanitized.append(sanitized_dep)
        
        return sanitized
    
    async def _detect_missing_dependencies(self, dependencies: List[Dict[str, Any]]) -> List[str]:
        """Detect missing dependencies"""
        missing = []
        
        try:
            # Get all dependency IDs
            all_dep_ids = {dep.get("id", "") for dep in dependencies}
            all_dep_ids.discard("")  # Remove empty IDs
            
            # Check sub-dependencies
            for dep in dependencies:
                sub_deps = dep.get("sub_dependencies", [])
                for sub_dep in sub_deps:
                    if sub_dep not in all_dep_ids:
                        missing.append(sub_dep)
            
        except Exception as e:
            self.logger.error(f"Missing dependencies detection failed: {str(e)}")
        
        return list(set(missing))  # Remove duplicates
    
    # Validation function implementations
    async def _validate_required_fields(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate required fields in dependencies"""
        errors = []
        required_fields = rule.criteria.get("required_fields", ["id", "name", "version"])
        
        for dep in dependencies:
            dep_id = dep.get("id", "unknown")
            for field in required_fields:
                if field not in dep or dep[field] is None:
                    error = DependencyValidationError(
                        dependency_id=dep_id,
                        rule_id=rule.id,
                        validation_type=rule.validation_type,
                        error_category="missing_field",
                        error_message=f"Required field '{field}' is missing",
                        actual_value=None,
                        expected_value="present",
                        severity=rule.severity
                    )
                    errors.append(error)
        
        return errors
    
    async def _validate_field_types(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate field types in dependencies"""
        errors = []
        field_types = rule.criteria.get("field_types", {})
        
        for dep in dependencies:
            dep_id = dep.get("id", "unknown")
            for field, expected_type in field_types.items():
                if field in dep:
                    value = dep[field]
                    type_mapping = {
                        "string": str,
                        "integer": int,
                        "number": (int, float),
                        "boolean": bool,
                        "array": list,
                        "object": dict
                    }
                    
                    expected_python_type = type_mapping.get(expected_type)
                    if expected_python_type and not isinstance(value, expected_python_type):
                        error = DependencyValidationError(
                            dependency_id=dep_id,
                            rule_id=rule.id,
                            validation_type=rule.validation_type,
                            error_category="type_mismatch",
                            error_message=f"Field '{field}' should be of type {expected_type}",
                            actual_value=type(value).__name__,
                            expected_value=expected_type,
                            severity=rule.severity
                        )
                        errors.append(error)
        
        return errors
    
    async def _validate_dependency_format(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate dependency format"""
        errors = []
        
        for dep in dependencies:
            dep_id = dep.get("id", "unknown")
            
            # Check ID format
            dep_id_value = dep.get("id", "")
            if not dep_id_value or not isinstance(dep_id_value, str):
                error = DependencyValidationError(
                    dependency_id=dep_id,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="invalid_format",
                    error_message="Dependency ID must be a non-empty string",
                    actual_value=dep_id_value,
                    expected_value="non-empty string",
                    severity=rule.severity
                )
                errors.append(error)
        
        return errors
    
    async def _validate_semantic_versioning(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate semantic versioning"""
        errors = []
        
        for dep in dependencies:
            dep_id = dep.get("id", "unknown")
            version = dep.get("version", "")
            
            if not self._is_valid_semver(version):
                error = DependencyValidationError(
                    dependency_id=dep_id,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="invalid_semver",
                    error_message=f"Invalid semantic version: {version}",
                    actual_value=version,
                    expected_value="semantic version (x.y.z)",
                    severity=rule.severity
                )
                errors.append(error)
        
        return errors
    
    async def _validate_version_constraints(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate version constraints"""
        errors = []
        
        for dep in dependencies:
            dep_id = dep.get("id", "unknown")
            constraint = dep.get("version_constraint", "")
            
            if constraint and not self._is_valid_version_constraint(constraint):
                error = DependencyValidationError(
                    dependency_id=dep_id,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="invalid_constraint",
                    error_message=f"Invalid version constraint: {constraint}",
                    actual_value=constraint,
                    expected_value="valid constraint (>=, <=, ~, ^)",
                    severity=rule.severity
                )
                errors.append(error)
        
        return errors
    
    async def _validate_version_compatibility(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate version compatibility"""
        errors = []
        
        # Check if dependencies list is provided
        if not dependencies:
            errors.append(DependencyValidationError(
                dependency_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_dependencies_provided",
                error_message="No dependencies provided for version compatibility validation",
                actual_value=None,
                expected_value="list of dependencies",
                severity="error"
            ))
            return errors
        
        # Validate version compatibility across dependencies
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                errors.append(DependencyValidationError(
                    dependency_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_dependency_format",
                    error_message="Dependency must be a dictionary",
                    actual_value=dependency,
                    expected_value="dependency dictionary",
                    severity="error"
                ))
                continue
            
            dependency_id = dependency.get("id", "unknown")
            version = dependency.get("version", "")
            version_constraint = dependency.get("version_constraint", "")
            
            if not version:
                errors.append(DependencyValidationError(
                    dependency_id=dependency_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="missing_version",
                    error_message="Dependency version is missing",
                    actual_value=version,
                    expected_value="semantic version (e.g., 1.0.0)",
                    severity="warning"
                ))
            else:
                # Validate semantic version format
                import re
                semver_pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9\-\.]+)?(\+[a-zA-Z0-9\-\.]+)?$'
                if not re.match(semver_pattern, version):
                    errors.append(DependencyValidationError(
                        dependency_id=dependency_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="invalid_version_format",
                        error_message=f"Dependency version '{version}' is not in semantic version format",
                        actual_value=version,
                        expected_value="semantic version (e.g., 1.0.0)",
                        severity="warning"
                    ))
            
            # Validate version constraint format
            if version_constraint:
                valid_operators = ["==", "!=", ">=", "<=", ">", "<", "~=", "^"]
                has_valid_operator = any(op in version_constraint for op in valid_operators)
                
                if not has_valid_operator and not re.match(semver_pattern, version_constraint):
                    errors.append(DependencyValidationError(
                        dependency_id=dependency_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="invalid_version_constraint",
                        error_message=f"Invalid version constraint: {version_constraint}",
                        actual_value=version_constraint,
                        expected_value="valid version constraint (e.g., >=1.0.0, ^2.3.0)",
                        severity="warning"
                    ))
            
            # Check for known incompatible versions
            dependency_name = dependency.get("name", "")
            known_incompatible = {
                "python": ["2.7", "3.0", "3.1", "3.2", "3.3"],
                "node": ["< 14.0.0"],
                "npm": ["< 6.0.0"]
            }
            
            for name, incompatible_versions in known_incompatible.items():
                if name.lower() in dependency_name.lower():
                    for incompatible in incompatible_versions:
                        if incompatible.startswith("<"):
                            # Handle version ranges
                            if version < incompatible.replace("< ", ""):
                                errors.append(DependencyValidationError(
                                    dependency_id=dependency_id,
                                    rule_id=rule.rule_id,
                                    validation_type=rule.validation_type,
                                    error_category="incompatible_version",
                                    error_message=f"Dependency '{dependency_name}' version {version} is incompatible",
                                    actual_value=version,
                                    expected_value=f"> {incompatible.replace('< ', '')}",
                                    severity="error"
                                ))
                        elif incompatible in version:
                            errors.append(DependencyValidationError(
                                dependency_id=dependency_id,
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="incompatible_version",
                                error_message=f"Dependency '{dependency_name}' version {version} is known to be incompatible",
                                actual_value=version,
                                expected_value="compatible version",
                                severity="error"
                            ))
        
        return errors
    
    async def _validate_interface_compatibility(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate interface compatibility"""
        errors = []
        
        # Check if dependencies list is provided
        if not dependencies:
            errors.append(DependencyValidationError(
                dependency_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_dependencies_provided",
                error_message="No dependencies provided for interface compatibility validation",
                actual_value=None,
                expected_value="list of dependencies",
                severity="error"
            ))
            return errors
        
        # Validate interface compatibility across dependencies
        dependency_interfaces = {}
        
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                errors.append(DependencyValidationError(
                    dependency_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_dependency_format",
                    error_message="Dependency must be a dictionary",
                    actual_value=dependency,
                    expected_value="dependency dictionary",
                    severity="error"
                ))
                continue
            
            dependency_id = dependency.get("id", "unknown")
            interfaces = dependency.get("interfaces", [])
            
            # Track interfaces for compatibility checking
            for interface in interfaces:
                if isinstance(interface, dict):
                    interface_name = interface.get("name", "")
                    interface_version = interface.get("version", "")
                    interface_type = interface.get("type", "")
                    
                    if interface_name:
                        if interface_name not in dependency_interfaces:
                            dependency_interfaces[interface_name] = []
                        dependency_interfaces[interface_name].append({
                            "dependency_id": dependency_id,
                            "version": interface_version,
                            "type": interface_type,
                            "interface": interface
                        })
        
        # Check for interface conflicts across dependencies
        for interface_name, implementations in dependency_interfaces.items():
            if len(implementations) > 1:
                # Check for version conflicts
                versions = [impl["version"] for impl in implementations if impl["version"]]
                if len(set(versions)) > 1:
                    errors.append(DependencyValidationError(
                        dependency_id="multiple",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="interface_version_conflict",
                        error_message=f"Interface '{interface_name}' has conflicting versions across dependencies: {set(versions)}",
                        actual_value=versions,
                        expected_value="consistent version across all dependencies",
                        severity="error"
                    ))
                
                # Check for type conflicts
                types = [impl["type"] for impl in implementations if impl["type"]]
                if len(set(types)) > 1:
                    errors.append(DependencyValidationError(
                        dependency_id="multiple",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="interface_type_conflict",
                        error_message=f"Interface '{interface_name}' has conflicting types across dependencies: {set(types)}",
                        actual_value=types,
                        expected_value="consistent type across all dependencies",
                        severity="error"
                    ))
                
                # Check for signature compatibility
                signatures = []
                for impl in implementations:
                    interface = impl["interface"]
                    methods = interface.get("methods", [])
                    signature = set()
                    for method in methods:
                        if isinstance(method, dict):
                            method_name = method.get("name", "")
                            params = tuple(sorted([p.get("name", "") for p in method.get("parameters", [])]))
                            signature.add((method_name, params))
                    signatures.append(signature)
                
                # Check if all signatures are compatible
                if len(signatures) > 1:
                    base_signature = signatures[0]
                    for i, signature in enumerate(signatures[1:], 1):
                        if signature != base_signature:
                            errors.append(DependencyValidationError(
                                dependency_id="multiple",
                                rule_id=rule.rule_id,
                                validation_type=rule.validation_type,
                                error_category="interface_signature_incompatible",
                                error_message=f"Interface '{interface_name}' has incompatible method signatures across dependencies",
                                actual_value=f"signature {i}: {signature}",
                                expected_value=f"base signature: {base_signature}",
                                severity="error"
                            ))
        
        return errors
    
    async def _validate_protocol_compatibility(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate protocol compatibility"""
        errors = []
        
        # Check if dependencies list is provided
        if not dependencies:
            errors.append(DependencyValidationError(
                dependency_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_dependencies_provided",
                error_message="No dependencies provided for protocol compatibility validation",
                actual_value=None,
                expected_value="list of dependencies",
                severity="error"
            ))
            return errors
        
        # Validate protocol compatibility across dependencies
        dependency_protocols = {}
        
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                errors.append(DependencyValidationError(
                    dependency_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_dependency_format",
                    error_message="Dependency must be a dictionary",
                    actual_value=dependency,
                    expected_value="dependency dictionary",
                    severity="error"
                ))
                continue
            
            dependency_id = dependency.get("id", "unknown")
            protocol = dependency.get("protocol", "")
            protocol_version = dependency.get("protocol_version", "")
            
            # Track protocols for compatibility checking
            if protocol:
                if protocol not in dependency_protocols:
                    dependency_protocols[protocol] = []
                dependency_protocols[protocol].append({
                    "dependency_id": dependency_id,
                    "version": protocol_version,
                    "protocol": protocol
                })
        
        # Check for protocol conflicts
        for protocol, implementations in dependency_protocols.items():
            if len(implementations) > 1:
                # Check for version conflicts within same protocol
                versions = [impl["version"] for impl in implementations if impl["version"]]
                if len(set(versions)) > 1:
                    errors.append(DependencyValidationError(
                        dependency_id="multiple",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="protocol_version_conflict",
                        error_message=f"Protocol '{protocol}' has conflicting versions across dependencies: {set(versions)}",
                        actual_value=versions,
                        expected_value="consistent protocol version across all dependencies",
                        severity="error"
                    ))
        
        # Validate individual dependency protocols
        supported_protocols = ["http", "https", "grpc", "websocket", "tcp", "udp", "mqtt", "amqp"]
        
        for dependency in dependencies:
            dependency_id = dependency.get("id", "unknown")
            protocol = dependency.get("protocol", "")
            
            if not protocol:
                errors.append(DependencyValidationError(
                    dependency_id=dependency_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="missing_protocol",
                    error_message="Dependency protocol is not specified",
                    actual_value=protocol,
                    expected_value="supported protocol",
                    severity="warning"
                ))
            elif protocol.lower() not in supported_protocols:
                errors.append(DependencyValidationError(
                    dependency_id=dependency_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="unsupported_protocol",
                    error_message=f"Unsupported protocol: {protocol}",
                    actual_value=protocol,
                    expected_value="one of: " + ", ".join(supported_protocols),
                    severity="warning"
                ))
            
            # Validate protocol-specific requirements
            if protocol.lower() == "https":
                ssl_config = dependency.get("ssl_config", {})
                if not ssl_config:
                    errors.append(DependencyValidationError(
                        dependency_id=dependency_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="missing_ssl_config",
                        error_message="HTTPS protocol requires SSL configuration",
                        actual_value=ssl_config,
                        expected_value="SSL configuration",
                        severity="error"
                    ))
            
            elif protocol.lower() == "grpc":
                grpc_config = dependency.get("grpc_config", {})
                if not grpc_config:
                    errors.append(DependencyValidationError(
                        dependency_id=dependency_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="missing_grpc_config",
                        error_message="gRPC protocol requires gRPC configuration",
                        actual_value=grpc_config,
                        expected_value="gRPC configuration",
                        severity="warning"
                    ))
        
        return errors
    
    async def _validate_data_format_compatibility(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate data format compatibility"""
        errors = []
        
        # Check if dependencies list is provided
        if not dependencies:
            errors.append(DependencyValidationError(
                dependency_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_dependencies_provided",
                error_message="No dependencies provided for data format compatibility validation",
                actual_value=None,
                expected_value="list of dependencies",
                severity="error"
            ))
            return errors
        
        # Validate data format compatibility across dependencies
        dependency_formats = {}
        
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                errors.append(DependencyValidationError(
                    dependency_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_dependency_format",
                    error_message="Dependency must be a dictionary",
                    actual_value=dependency,
                    expected_value="dependency dictionary",
                    severity="error"
                ))
                continue
            
            dependency_id = dependency.get("id", "unknown")
            data_format = dependency.get("data_format", "")
            format_version = dependency.get("format_version", "")
            
            # Track data formats for compatibility checking
            if data_format:
                if data_format not in dependency_formats:
                    dependency_formats[data_format] = []
                dependency_formats[data_format].append({
                    "dependency_id": dependency_id,
                    "version": format_version,
                    "format": data_format
                })
        
        # Check for data format conflicts
        for data_format, implementations in dependency_formats.items():
            if len(implementations) > 1:
                # Check for version conflicts within same format
                versions = [impl["version"] for impl in implementations if impl["version"]]
                if len(set(versions)) > 1:
                    errors.append(DependencyValidationError(
                        dependency_id="multiple",
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="data_format_version_conflict",
                        error_message=f"Data format '{data_format}' has conflicting versions across dependencies: {set(versions)}",
                        actual_value=versions,
                        expected_value="consistent data format version across all dependencies",
                        severity="error"
                    ))
        
        # Validate individual dependency data formats
        supported_formats = ["json", "xml", "yaml", "protobuf", "avro", "csv", "parquet"]
        
        for dependency in dependencies:
            dependency_id = dependency.get("id", "unknown")
            data_format = dependency.get("data_format", "")
            
            if not data_format:
                errors.append(DependencyValidationError(
                    dependency_id=dependency_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="missing_data_format",
                    error_message="Dependency data format is not specified",
                    actual_value=data_format,
                    expected_value="supported data format",
                    severity="warning"
                ))
            elif data_format.lower() not in supported_formats:
                errors.append(DependencyValidationError(
                    dependency_id=dependency_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="unsupported_data_format",
                    error_message=f"Unsupported data format: {data_format}",
                    actual_value=data_format,
                    expected_value="one of: " + ", ".join(supported_formats),
                    severity="warning"
                ))
            
            # Validate format-specific requirements
            if data_format.lower() == "json":
                json_config = dependency.get("json_config", {})
                if json_config:
                    # Check for JSON schema if specified
                    schema = json_config.get("schema", "")
                    if schema and not isinstance(schema, dict):
                        errors.append(DependencyValidationError(
                            dependency_id=dependency_id,
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="invalid_json_schema",
                            error_message="JSON schema must be a dictionary",
                            actual_value=schema,
                            expected_value="JSON schema dictionary",
                            severity="error"
                        ))
            
            elif data_format.lower() == "xml":
                xml_config = dependency.get("xml_config", {})
                if xml_config:
                    # Check for XML namespace if required
                    namespace = xml_config.get("namespace", "")
                    if xml_config.get("require_namespace", False) and not namespace:
                        errors.append(DependencyValidationError(
                            dependency_id=dependency_id,
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="missing_xml_namespace",
                            error_message="XML format requires namespace",
                            actual_value=namespace,
                            expected_value="XML namespace",
                            severity="error"
                        ))
            
            elif data_format.lower() == "protobuf":
                proto_config = dependency.get("protobuf_config", {})
                if not proto_config:
                    errors.append(DependencyValidationError(
                        dependency_id=dependency_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="missing_protobuf_config",
                        error_message="Protocol Buffers format requires protobuf configuration",
                        actual_value=proto_config,
                        expected_value="protobuf configuration",
                        severity="warning"
                    ))
        
        return errors
    
    async def _validate_trusted_sources(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate trusted sources"""
        errors = []
        trusted_sources = rule.criteria.get("trusted_sources", [])
        
        for dep in dependencies:
            dep_id = dep.get("id", "unknown")
            source = dep.get("source", "")
            
            if trusted_sources and source not in trusted_sources:
                error = DependencyValidationError(
                    dependency_id=dep_id,
                    rule_id=rule.id,
                    validation_type=rule.validation_type,
                    error_category="untrusted_source",
                    error_message=f"Dependency source '{source}' is not in trusted sources",
                    actual_value=source,
                    expected_value=f"one of {trusted_sources}",
                    severity=ValidationSeverity.WARNING
                )
                errors.append(error)
        
        return errors
    
    async def _validate_security_policies(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate security policies"""
        errors = []
        
        # Check if dependencies list is provided
        if not dependencies:
            errors.append(DependencyValidationError(
                dependency_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_dependencies_provided",
                error_message="No dependencies provided for security policy validation",
                actual_value=None,
                expected_value="list of dependencies",
                severity="error"
            ))
            return errors
        
        # Validate security policies across dependencies
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                errors.append(DependencyValidationError(
                    dependency_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_dependency_format",
                    error_message="Dependency must be a dictionary",
                    actual_value=dependency,
                    expected_value="dependency dictionary",
                    severity="error"
                ))
                continue
            
            dependency_id = dependency.get("id", "unknown")
            security_policy = dependency.get("security_policy", {})
            
            if not security_policy:
                errors.append(DependencyValidationError(
                    dependency_id=dependency_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="missing_security_policy",
                    error_message="Dependency security policy is not defined",
                    actual_value=security_policy,
                    expected_value="security policy configuration",
                    severity="warning"
                ))
                continue
            
            # Validate authentication requirements
            auth_required = security_policy.get("authentication_required", False)
            if not auth_required:
                errors.append(DependencyValidationError(
                    dependency_id=dependency_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="authentication_not_required",
                    error_message="Dependency should require authentication for security",
                    actual_value=auth_required,
                    expected_value=True,
                    severity="warning"
                ))
            
            # Validate encryption requirements
            encryption = security_policy.get("encryption", {})
            if not encryption:
                errors.append(DependencyValidationError(
                    dependency_id=dependency_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="encryption_not_configured",
                    error_message="Dependency encryption policy is not configured",
                    actual_value=encryption,
                    expected_value="encryption configuration",
                    severity="warning"
                ))
            else:
                # Check for encryption in transit
                if not encryption.get("in_transit", False):
                    errors.append(DependencyValidationError(
                        dependency_id=dependency_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="encryption_in_transit_not_enabled",
                        error_message="Dependency should enable encryption in transit",
                        actual_value=encryption.get("in_transit"),
                        expected_value=True,
                        severity="warning"
                    ))
                
                # Check for encryption at rest
                if not encryption.get("at_rest", False):
                    errors.append(DependencyValidationError(
                        dependency_id=dependency_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="encryption_at_rest_not_enabled",
                        error_message="Dependency should enable encryption at rest",
                        actual_value=encryption.get("at_rest"),
                        expected_value=True,
                        severity="warning"
                    ))
            
            # Validate access control
            access_control = security_policy.get("access_control", {})
            if not access_control:
                errors.append(DependencyValidationError(
                    dependency_id=dependency_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="access_control_not_configured",
                    error_message="Dependency access control policy is not configured",
                    actual_value=access_control,
                    expected_value="access control configuration",
                    severity="warning"
                ))
            else:
                # Check for role-based access control
                if not access_control.get("rbac_enabled", False):
                    errors.append(DependencyValidationError(
                        dependency_id=dependency_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="rbac_not_enabled",
                        error_message="Dependency should enable role-based access control",
                        actual_value=access_control.get("rbac_enabled"),
                        expected_value=True,
                        severity="warning"
                    ))
        
        return errors
    
    async def _validate_vulnerability_check(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate vulnerability check"""
        errors = []
        
        # Check if dependencies list is provided
        if not dependencies:
            errors.append(DependencyValidationError(
                dependency_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_dependencies_provided",
                error_message="No dependencies provided for vulnerability check validation",
                actual_value=None,
                expected_value="list of dependencies",
                severity="error"
            ))
            return errors
        
        # Validate vulnerability checks across dependencies
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                errors.append(DependencyValidationError(
                    dependency_id="invalid",
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_dependency_format",
                    error_message="Dependency must be a dictionary",
                    actual_value=dependency,
                    expected_value="dependency dictionary",
                    severity="error"
                ))
                continue
            
            dependency_id = dependency.get("id", "unknown")
            vulnerability_scan = dependency.get("vulnerability_scan", {})
            
            if not vulnerability_scan:
                errors.append(DependencyValidationError(
                    dependency_id=dependency_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="vulnerability_scan_not_configured",
                    error_message="Dependency vulnerability scan is not configured",
                    actual_value=vulnerability_scan,
                    expected_value="vulnerability scan configuration",
                    severity="warning"
                ))
                continue
            
            # Validate scan frequency
            scan_frequency = vulnerability_scan.get("frequency", "")
            valid_frequencies = ["daily", "weekly", "monthly", "on_update"]
            if scan_frequency not in valid_frequencies:
                errors.append(DependencyValidationError(
                    dependency_id=dependency_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_scan_frequency",
                    error_message=f"Invalid scan frequency: {scan_frequency}",
                    actual_value=scan_frequency,
                    expected_value="one of: " + ", ".join(valid_frequencies),
                    severity="warning"
                ))
            
            # Validate severity threshold
            severity_threshold = vulnerability_scan.get("severity_threshold", "")
            valid_severities = ["low", "medium", "high", "critical"]
            if severity_threshold not in valid_severities:
                errors.append(DependencyValidationError(
                    dependency_id=dependency_id,
                    rule_id=rule.rule_id,
                    validation_type=rule.validation_type,
                    error_category="invalid_severity_threshold",
                    error_message=f"Invalid severity threshold: {severity_threshold}",
                    actual_value=severity_threshold,
                    expected_value="one of: " + ", ".join(valid_severities),
                    severity="warning"
                ))
            
            # Check for recent scan results
            last_scan_date = vulnerability_scan.get("last_scan_date", "")
            if last_scan_date:
                try:
                    from datetime import datetime, timedelta
                    scan_date = datetime.fromisoformat(last_scan_date.replace('Z', '+00:00'))
                    days_since_scan = (datetime.now() - scan_date).days
                    
                    # Warn if scan is older than 30 days
                    if days_since_scan > 30:
                        errors.append(DependencyValidationError(
                            dependency_id=dependency_id,
                            rule_id=rule.rule_id,
                            validation_type=rule.validation_type,
                            error_category="stale_scan_results",
                            error_message=f"Vulnerability scan results are {days_since_scan} days old",
                            actual_value=days_since_scan,
                            expected_value="< 30 days",
                            severity="warning"
                        ))
                except ValueError:
                    errors.append(DependencyValidationError(
                        dependency_id=dependency_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="invalid_scan_date_format",
                        error_message="Last scan date format is invalid",
                        actual_value=last_scan_date,
                        expected_value="ISO 8601 date",
                        severity="warning"
                    ))
            
            # Check for known vulnerabilities
            known_vulnerabilities = vulnerability_scan.get("known_vulnerabilities", [])
            if known_vulnerabilities:
                critical_vulns = [v for v in known_vulnerabilities if v.get("severity", "").lower() == "critical"]
                high_vulns = [v for v in known_vulnerabilities if v.get("severity", "").lower() == "high"]
                
                if critical_vulns:
                    errors.append(DependencyValidationError(
                        dependency_id=dependency_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="critical_vulnerabilities_found",
                        error_message=f"Found {len(critical_vulns)} critical vulnerabilities",
                        actual_value=len(critical_vulns),
                        expected_value=0,
                        severity="error"
                    ))
                
                if high_vulns:
                    errors.append(DependencyValidationError(
                        dependency_id=dependency_id,
                        rule_id=rule.rule_id,
                        validation_type=rule.validation_type,
                        error_category="high_vulnerabilities_found",
                        error_message=f"Found {len(high_vulns)} high severity vulnerabilities",
                        actual_value=len(high_vulns),
                        expected_value=0,
                        severity="warning"
                    ))
        
        return errors
    
    async def _validate_circular_detection(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate circular dependency detection"""
        errors = []
        circular_deps = await self.detect_circular_dependencies(dependencies)
        
        for circular_dep in circular_deps:
            error = DependencyValidationError(
                dependency_id="circular",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="circular_dependency",
                error_message=f"Circular dependency detected: {circular_dep}",
                actual_value=circular_dep,
                expected_value="no cycles",
                severity=ValidationSeverity.CRITICAL
            )
            errors.append(error)
        
        return errors
    
    async def _validate_cycle_analysis(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate cycle analysis"""
        errors = []
        
        # Check if dependencies list is provided
        if not dependencies:
            errors.append(DependencyValidationError(
                dependency_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_dependencies_provided",
                error_message="No dependencies provided for cycle analysis validation",
                actual_value=None,
                expected_value="list of dependencies",
                severity="error"
            ))
            return errors
        
        # Build dependency graph for cycle analysis
        dependency_graph = {}
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                continue
            
            dependency_id = dependency.get("id", "unknown")
            depends_on = dependency.get("depends_on", [])
            
            if dependency_id not in dependency_graph:
                dependency_graph[dependency_id] = set()
            
            for dep in depends_on:
                if isinstance(dep, str):
                    dependency_graph[dependency_id].add(dep)
                elif isinstance(dep, dict):
                    dep_id = dep.get("id", "")
                    if dep_id:
                        dependency_graph[dependency_id].add(dep_id)
        
        # Detect cycles using depth-first search
        visited = set()
        recursion_stack = set()
        cycles = []
        
        def dfs(node, path):
            if node in recursion_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(" -> ".join(cycle))
                return
            
            if node in visited:
                return
            
            visited.add(node)
            recursion_stack.add(node)
            
            for neighbor in dependency_graph.get(node, []):
                if neighbor in dependency_graph:
                    dfs(neighbor, path + [node])
            
            recursion_stack.remove(node)
        
        # Run DFS on all nodes
        for node in dependency_graph:
            if node not in visited:
                dfs(node, [])
        
        # Report detected cycles
        for cycle in cycles:
            errors.append(DependencyValidationError(
                dependency_id="cycle_detected",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="dependency_cycle",
                error_message=f"Dependency cycle detected: {cycle}",
                actual_value=cycle,
                expected_value="acyclic dependency graph",
                severity="error"
            ))
        
        # Analyze cycle complexity
        if cycles:
            errors.append(DependencyValidationError(
                dependency_id="complexity_analysis",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="cycle_complexity",
                error_message=f"Found {len(cycles)} dependency cycles affecting system maintainability",
                actual_value=len(cycles),
                expected_value=0,
                severity="warning"
            ))
        
        # Check for potential circular dependencies (indirect)
        indirect_cycles = []
        for node in dependency_graph:
            for neighbor in dependency_graph.get(node, []):
                if neighbor in dependency_graph and node in dependency_graph.get(neighbor, set()):
                    if f"{node} <-> {neighbor}" not in indirect_cycles and f"{neighbor} <-> {node}" not in indirect_cycles:
                        indirect_cycles.append(f"{node} <-> {neighbor}")
        
        for indirect_cycle in indirect_cycles:
            errors.append(DependencyValidationError(
                dependency_id="indirect_cycle",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="potential_circular_dependency",
                error_message=f"Potential circular dependency detected: {indirect_cycle}",
                actual_value=indirect_cycle,
                expected_value="no bidirectional dependencies",
                severity="warning"
            ))
        
        return errors
    
    async def _validate_transitive_analysis(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate transitive analysis"""
        errors = []
        
        # Check if dependencies list is provided
        if not dependencies:
            errors.append(DependencyValidationError(
                dependency_id="unknown",
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="no_dependencies_provided",
                error_message="No dependencies provided for transitive analysis validation",
                actual_value=None,
                expected_value="list of dependencies",
                severity="error"
            ))
            return errors
        
        # Build dependency graph for transitive analysis
        dependency_graph = {}
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                continue
            
            dependency_id = dependency.get("id", "unknown")
            depends_on = dependency.get("depends_on", [])
            
            if dependency_id not in dependency_graph:
                dependency_graph[dependency_id] = set()
            
            for dep in depends_on:
                if isinstance(dep, str):
                    dependency_graph[dependency_id].add(dep)
                elif isinstance(dep, dict):
                    dep_id = dep.get("id", "")
                    if dep_id:
                        dependency_graph[dependency_id].add(dep_id)
        
        # Calculate transitive dependencies for each node
        transitive_deps = {}
        
        def get_transitive_dependencies(node, visited=None):
            if visited is None:
                visited = set()
            
            if node in visited:
                return set()
            
            visited.add(node)
            transitive = set()
            
            for neighbor in dependency_graph.get(node, []):
                transitive.add(neighbor)
                transitive.update(get_transitive_dependencies(neighbor, visited.copy()))
            
            return transitive
        
        for node in dependency_graph:
            transitive_deps[node] = get_transitive_dependencies(node)
        
        # Analyze transitive dependency depth
        max_depth = 0
        deep_dependencies = []
        
        for node, transitive in transitive_deps.items():
            if len(transitive) > max_depth:
                max_depth = len(transitive)
            
            # Warn about dependencies with too many transitive dependencies
            if len(transitive) > 10:
                deep_dependencies.append({
                    "dependency": node,
                    "transitive_count": len(transitive),
                    "transitive_deps": list(transitive)
                })
        
        for deep_dep in deep_dependencies:
            errors.append(DependencyValidationError(
                dependency_id=deep_dep["dependency"],
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="excessive_transitive_dependencies",
                error_message=f"Dependency '{deep_dep['dependency']}' has {deep_dep['transitive_count']} transitive dependencies",
                actual_value=deep_dep["transitive_count"],
                expected_value="<= 10 transitive dependencies",
                severity="warning"
            ))
        
        # Check for potential diamond dependencies
        diamond_patterns = []
        for node in dependency_graph:
            direct_deps = dependency_graph[node]
            
            # Check if any two direct dependencies share common transitive dependencies
            for dep1 in direct_deps:
                for dep2 in direct_deps:
                    if dep1 != dep2:
                        transitive1 = transitive_deps.get(dep1, set())
                        transitive2 = transitive_deps.get(dep2, set())
                        common = transitive1.intersection(transitive2)
                        
                        if common:
                            diamond_patterns.append({
                                "root": node,
                                "branch1": dep1,
                                "branch2": dep2,
                                "common": list(common)
                            })
        
        for pattern in diamond_patterns:
            errors.append(DependencyValidationError(
                dependency_id=pattern["root"],
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="diamond_dependency_pattern",
                error_message=f"Diamond dependency pattern detected: {pattern['root']} -> {pattern['branch1']} and {pattern['branch2']} both depend on {pattern['common']}",
                actual_value=pattern,
                expected_value="avoid diamond dependency patterns",
                severity="warning"
            ))
        
        # Validate transitive dependency stability
        unstable_transitive = []
        for node, transitive in transitive_deps.items():
            for transitive_dep in transitive:
                # Check if transitive dependency is marked as unstable
                for dependency in dependencies:
                    if dependency.get("id") == transitive_dep:
                        stability = dependency.get("stability", "stable")
                        if stability.lower() in ["unstable", "experimental", "deprecated"]:
                            unstable_transitive.append({
                                "dependency": node,
                                "transitive": transitive_dep,
                                "stability": stability
                            })
        
        for unstable in unstable_transitive:
            errors.append(DependencyValidationError(
                dependency_id=unstable["dependency"],
                rule_id=rule.rule_id,
                validation_type=rule.validation_type,
                error_category="unstable_transitive_dependency",
                error_message=f"Dependency '{unstable['dependency']}' transitively depends on unstable '{unstable['transitive']}' ({unstable['stability']})",
                actual_value=unstable["stability"],
                expected_value="stable transitive dependencies",
                severity="warning"
            ))
        
        return errors
    
    async def _validate_dependency_depth(
        self, 
        dependencies: List[Dict[str, Any]], 
        rule: DependencyValidationRule
    ) -> List[DependencyValidationError]:
        """Validate dependency depth"""
        errors = []
        max_allowed_depth = rule.criteria.get("max_depth", 5)
        
        actual_depth = self._calculate_dependencies_depth(dependencies)
        if actual_depth > max_allowed_depth:
            error = DependencyValidationError(
                dependency_id="depth_analysis",
                rule_id=rule.id,
                validation_type=rule.validation_type,
                error_category="excessive_depth",
                error_message=f"Dependency depth {actual_depth} exceeds maximum {max_allowed_depth}",
                actual_value=actual_depth,
                expected_value=f"<={max_allowed_depth}",
                severity=ValidationSeverity.WARNING
            )
            errors.append(error)
        
        return errors
    
    def _is_valid_semver(self, version: str) -> bool:
        """Check if version follows semantic versioning"""
        if not version:
            return False
        
        import re
        semver_pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9\-]+)?(\+[a-zA-Z0-9\-]+)?$"
        return re.match(semver_pattern, version) is not None
    
    def _is_valid_version_constraint(self, constraint: str) -> bool:
        """Check if version constraint is valid"""
        if not constraint:
            return True  # Empty constraint is valid
        
        import re
        constraint_pattern = r"^[~\^<>=]*\d+\.\d+\.\d+$"
        return re.match(constraint_pattern, constraint) is not None
    
    async def _generate_validation_summary(
        self, 
        layer_name: str,
        errors: List[DependencyValidationError],
        circular_dependencies: List[str],
        missing_dependencies: List[str]
    ) -> Dict[str, Any]:
        """Generate validation summary"""
        error_types = [error.validation_type.value for error in errors]
        error_categories = [error.error_category for error in errors]
        severity_counts = {}
        
        for error in errors:
            severity = error.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "layer_name": layer_name,
            "total_errors": len(errors),
            "error_types": list(set(error_types)),
            "error_categories": list(set(error_categories)),
            "severity_distribution": severity_counts,
            "circular_dependencies_count": len(circular_dependencies),
            "missing_dependencies_count": len(missing_dependencies),
            "most_common_error": max(error_categories) if error_categories else None
        }
    
    def _extract_security_flags(self, errors: List[DependencyValidationError]) -> List[str]:
        """Extract security flags from validation errors"""
        security_flags = []
        
        for error in errors:
            if error.validation_type == DependencyValidationType.SECURITY:
                security_flags.append("security_validation_failed")
            elif "untrusted" in error.error_category:
                security_flags.append("untrusted_dependency")
            elif "circular" in error.error_category:
                security_flags.append("circular_dependency")
        
        return security_flags
    
    async def _estimate_validation_complexity(self, request: LayerDependenciesValidationRequest) -> str:
        """Estimate validation complexity"""
        complexity_score = len(request.dependencies) // 5
        
        # Add complexity for validation rules
        complexity_score += len(request.validation_rules) // 3
        
        if complexity_score <= 3:
            return "low"
        elif complexity_score <= 7:
            return "medium"
        else:
            return "high"
    
    def _calculate_dependencies_risk_score(self, validation_result: DependenciesValidationResult) -> float:
        """Calculate risk score for the dependencies (0.0 to 1.0)"""
        risk_score = 0.1  # Base risk
        
        # Increase risk for validation errors
        if validation_result.validation_errors:
            risk_score += 0.3
        
        # Increase risk for circular dependencies
        if validation_result.circular_dependencies:
            risk_score += 0.4
        
        # Increase risk for missing dependencies
        if validation_result.missing_dependencies:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    def _generate_dependencies_id(self, request: LayerDependenciesValidationRequest, result: DependenciesValidationResult) -> str:
        """Generate unique dependencies identifier"""
        timestamp = datetime.now().isoformat()
        content = f"{request.layer_name}:{len(result.validation_errors)}:{len(result.circular_dependencies)}:{timestamp}"
        return f"deps_validation_{hash(content) % 1000000:06d}"
    
    def _create_fallback_validation(self, request: LayerDependenciesValidationRequest, error: str) -> LayerDependenciesValidationResult:
        """Create safe fallback validation when main validation fails"""
        fallback_error = DependencyValidationError(
            dependency_id="fallback",
            rule_id="fallback_rule",
            validation_type=DependencyValidationType.STRUCTURAL,
            error_category="validation_failed",
            error_message=f"Validation failed: {error}",
            actual_value="fallback",
            expected_value="success",
            severity=ValidationSeverity.WARNING
        )
        
        fallback_result = DependenciesValidationResult(
            is_valid=False,
            validation_errors=[fallback_error],
            validation_warnings=[],
            circular_dependencies=[],
            missing_dependencies=[],
            validation_summary={"fallback": True},
            security_flags=["fallback_mode"]
        )
        
        return LayerDependenciesValidationResult(
            validation_result=fallback_result,
            validated_dependencies=[],
            validation_metadata={"fallback_mode": True},
            safety_validation={"fallback_mode": True},
            dependencies_id=f"fallback_{hash(error) % 100000:06d}"
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when dependencies violate safety policies"""
    pass


class LayerDependenciesValidationError(Exception):
    """Raised for general layer dependencies validation errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_layer_dependencies_validator(safety_policy: Optional[LayerDependenciesSafetyPolicy] = None) -> LayerDependenciesValidator:
    """Factory function to create LayerDependenciesValidator with optional custom safety policy"""
    return LayerDependenciesValidator(safety_policy)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_dependencies_request(request: LayerDependenciesValidationRequest) -> tuple[bool, Optional[str]]:
    """Validate layer dependencies request parameters"""
    try:
        if not request.layer_name or not request.layer_name.strip():
            return False, "Layer name cannot be empty"
        
        if not isinstance(request.dependencies, list):
            return False, "Dependencies must be a list"
        
        if not isinstance(request.validation_rules, list):
            return False, "Validation rules must be a list"
        
        if not isinstance(request.validation_options, dict):
            return False, "Validation options must be a dictionary"
        
        if not isinstance(request.context, dict):
            return False, "Context must be a dictionary"
        
        return True, None
        
    except Exception as e:
        return False, f"Request validation error: {str(e)}"
