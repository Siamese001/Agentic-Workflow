"""
L1 Cognitive Planning - Prepare Information Orchestrator

Coordinates prepare information operations and aggregates results
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

# Import prepare information interfaces
from .format_registry_context import RegistryContextFormatterInterface, RegistryContextFormattingRequest
from .prepare_core_payload import CorePayloadPreparerInterface, CorePayloadPreparationRequest


# ============================================================================
# ORCHESTRATION TYPES AND INTERFACES
# ============================================================================

class PreparationType(str, Enum):
    """Supported preparation types for orchestration"""
    CONTEXT_FORMATTING = "context_formatting"
    PAYLOAD_PREPARATION = "payload_preparation"
    ALL = "all"


class PreparationMode(str, Enum):
    """Preparation execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


@dataclass
class PreparationResult:
    """Individual preparation result from orchestrator"""
    preparation_type: PreparationType
    is_successful: bool
    score: float
    errors: List[Any]
    warnings: List[Any]
    metadata: Dict[str, Any]
    execution_time: float
    timestamp: datetime


@dataclass
class PreparationSummary:
    """Aggregated preparation summary"""
    overall_successful: bool
    overall_score: float
    preparation_results: List[PreparationResult]
    total_errors: int
    total_warnings: int
    execution_summary: Dict[str, Any]
    recommendations: List[str]
    flags: List[str]


@dataclass
class PrepareInformationRequest:
    """Request for preparation orchestration"""
    layer_name: str
    layer_spec: Dict[str, Any]
    preparation_types: List[PreparationType]
    preparation_mode: PreparationMode
    preparation_options: Dict[str, Any]
    context: Dict[str, Any]
    safety_level: str = "standard"
    timeout_seconds: Optional[int] = None


class PrepareInformationOrchestratorInterface(ABC):
    """Abstract interface for prepare information orchestration"""
    
    @abstractmethod
    async def orchestrate_preparations(self, request: PrepareInformationRequest) -> PreparationSummary:
        """Orchestrate multiple preparations and aggregate results"""
        pass
    
    @abstractmethod
    async def run_preparation_pipeline(self, request: PrepareInformationRequest) -> PreparationSummary:
        """Run preparation pipeline with dependencies"""
        pass


# ============================================================================
# L5 SAFETY FOR ORCHESTRATION
# ============================================================================

class PrepareOrchestratorSafetyPolicy(BaseModel):
    """L5 Safety policy for preparation orchestration"""
    max_concurrent_preparations: int = Field(default=2, description="Maximum concurrent preparations")
    max_execution_time_seconds: int = Field(default=180, description="Maximum total execution time")
    allowed_preparation_types: List[str] = Field(default_factory=lambda: [t.value for t in PreparationType])
    allowed_preparation_modes: List[str] = Field(default_factory=lambda: [t.value for t in PreparationMode])
    require_safety_validation: bool = Field(default=True)
    prevent_orchestration_overload: bool = Field(default=True)
    enable_timeout_protection: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class PrepareOrchestratorSafetyValidator:
    """L5 Safety validator for preparation orchestration"""
    
    def __init__(self, policy: PrepareOrchestratorSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.PrepareOrchestratorSafetyValidator")
    
    def validate_orchestrator_request(self, request: PrepareInformationRequest) -> tuple[bool, Optional[str]]:
        """Validates orchestrator request against L5 safety policies"""
        try:
            # Check preparation types
            for preparation_type in request.preparation_types:
                if preparation_type.value not in self.policy.allowed_preparation_types:
                    error_msg = f"Prohibited preparation type: {preparation_type.value}"
                    self.logger.warning(f"Safety violation: {error_msg}")
                    return False, error_msg
            
            # Check preparation mode
            if request.preparation_mode.value not in self.policy.allowed_preparation_modes:
                error_msg = f"Prohibited preparation mode: {request.preparation_mode.value}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check concurrent preparation limit
            if len(request.preparation_types) > self.policy.max_concurrent_preparations:
                error_msg = f"Too many concurrent preparations: {len(request.preparation_types)} > {self.policy.max_concurrent_preparations}"
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

class PrepareInformationOrchestrator(PrepareInformationOrchestratorInterface):
    """
    L1 Cognitive Planning implementation for coordinating prepare information operations.
    
    Provides orchestration of context formatting and payload preparation with parallel/sequential execution,
    following L5 safety principles and comprehensive logging.
    """
    
    def __init__(self, 
                 context_formatter: RegistryContextFormatterInterface,
                 payload_preparer: CorePayloadPreparerInterface,
                 safety_policy: Optional[PrepareOrchestratorSafetyPolicy] = None):
        
        self.safety_policy = safety_policy or PrepareOrchestratorSafetyPolicy()
        self.safety_validator = PrepareOrchestratorSafetyValidator(self.safety_policy)
        self.logger = logging.getLogger(__name__)
        
        # Store preparation instances
        self.preparers = {
            PreparationType.CONTEXT_FORMATTING: context_formatter,
            PreparationType.PAYLOAD_PREPARATION: payload_preparer
        }
        
        # Preparation dependencies (context formatting first, then payload preparation)
        self.preparation_dependencies = {
            PreparationType.CONTEXT_FORMATTING: [],
            PreparationType.PAYLOAD_PREPARATION: [PreparationType.CONTEXT_FORMATTING]
        }
        
        self.logger.info("PrepareInformationOrchestrator initialized with L5 safety policies")
    
    async def orchestrate_preparations(self, request: PrepareInformationRequest) -> PreparationSummary:
        """
        Orchestrate multiple preparations and aggregate results.
        
        Args:
            request: Prepare information request with preparation types and execution mode
            
        Returns:
            PreparationSummary: Aggregated preparation results and summary
            
        Raises:
            ValidationError: If orchestration fails
            SafetyError: If orchestration violates safety policies
        """
        self.logger.info(f"Orchestrating preparations for layer {request.layer_name}")
        
        try:
            # L5 Safety validation
            is_valid, error_msg = self.safety_validator.validate_orchestrator_request(request)
            if not is_valid:
                raise SafetyError(f"Preparation orchestrator safety validation failed: {error_msg}")
            
            # Resolve preparation types
            preparation_types = self._resolve_preparation_types(request.preparation_types)
            
            # Execute preparations based on mode
            if request.preparation_mode == PreparationMode.SEQUENTIAL:
                preparation_results = await self._execute_sequential(request, preparation_types)
            elif request.preparation_mode == PreparationMode.PARALLEL:
                preparation_results = await self._execute_parallel(request, preparation_types)
            else:
                raise ValueError(f"Unsupported preparation mode: {request.preparation_mode}")
            
            # Generate summary
            summary = await self._generate_preparation_summary(request, preparation_results)
            
            self.logger.info(f"Successfully orchestrated preparations for {request.layer_name} with overall score {summary.overall_score:.2f}")
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to orchestrate preparations: {str(e)}")
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback summary in non-fail-closed mode
            return self._create_fallback_summary(request, str(e))
    
    async def run_preparation_pipeline(self, request: PrepareInformationRequest) -> PreparationSummary:
        """
        Run preparation pipeline with dependencies.
        
        Args:
            request: Prepare information request for pipeline execution
            
        Returns:
            PreparationSummary: Pipeline execution results
        """
        # Use sequential mode for pipeline (context -> payload)
        pipeline_request = PrepareInformationRequest(
            layer_name=request.layer_name,
            layer_spec=request.layer_spec,
            preparation_types=request.preparation_types,
            preparation_mode=PreparationMode.SEQUENTIAL,
            preparation_options=request.preparation_options,
            context=request.context,
            safety_level=request.safety_level,
            timeout_seconds=request.timeout_seconds
        )
        
        return await self.orchestrate_preparations(pipeline_request)
    
    def _resolve_preparation_types(self, preparation_types: List[PreparationType]) -> List[PreparationType]:
        """Resolve preparation types, expanding ALL if present"""
        if PreparationType.ALL in preparation_types:
            return [pt for pt in PreparationType if pt != PreparationType.ALL]
        return preparation_types
    
    async def _execute_sequential(self, request: PrepareInformationRequest, preparation_types: List[PreparationType]) -> List[PreparationResult]:
        """Execute preparations sequentially"""
        results = []
        
        for preparation_type in preparation_types:
            try:
                start_time = datetime.now()
                result = await self._execute_single_preparation(request, preparation_type)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                preparation_result = PreparationResult(
                    preparation_type=preparation_type,
                    is_successful=result.is_formatted if hasattr(result, 'is_formatted') else result.is_prepared,
                    score=getattr(result, 'formatting_score', getattr(result, 'preparation_score', 0.0)),
                    errors=getattr(result, 'formatting_errors', getattr(result, 'preparation_errors', [])),
                    warnings=getattr(result, 'formatting_warnings', getattr(result, 'preparation_warnings', [])),
                    metadata=getattr(result, 'formatting_metadata', getattr(result, 'preparation_metadata', {})),
                    execution_time=execution_time,
                    timestamp=start_time
                )
                results.append(preparation_result)
                
            except Exception as e:
                self.logger.error(f"Failed to execute {preparation_type} preparation: {str(e)}")
                # Create error result
                error_result = PreparationResult(
                    preparation_type=preparation_type,
                    is_successful=False,
                    score=0.0,
                    errors=[str(e)],
                    warnings=[],
                    metadata={"error": True},
                    execution_time=0.0,
                    timestamp=datetime.now()
                )
                results.append(error_result)
        
        return results
    
    async def _execute_parallel(self, request: PrepareInformationRequest, preparation_types: List[PreparationType]) -> List[PreparationResult]:
        """Execute preparations in parallel"""
        tasks = []
        
        for preparation_type in preparation_types:
            task = self._execute_single_preparation_with_timing(request, preparation_type)
            tasks.append(task)
        
        # Execute all tasks in parallel
        try:
            if request.timeout_seconds:
                results = await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=request.timeout_seconds)
            else:
                results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            preparation_results = []
            for i, result in enumerate(results):
                preparation_type = preparation_types[i]
                
                if isinstance(result, Exception):
                    self.logger.error(f"Parallel preparation failed for {preparation_type}: {str(result)}")
                    error_result = PreparationResult(
                        preparation_type=preparation_type,
                        is_successful=False,
                        score=0.0,
                        errors=[str(result)],
                        warnings=[],
                        metadata={"error": True},
                        execution_time=0.0,
                        timestamp=datetime.now()
                    )
                    preparation_results.append(error_result)
                else:
                    preparation_results.append(result)
            
            return preparation_results
            
        except asyncio.TimeoutError:
            self.logger.error("Parallel preparation execution timed out")
            # Create timeout results for all remaining preparations
            timeout_results = []
            for preparation_type in preparation_types:
                timeout_result = PreparationResult(
                    preparation_type=preparation_type,
                    is_successful=False,
                    score=0.0,
                    errors=["Execution timed out"],
                    warnings=[],
                    metadata={"timeout": True},
                    execution_time=request.timeout_seconds or 0.0,
                    timestamp=datetime.now()
                )
                timeout_results.append(timeout_result)
            return timeout_results
    
    async def _execute_single_preparation_with_timing(self, request: PrepareInformationRequest, preparation_type: PreparationType) -> PreparationResult:
        """Execute single preparation with timing"""
        start_time = datetime.now()
        result = await self._execute_single_preparation(request, preparation_type)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return PreparationResult(
            preparation_type=preparation_type,
            is_successful=result.is_formatted if hasattr(result, 'is_formatted') else result.is_prepared,
            score=getattr(result, 'formatting_score', getattr(result, 'preparation_score', 0.0)),
            errors=getattr(result, 'formatting_errors', getattr(result, 'preparation_errors', [])),
            warnings=getattr(result, 'formatting_warnings', getattr(result, 'preparation_warnings', [])),
            metadata=getattr(result, 'formatting_metadata', getattr(result, 'preparation_metadata', {})),
            execution_time=execution_time,
            timestamp=start_time
        )
    
    async def _execute_single_preparation(self, request: PrepareInformationRequest, preparation_type: PreparationType):
        """Execute single preparation based on type"""
        preparer = self.preparers.get(preparation_type)
        if not preparer:
            raise ValueError(f"No preparer found for type: {preparation_type}")
        
        # Create appropriate request based on preparation type
        if preparation_type == PreparationType.CONTEXT_FORMATTING:
            preparation_request = RegistryContextFormattingRequest(
                layer_name=request.layer_name,
                layer_spec=request.layer_spec,
                context_data=request.layer_spec.get("context_data", {}),
                formatting_rules=request.preparation_options.get("formatting_rules", []),
                formatting_options=request.preparation_options,
                context=request.context,
                formatting_constraints=request.preparation_options.get("formatting_constraints", {}),
                safety_level=request.safety_level
            )
            return await preparer.format_registry_context(preparation_request)
        
        elif preparation_type == PreparationType.PAYLOAD_PREPARATION:
            preparation_request = CorePayloadPreparationRequest(
                layer_name=request.layer_name,
                layer_spec=request.layer_spec,
                payload_data=request.layer_spec.get("payload_data", {}),
                preparation_rules=request.preparation_options.get("preparation_rules", []),
                preparation_options=request.preparation_options,
                context=request.context,
                preparation_constraints=request.preparation_options.get("preparation_constraints", {}),
                safety_level=request.safety_level
            )
            return await preparer.prepare_core_payload(preparation_request)
        
        else:
            raise ValueError(f"Unsupported preparation type: {preparation_type}")
    
    async def _generate_preparation_summary(self, request: PrepareInformationRequest, preparation_results: List[PreparationResult]) -> PreparationSummary:
        """Generate aggregated preparation summary"""
        total_errors = sum(len(result.errors) for result in preparation_results)
        total_warnings = sum(len(result.warnings) for result in preparation_results)
        
        # Calculate overall score
        if preparation_results:
            overall_score = sum(result.score for result in preparation_results) / len(preparation_results)
        else:
            overall_score = 0.0
        
        # Determine overall success
        overall_successful = all(result.is_successful for result in preparation_results)
        
        # Generate execution summary
        execution_summary = {
            "total_preparations": len(preparation_results),
            "successful_preparations": sum(1 for result in preparation_results if result.is_successful),
            "failed_preparations": sum(1 for result in preparation_results if not result.is_successful),
            "total_execution_time": sum(result.execution_time for result in preparation_results),
            "average_execution_time": sum(result.execution_time for result in preparation_results) / len(preparation_results) if preparation_results else 0.0,
            "preparation_types": [result.preparation_type.value for result in preparation_results]
        }
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(preparation_results)
        
        # Extract flags
        flags = self._extract_flags(preparation_results)
        
        return PreparationSummary(
            overall_successful=overall_successful,
            overall_score=round(overall_score, 2),
            preparation_results=preparation_results,
            total_errors=total_errors,
            total_warnings=total_warnings,
            execution_summary=execution_summary,
            recommendations=recommendations,
            flags=flags
        )
    
    async def _generate_recommendations(self, preparation_results: List[PreparationResult]) -> List[str]:
        """Generate recommendations based on preparation results"""
        recommendations = []
        
        for result in preparation_results:
            if not result.is_successful:
                if result.preparation_type == PreparationType.CONTEXT_FORMATTING:
                    recommendations.append("Review context formatting rules and data structure")
                elif result.preparation_type == PreparationType.PAYLOAD_PREPARATION:
                    recommendations.append("Check payload preparation configuration and data validation")
        
        if not recommendations:
            recommendations.append("All preparations completed successfully")
        
        return recommendations
    
    def _extract_flags(self, preparation_results: List[PreparationResult]) -> List[str]:
        """Extract flags from preparation results"""
        flags = []
        
        for result in preparation_results:
            if not result.is_successful:
                flags.append(f"{result.preparation_type.value}_preparation_failed")
            if result.errors:
                flags.append(f"{result.preparation_type.value}_has_errors")
            if result.warnings:
                flags.append(f"{result.preparation_type.value}_has_warnings")
        
        return flags
    
    def _create_fallback_summary(self, request: PrepareInformationRequest, error: str) -> PreparationSummary:
        """Create safe fallback summary when orchestration fails"""
        error_result = PreparationResult(
            preparation_type=PreparationType.CONTEXT_FORMATTING,  # Default type
            is_successful=False,
            score=0.0,
            errors=[f"Preparation orchestration failed: {error}"],
            warnings=[],
            metadata={"fallback": True, "error": error},
            execution_time=0.0,
            timestamp=datetime.now()
        )
        
        return PreparationSummary(
            overall_successful=False,
            overall_score=0.0,
            preparation_results=[error_result],
            total_errors=1,
            total_warnings=0,
            execution_summary={"fallback": True},
            recommendations=["Fix preparation orchestration system"],
            flags=["fallback_mode", "orchestration_failed"]
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when preparation orchestration violates safety policies"""
    pass


class PreparationOrchestrationError(Exception):
    """Raised for general preparation orchestration errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_prepare_information_orchestrator(
    context_formatter: RegistryContextFormatterInterface,
    payload_preparer: CorePayloadPreparerInterface,
    safety_policy: Optional[PrepareOrchestratorSafetyPolicy] = None
) -> PrepareInformationOrchestrator:
    """Factory function to create PrepareInformationOrchestrator"""
    return PrepareInformationOrchestrator(
        context_formatter=context_formatter,
        payload_preparer=payload_preparer,
        safety_policy=safety_policy
    )
