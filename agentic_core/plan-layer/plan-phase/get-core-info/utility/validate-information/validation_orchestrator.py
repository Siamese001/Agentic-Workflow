"""
L1 Cognitive Planning - Layer Validation Orchestrator

Coordinates multiple layer validators and aggregates validation results
with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from __future__ import annotations
import logging
import asyncio
from typing import Any, Dict, List, Optional, Union, Tuple, Type
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field, ValidationError

# Import all validator interfaces
from .validate_layer_dependencies import LayerDependenciesValidatorInterface, LayerDependenciesValidationRequest
from .validate_layer_interfaces import LayerInterfacesValidatorInterface, LayerInterfacesValidationRequest
from .validate_layer_compatibility import LayerCompatibilityValidatorInterface, LayerCompatibilityValidationRequest
from .validate_layer_security import LayerSecurityValidatorInterface, LayerSecurityValidationRequest
from .validate_layer_performance import LayerPerformanceValidatorInterface, LayerPerformanceValidationRequest
from .validate_layer_reliability import LayerReliabilityValidatorInterface, LayerReliabilityValidationRequest
from .validate_layer_scalability import LayerScalabilityValidatorInterface, LayerScalabilityValidationRequest
from .validate_layer_maintainability import LayerMaintainabilityValidatorInterface, LayerMaintainabilityValidationRequest
from .validate_layer_completeness import LayerCompletenessValidatorInterface, LayerCompletenessValidationRequest


# ============================================================================
# ORCHESTRATION TYPES AND INTERFACES
# ============================================================================

class ValidationType(str, Enum):
    """Supported validation types for orchestration"""
    DEPENDENCIES = "dependencies"
    INTERFACES = "interfaces"
    COMPATIBILITY = "compatibility"
    SECURITY = "security"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"
    COMPLETENESS = "completeness"
    ALL = "all"


class OrchestrationMode(str, Enum):
    """Orchestration execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PARALLEL_WITH_DEPENDENCIES = "parallel_with_dependencies"


@dataclass
class ValidationResult:
    """Individual validation result from orchestrator"""
    validation_type: ValidationType
    is_valid: bool
    score: float
    errors: List[Any]
    warnings: List[Any]
    metadata: Dict[str, Any]
    execution_time: float
    timestamp: datetime


@dataclass
class ValidationSummary:
    """Aggregated validation summary"""
    overall_valid: bool
    overall_score: float
    validation_results: List[ValidationResult]
    total_errors: int
    total_warnings: int
    execution_summary: Dict[str, Any]
    recommendations: List[str]
    flags: List[str]


@dataclass
class OrchestratorRequest:
    """Request for validation orchestration"""
    layer_name: str
    layer_spec: Dict[str, Any]
    validation_types: List[ValidationType]
    orchestration_mode: OrchestrationMode
    validation_options: Dict[str, Any]
    context: Dict[str, Any]
    safety_level: str = "standard"
    timeout_seconds: Optional[int] = None


class LayerValidationOrchestratorInterface(ABC):
    """Abstract interface for layer validation orchestration"""
    
    @abstractmethod
    async def orchestrate_validations(self, request: OrchestratorRequest) -> ValidationSummary:
        """Orchestrate multiple validations and aggregate results"""
        pass
    
    @abstractmethod
    async def run_validation_pipeline(self, request: OrchestratorRequest) -> ValidationSummary:
        """Run validation pipeline with dependencies"""
        pass


# ============================================================================
# L5 SAFETY FOR ORCHESTRATION
# ============================================================================

class OrchestratorSafetyPolicy(BaseModel):
    """L5 Safety policy for validation orchestration"""
    max_concurrent_validations: int = Field(default=5, description="Maximum concurrent validations")
    max_execution_time_seconds: int = Field(default=300, description="Maximum total execution time")
    allowed_validation_types: List[str] = Field(default_factory=lambda: [t.value for t in ValidationType])
    allowed_orchestration_modes: List[str] = Field(default_factory=lambda: [t.value for t in OrchestrationMode])
    require_safety_validation: bool = Field(default=True)
    prevent_orchestration_overload: bool = Field(default=True)
    enable_timeout_protection: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class OrchestratorSafetyValidator:
    """L5 Safety validator for orchestration operations"""
    
    def __init__(self, policy: OrchestratorSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.OrchestratorSafetyValidator")
    
    def validate_orchestrator_request(self, request: OrchestratorRequest) -> tuple[bool, Optional[str]]:
        """Validates orchestrator request against L5 safety policies"""
        try:
            # Check validation types
            for validation_type in request.validation_types:
                if validation_type.value not in self.policy.allowed_validation_types:
                    error_msg = f"Prohibited validation type: {validation_type.value}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check orchestration mode
            if request.orchestration_mode.value not in self.policy.allowed_orchestration_modes:
                error_msg = f"Prohibited orchestration mode: {request.orchestration_mode.value}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check concurrent validation limit
            if len(request.validation_types) > self.policy.max_concurrent_validations:
                error_msg = f"Too many concurrent validations: {len(request.validation_types)} > {self.policy.max_concurrent_validations}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check timeout
            if request.timeout_seconds and request.timeout_seconds > self.policy.max_execution_time_seconds:
                error_msg = f"Timeout too long: {request.timeout_seconds} > {self.policy.max_execution_time_seconds}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            return True, None
            
        except Exception as e:
            error_msg = f"Orchestration validation error: {str(e)}"
            self.logger.error(f"Safety validation failed: {error_msg}")
            if self.policy.fail_closed:
                return False, error_msg
            return True, error_msg


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class LayerValidationOrchestrator(LayerValidationOrchestratorInterface):
    """
    L1 Cognitive Planning implementation for coordinating layer validations.
    
    Provides orchestration of multiple validators with parallel/sequential execution,
    following L5 safety principles and comprehensive logging.
    """
    
    def __init__(self, 
                 dependencies_validator: LayerDependenciesValidatorInterface,
                 interfaces_validator: LayerInterfacesValidatorInterface,
                 compatibility_validator: LayerCompatibilityValidatorInterface,
                 security_validator: LayerSecurityValidatorInterface,
                 performance_validator: LayerPerformanceValidatorInterface,
                 reliability_validator: LayerReliabilityValidatorInterface,
                 scalability_validator: LayerScalabilityValidatorInterface,
                 maintainability_validator: LayerMaintainabilityValidatorInterface,
                 completeness_validator: LayerCompletenessValidatorInterface,
                 safety_policy: Optional[OrchestratorSafetyPolicy] = None):
        
        self.safety_policy = safety_policy or OrchestratorSafetyPolicy()
        self.safety_validator = OrchestratorSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Store validator instances
        self.validators = {
            ValidationType.DEPENDENCIES: dependencies_validator,
            ValidationType.INTERFACES: interfaces_validator,
            ValidationType.COMPATIBILITY: compatibility_validator,
            ValidationType.SECURITY: security_validator,
            ValidationType.PERFORMANCE: performance_validator,
            ValidationType.RELIABILITY: reliability_validator,
            ValidationType.SCALABILITY: scalability_validator,
            ValidationType.MAINTAINABILITY: maintainability_validator,
            ValidationType.COMPLETENESS: completeness_validator
        }
        
        # Validation dependencies (for parallel_with_dependencies mode)
        self.validation_dependencies = {
            ValidationType.DEPENDENCIES: [],
            ValidationType.INTERFACES: [ValidationType.DEPENDENCIES],
            ValidationType.COMPATIBILITY: [ValidationType.INTERFACES, ValidationType.DEPENDENCIES],
            ValidationType.SECURITY: [ValidationType.INTERFACES],
            ValidationType.PERFORMANCE: [ValidationType.INTERFACES],
            ValidationType.RELIABILITY: [ValidationType.INTERFACES, ValidationType.SECURITY],
            ValidationType.SCALABILITY: [ValidationType.PERFORMANCE, ValidationType.RELIABILITY],
            ValidationType.MAINTAINABILITY: [ValidationType.DEPENDENCIES, ValidationType.INTERFACES],
            ValidationType.COMPLETENESS: [ValidationType.DEPENDENCIES, ValidationType.INTERFACES, ValidationType.SECURITY]
        }
        
        self.logger.info("LayerValidationOrchestrator initialized with L5 safety policies")
    
    async def orchestrate_validations(self, request: OrchestratorRequest) -> ValidationSummary:
        """
        Orchestrate multiple validations and aggregate results.
        
        Args:
            request: Orchestrator request with validation types and execution mode
            
        Returns:
            ValidationSummary: Aggregated validation results and summary
            
        Raises:
            ValidationError: If orchestration fails
            SafetyError: If orchestration violates safety policies
        """
        self.logger.info(f"Orchestrating validations for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            is_valid, error_msg = self.safety_validator.validate_orchestrator_request(request)
            if not is_valid:
                raise SafetyError(f"Orchestrator safety validation failed: {error_msg}")
            
            # Resolve validation types
            validation_types = self._resolve_validation_types(request.validation_types)
            
            # Execute validations based on mode
            if request.orchestration_mode == OrchestrationMode.SEQUENTIAL:
                validation_results = await self._execute_sequential(request, validation_types)
            elif request.orchestration_mode == OrchestrationMode.PARALLEL:
                validation_results = await self._execute_parallel(request, validation_types)
            elif request.orchestration_mode == OrchestrationMode.PARALLEL_WITH_DEPENDENCIES:
                validation_results = await self._execute_parallel_with_dependencies(request, validation_types)
            else:
                raise ValueError(f"Unsupported orchestration mode: {request.orchestration_mode}")
            
            # Generate summary
            summary = await self._generate_validation_summary(request, validation_results)
            
            self.logger.info(f"Successfully orchestrated validations for {request.layer_name} with overall score {summary.overall_score:.2f}")
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to orchestrate validations: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback summary in non-fail-closed mode
            return self._create_fallback_summary(request, str(e))
    
    async def run_validation_pipeline(self, request: OrchestratorRequest) -> ValidationSummary:
        """
        Run validation pipeline with dependencies.
        
        Args:
            request: Orchestrator request for pipeline execution
            
        Returns:
            ValidationSummary: Pipeline execution results
        """
        # Use parallel_with_dependencies mode for pipeline
        pipeline_request = OrchestratorRequest(
            layer_name=request.layer_name,
            layer_spec=request.layer_spec,
            validation_types=request.validation_types,
            orchestration_mode=OrchestrationMode.PARALLEL_WITH_DEPENDENCIES,
            validation_options=request.validation_options,
            context=request.context,
            safety_level=request.safety_level,
            timeout_seconds=request.timeout_seconds
        )
        
        return await self.orchestrate_validations(pipeline_request)
    
    def _resolve_validation_types(self, validation_types: List[ValidationType]) -> List[ValidationType]:
        """Resolve validation types, expanding ALL if present"""
        if ValidationType.ALL in validation_types:
            return [vt for vt in ValidationType if vt != ValidationType.ALL]
        return validation_types
    
    async def _execute_sequential(self, request: OrchestratorRequest, validation_types: List[ValidationType]) -> List[ValidationResult]:
        """Execute validations sequentially"""
        results = []
        
        for validation_type in validation_types:
            try:
                start_time = datetime.now()
                result = await self._execute_single_validation(request, validation_type)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                validation_result = ValidationResult(
                    validation_type=validation_type,
                    is_valid=result.validation_result.is_valid if hasattr(result, 'validation_result') else result.is_complete,
                    score=getattr(result.validation_result, 'score', getattr(result.validation_result, 'security_score', 0.0)) if hasattr(result, 'validation_result') else 0.0,
                    errors=getattr(result.validation_result, 'validation_errors', []) if hasattr(result, 'validation_result') else [],
                    warnings=getattr(result.validation_result, 'validation_warnings', []) if hasattr(result, 'validation_result') else [],
                    metadata=getattr(result, 'validation_metadata', {}),
                    execution_time=execution_time,
                    timestamp=start_time
                )
                results.append(validation_result)
                
            except Exception as e:
                self.logger.error(f"Failed to execute {validation_type} validation: {str(e)}")
                # Create error result
                error_result = ValidationResult(
                    validation_type=validation_type,
                    is_valid=False,
                    score=0.0,
                    errors=[str(e)],
                    warnings=[],
                    metadata={"error": True},
                    execution_time=0.0,
                    timestamp=datetime.now()
                )
                results.append(error_result)
        
        return results
    
    async def _execute_parallel(self, request: OrchestratorRequest, validation_types: List[ValidationType]) -> List[ValidationResult]:
        """Execute validations in parallel"""
        tasks = []
        
        for validation_type in validation_types:
            task = self._execute_single_validation_with_timing(request, validation_type)
            tasks.append(task)
        
        # Execute all tasks in parallel
        try:
            if request.timeout_seconds:
                results = await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=request.timeout_seconds)
            else:
                results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            validation_results = []
            for i, result in enumerate(results):
                validation_type = validation_types[i]
                
                if isinstance(result, Exception):
                    self.logger.error(f"Parallel validation failed for {validation_type}: {str(result)}")
                    error_result = ValidationResult(
                        validation_type=validation_type,
                        is_valid=False,
                        score=0.0,
                        errors=[str(result)],
                        warnings=[],
                        metadata={"error": True},
                        execution_time=0.0,
                        timestamp=datetime.now()
                    )
                    validation_results.append(error_result)
                else:
                    validation_results.append(result)
            
            return validation_results
            
        except asyncio.TimeoutError:
            self.logger.error("Parallel validation execution timed out")
            # Create timeout results for all remaining validations
            timeout_results = []
            for validation_type in validation_types:
                timeout_result = ValidationResult(
                    validation_type=validation_type,
                    is_valid=False,
                    score=0.0,
                    errors=["Execution timed out"],
                    warnings=[],
                    metadata={"timeout": True},
                    execution_time=request.timeout_seconds or 0.0,
                    timestamp=datetime.now()
                )
                timeout_results.append(timeout_result)
            return timeout_results
    
    async def _execute_parallel_with_dependencies(self, request: OrchestratorRequest, validation_types: List[ValidationType]) -> List[ValidationResult]:
        """Execute validations in parallel respecting dependencies"""
        results = {}
        completed_validations = set()
        
        # Continue until all validations are completed
        while len(completed_validations) < len(validation_types):
            # Find validations ready to execute
            ready_validations = []
            for validation_type in validation_types:
                if validation_type not in completed_validations:
                    dependencies = self.validation_dependencies.get(validation_type, [])
                    if all(dep in completed_validations for dep in dependencies):
                        ready_validations.append(validation_type)
            
            if not ready_validations:
                # Circular dependency or missing dependency
                self.logger.error("Circular dependency detected in validation types")
                break
            
            # Execute ready validations in parallel
            tasks = []
            for validation_type in ready_validations:
                task = self._execute_single_validation_with_timing(request, validation_type)
                tasks.append(task)
            
            try:
                if request.timeout_seconds:
                    batch_results = await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True), 
                        timeout=request.timeout_seconds // len(validation_types)
                    )
                else:
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process batch results
                for i, result in enumerate(batch_results):
                    validation_type = ready_validations[i]
                    
                    if isinstance(result, Exception):
                        self.logger.error(f"Dependency validation failed for {validation_type}: {str(result)}")
                        error_result = ValidationResult(
                            validation_type=validation_type,
                            is_valid=False,
                            score=0.0,
                            errors=[str(result)],
                            warnings=[],
                            metadata={"error": True},
                            execution_time=0.0,
                            timestamp=datetime.now()
                        )
                        results[validation_type] = error_result
                    else:
                        results[validation_type] = result
                    
                    completed_validations.add(validation_type)
                    
            except asyncio.TimeoutError:
                self.logger.error("Dependency validation execution timed out")
                # Create timeout results for ready validations
                for validation_type in ready_validations:
                    timeout_result = ValidationResult(
                        validation_type=validation_type,
                        is_valid=False,
                        score=0.0,
                        errors=["Execution timed out"],
                        warnings=[],
                        metadata={"timeout": True},
                        execution_time=request.timeout_seconds or 0.0,
                        timestamp=datetime.now()
                    )
                    results[validation_type] = timeout_result
                    completed_validations.add(validation_type)
        
        return [results[vt] for vt in validation_types if vt in results]
    
    async def _execute_single_validation_with_timing(self, request: OrchestratorRequest, validation_type: ValidationType) -> ValidationResult:
        """Execute single validation with timing"""
        start_time = datetime.now()
        result = await self._execute_single_validation(request, validation_type)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return ValidationResult(
            validation_type=validation_type,
            is_valid=result.validation_result.is_valid if hasattr(result, 'validation_result') else result.is_complete,
            score=getattr(result.validation_result, 'score', getattr(result.validation_result, 'security_score', 0.0)) if hasattr(result, 'validation_result') else 0.0,
            errors=getattr(result.validation_result, 'validation_errors', []) if hasattr(result, 'validation_result') else [],
            warnings=getattr(result.validation_result, 'validation_warnings', []) if hasattr(result, 'validation_result') else [],
            metadata=getattr(result, 'validation_metadata', {}),
            execution_time=execution_time,
            timestamp=start_time
        )
    
    async def _execute_single_validation(self, request: OrchestratorRequest, validation_type: ValidationType):
        """Execute single validation based on type"""
        validator = self.validators.get(validation_type)
        if not validator:
            raise ValueError(f"No validator found for type: {validation_type}")
        
        # Create appropriate request based on validation type
        if validation_type == ValidationType.DEPENDENCIES:
            validation_request = LayerDependenciesValidationRequest(
                layer_name=request.layer_name,
                layer_spec=request.layer_spec,
                dependencies=request.layer_spec.get("dependencies", []),
                dependency_rules=request.validation_options.get("dependency_rules", []),
                validation_options=request.validation_options,
                context=request.context,
                dependency_constraints=request.validation_options.get("dependency_constraints", {}),
                safety_level=request.safety_level
            )
            return await validator.validate_dependencies(validation_request)
        
        elif validation_type == ValidationType.INTERFACES:
            validation_request = LayerInterfacesValidationRequest(
                layer_name=request.layer_name,
                layer_spec=request.layer_spec,
                interfaces=request.layer_spec.get("interfaces", []),
                interface_rules=request.validation_options.get("interface_rules", []),
                validation_options=request.validation_options,
                context=request.context,
                interface_constraints=request.validation_options.get("interface_constraints", {}),
                safety_level=request.safety_level
            )
            return await validator.validate_interfaces(validation_request)
        
        elif validation_type == ValidationType.COMPATIBILITY:
            validation_request = LayerCompatibilityValidationRequest(
                layer_name=request.layer_name,
                layer_spec=request.layer_spec,
                source_layer=request.layer_spec.get("source_layer", {}),
                target_layer=request.layer_spec.get("target_layer", {}),
                compatibility_rules=request.validation_options.get("compatibility_rules", []),
                validation_options=request.validation_options,
                context=request.context,
                compatibility_constraints=request.validation_options.get("compatibility_constraints", {}),
                safety_level=request.safety_level
            )
            return await validator.validate_compatibility(validation_request)
        
        elif validation_type == ValidationType.SECURITY:
            validation_request = LayerSecurityValidationRequest(
                layer_name=request.layer_name,
                layer_spec=request.layer_spec,
                security_rules=request.validation_options.get("security_rules", []),
                validation_options=request.validation_options,
                context=request.context,
                security_constraints=request.validation_options.get("security_constraints", {}),
                safety_level=request.safety_level
            )
            return await validator.validate_security(validation_request)
        
        elif validation_type == ValidationType.PERFORMANCE:
            validation_request = LayerPerformanceValidationRequest(
                layer_name=request.layer_name,
                layer_spec=request.layer_spec,
                performance_metrics=request.layer_spec.get("performance_metrics", {}),
                performance_rules=request.validation_options.get("performance_rules", []),
                validation_options=request.validation_options,
                context=request.context,
                performance_constraints=request.validation_options.get("performance_constraints", {}),
                safety_level=request.safety_level
            )
            return await validator.validate_performance(validation_request)
        
        elif validation_type == ValidationType.RELIABILITY:
            validation_request = LayerReliabilityValidationRequest(
                layer_name=request.layer_name,
                layer_spec=request.layer_spec,
                reliability_metrics=request.layer_spec.get("reliability_metrics", {}),
                reliability_rules=request.validation_options.get("reliability_rules", []),
                validation_options=request.validation_options,
                context=request.context,
                reliability_constraints=request.validation_options.get("reliability_constraints", {}),
                safety_level=request.safety_level
            )
            return await validator.validate_reliability(validation_request)
        
        elif validation_type == ValidationType.SCALABILITY:
            validation_request = LayerScalabilityValidationRequest(
                layer_name=request.layer_name,
                layer_spec=request.layer_spec,
                scalability_metrics=request.layer_spec.get("scalability_metrics", {}),
                scalability_rules=request.validation_options.get("scalability_rules", []),
                validation_options=request.validation_options,
                context=request.context,
                scalability_constraints=request.validation_options.get("scalability_constraints", {}),
                safety_level=request.safety_level
            )
            return await validator.validate_scalability(validation_request)
        
        elif validation_type == ValidationType.MAINTAINABILITY:
            validation_request = LayerMaintainabilityValidationRequest(
                layer_name=request.layer_name,
                layer_spec=request.layer_spec,
                maintainability_metrics=request.layer_spec.get("maintainability_metrics", {}),
                maintainability_rules=request.validation_options.get("maintainability_rules", []),
                validation_options=request.validation_options,
                context=request.context,
                maintainability_constraints=request.validation_options.get("maintainability_constraints", {}),
                safety_level=request.safety_level
            )
            return await validator.validate_maintainability(validation_request)
        
        elif validation_type == ValidationType.COMPLETENESS:
            validation_request = LayerCompletenessValidationRequest(
                layer_name=request.layer_name,
                layer_spec=request.layer_spec,
                completeness_metrics=request.layer_spec.get("completeness_metrics", {}),
                completeness_rules=request.validation_options.get("completeness_rules", []),
                validation_options=request.validation_options,
                context=request.context,
                completeness_constraints=request.validation_options.get("completeness_constraints", {}),
                safety_level=request.safety_level
            )
            return await validator.validate_completeness(validation_request)
        
        else:
            raise ValueError(f"Unsupported validation type: {validation_type}")
    
    async def _generate_validation_summary(self, request: OrchestratorRequest, validation_results: List[ValidationResult]) -> ValidationSummary:
        """Generate aggregated validation summary"""
        total_errors = sum(len(result.errors) for result in validation_results)
        total_warnings = sum(len(result.warnings) for result in validation_results)
        
        # Calculate overall score
        if validation_results:
            overall_score = sum(result.score for result in validation_results) / len(validation_results)
        else:
            overall_score = 0.0
        
        # Determine overall validity
        overall_valid = all(result.is_valid for result in validation_results)
        
        # Generate execution summary
        execution_summary = {
            "total_validations": len(validation_results),
            "successful_validations": sum(1 for result in validation_results if result.is_valid),
            "failed_validations": sum(1 for result in validation_results if not result.is_valid),
            "total_execution_time": sum(result.execution_time for result in validation_results),
            "average_execution_time": sum(result.execution_time for result in validation_results) / len(validation_results) if validation_results else 0.0,
            "validation_types": [result.validation_type.value for result in validation_results]
        }
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(validation_results)
        
        # Extract flags
        flags = self._extract_flags(validation_results)
        
        return ValidationSummary(
            overall_valid=overall_valid,
            overall_score=round(overall_score, 2),
            validation_results=validation_results,
            total_errors=total_errors,
            total_warnings=total_warnings,
            execution_summary=execution_summary,
            recommendations=recommendations,
            flags=flags
        )
    
    async def _generate_recommendations(self, validation_results: List[ValidationResult]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        for result in validation_results:
            if not result.is_valid:
                if result.validation_type == ValidationType.DEPENDENCIES:
                    recommendations.append("Review and fix dependency issues")
                elif result.validation_type == ValidationType.INTERFACES:
                    recommendations.append("Improve interface design and implementation")
                elif result.validation_type == ValidationType.COMPATIBILITY:
                    recommendations.append("Address compatibility issues between layers")
                elif result.validation_type == ValidationType.SECURITY:
                    recommendations.append("Enhance security measures and configurations")
                elif result.validation_type == ValidationType.PERFORMANCE:
                    recommendations.append("Optimize performance bottlenecks")
                elif result.validation_type == ValidationType.RELIABILITY:
                    recommendations.append("Improve system reliability and fault tolerance")
                elif result.validation_type == ValidationType.SCALABILITY:
                    recommendations.append("Enhance scalability configurations")
                elif result.validation_type == ValidationType.MAINTAINABILITY:
                    recommendations.append("Improve code maintainability and documentation")
                elif result.validation_type == ValidationType.COMPLETENESS:
                    recommendations.append("Complete missing features and documentation")
        
        if not recommendations:
            recommendations.append("All validations passed successfully")
        
        return recommendations
    
    def _extract_flags(self, validation_results: List[ValidationResult]) -> List[str]:
        """Extract flags from validation results"""
        flags = []
        
        for result in validation_results:
            if not result.is_valid:
                flags.append(f"{result.validation_type.value}_validation_failed")
            if result.errors:
                flags.append(f"{result.validation_type.value}_has_errors")
            if result.warnings:
                flags.append(f"{result.validation_type.value}_has_warnings")
        
        return flags
    
    def _create_fallback_summary(self, request: OrchestratorRequest, error: str) -> ValidationSummary:
        """Create safe fallback summary when orchestration fails"""
        error_result = ValidationResult(
            validation_type=ValidationType.DEPENDENCIES,  # Default type
            is_valid=False,
            score=0.0,
            errors=[f"Orchestration failed: {error}"],
            warnings=[],
            metadata={"fallback": True, "error": error},
            execution_time=0.0,
            timestamp=datetime.now()
        )
        
        return ValidationSummary(
            overall_valid=False,
            overall_score=0.0,
            validation_results=[error_result],
            total_errors=1,
            total_warnings=0,
            execution_summary={"fallback": True},
            recommendations=["Fix orchestration system"],
            flags=["fallback_mode", "orchestration_failed"]
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when orchestration violates safety policies"""
    pass


class OrchestrationError(Exception):
    """Raised for general orchestration errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_validation_orchestrator(
    dependencies_validator: LayerDependenciesValidatorInterface,
    interfaces_validator: LayerInterfacesValidatorInterface,
    compatibility_validator: LayerCompatibilityValidatorInterface,
    security_validator: LayerSecurityValidatorInterface,
    performance_validator: LayerPerformanceValidatorInterface,
    reliability_validator: LayerReliabilityValidatorInterface,
    scalability_validator: LayerScalabilityValidatorInterface,
    maintainability_validator: LayerMaintainabilityValidatorInterface,
    completeness_validator: LayerCompletenessValidatorInterface,
    safety_policy: Optional[OrchestratorSafetyPolicy] = None
) -> LayerValidationOrchestrator:
    """Factory function to create LayerValidationOrchestrator"""
    return LayerValidationOrchestrator(
        dependencies_validator=dependencies_validator,
        interfaces_validator=interfaces_validator,
        compatibility_validator=compatibility_validator,
        security_validator=security_validator,
        performance_validator=performance_validator,
        reliability_validator=reliability_validator,
        scalability_validator=scalability_validator,
        maintainability_validator=maintainability_validator,
        completeness_validator=completeness_validator,
        safety_policy=safety_policy
    )
