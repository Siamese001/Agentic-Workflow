"""
L1 Cognitive Planning - Get Core Info Orchestrator

Top-level orchestrator that integrates general, specific, and utility subsystems
in a cohesive workflow with L5 safety, comprehensive logging, and fail-closed architecture.
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

# Import subsystem components
from .general.understand_request import (
    CoreQueryBuilderInterface,
    LayerParameterExtractorInterface,
    RegistryIntentParserInterface
)

from .specific import (
    LayerRequirementsAnalyzerInterface,
    LayerDependencyExtractorInterface,
    LayerIdGeneratorInterface,
    LayerInterfaceMapperInterface,
    LayerCompatibilityValidatorInterface,
    LayerSpecValidatorInterface
)

from .utility.prepare_information import (
    PrepareInformationOrchestratorInterface,
    PrepareInformationRequest,
    PreparationType,
    PreparationMode
)

from .utility.validate_information import (
    LayerValidationOrchestratorInterface,
    OrchestratorRequest,
    ValidationType,
    OrchestrationMode
)


# ============================================================================
# ORCHESTRATION TYPES AND INTERFACES
# ============================================================================

class ExecutionMode(str, Enum):
    """Supported execution modes for the orchestrator"""
    FULL_WORKFLOW = "full_workflow"  # Execute all phases
    GENERAL_ONLY = "general_only"    # Execute only general phase
    SPECIFIC_ONLY = "specific_only"  # Execute only specific phase
    UTILITY_ONLY = "utility_only"    # Execute only utility phase
    CUSTOM = "custom"                # Custom phase selection


class PhaseStatus(str, Enum):
    """Phase execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PhaseResult:
    """Result of a single phase execution"""
    phase_name: str
    status: PhaseStatus
    is_successful: bool
    score: float
    errors: List[Any]
    warnings: List[Any]
    metadata: Dict[str, Any]
    execution_time: float
    timestamp: datetime
    output_data: Optional[Dict[str, Any]] = None


@dataclass
class GetCoreInfoRequest:
    """Unified request for get core info orchestration"""
    layer_name: str
    layer_spec: Dict[str, Any]
    execution_mode: ExecutionMode
    phase_selection: Optional[List[str]] = None
    execution_options: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    safety_level: str = "standard"
    timeout_seconds: Optional[int] = None
    enable_rollback: bool = True
    collect_metrics: bool = True


@dataclass
class GetCoreInfoResponse:
    """Unified response from get core info orchestration"""
    request_id: str
    overall_successful: bool
    overall_score: float
    phase_results: List[PhaseResult]
    total_errors: int
    total_warnings: int
    execution_summary: Dict[str, Any]
    recommendations: List[str]
    flags: List[str]
    phase_completion_status: Dict[str, bool]
    phase_2_keys: bool
    execution_time: float
    timestamp: datetime
    rollback_data: Optional[Dict[str, Any]] = None


class GetCoreInfoOrchestratorInterface(ABC):
    """Abstract interface for get core info orchestration"""
    
    @abstractmethod
    async def orchestrate_get_core_info(self, request: GetCoreInfoRequest) -> GetCoreInfoResponse:
        """Orchestrate the complete get core info workflow"""
        pass
    
    @abstractmethod
    async def get_phase_status(self, request_id: str) -> Dict[str, PhaseStatus]:
        """Get current status of all phases"""
        pass
    
    @abstractmethod
    async def rollback_to_phase(self, request_id: str, target_phase: str) -> bool:
        """Rollback execution to a specific phase"""
        pass


# ============================================================================
# L5 SAFETY FOR ORCHESTRATION
# ============================================================================

class GetCoreInfoSafetyPolicy(BaseModel):
    """L5 Safety policy for get core info orchestration"""
    max_execution_time_seconds: int = Field(default=600, description="Maximum total execution time")
    allowed_execution_modes: List[str] = Field(default_factory=lambda: [t.value for t in ExecutionMode])
    require_phase_validation: bool = Field(default=True)
    prevent_orchestration_overload: bool = Field(default=True)
    enable_timeout_protection: bool = Field(default=True)
    enable_rollback_protection: bool = Field(default=True)
    fail_closed: bool = Field(default=True)


class GetCoreInfoSafetyValidator:
    """L5 Safety validator for get core info orchestration"""
    
    def __init__(self, policy: GetCoreInfoSafetyPolicy):
        self.policy = policy
        self.logger = logging.getLogger(f"{__name__}.GetCoreInfoSafetyValidator")
    
    def validate_orchestrator_request(self, request: GetCoreInfoRequest) -> tuple[bool, Optional[str]]:
        """Validates orchestrator request against L5 safety policies"""
        try:
            # Check execution mode
            if request.execution_mode.value not in self.policy.allowed_execution_modes:
                error_msg = f"Prohibited execution mode: {request.execution_mode.value}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Check timeout
            if request.timeout_seconds and request.timeout_seconds > self.policy.max_execution_time_seconds:
                error_msg = f"Timeout too long: {request.timeout_seconds} > {self.policy.max_execution_time_seconds}"
                self.logger.warning(f"Safety violation: {error_msg}")
                return False, error_msg
            
            # Validate phase selection for custom mode
            if request.execution_mode == ExecutionMode.CUSTOM and not request.phase_selection:
                error_msg = "Custom execution mode requires phase_selection"
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
# PHASE COMPLETION TRACKER
# ============================================================================

@dataclass
class PhaseCompletionStatus:
    """Phase completion status tracker"""
    phase_name: str
    is_completed: bool
    completion_time: Optional[datetime]
    components_completed: List[str]
    components_failed: List[str]
    score: float
    metadata: Dict[str, Any]


class PhaseCompletionChecker:
    """Phase completion checker for validating phase 2 keys"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.required_phases = ["general", "specific", "utility"]
        self.required_components = {
            "general": ["core_query_builder", "layer_parameter_extractor", "registry_intent_parser"],
            "specific": ["layer_requirements_analyzer", "layer_dependency_extractor", "layer_id_generator", 
                        "layer_interface_mapper", "layer_compatibility_validator", "layer_spec_validator"],
            "utility": ["context_formatter", "payload_preparer", "validation_orchestrator"]
        }
    
    def check_phase_completion(self, phase_results: List[PhaseResult]) -> Dict[str, PhaseCompletionStatus]:
        """Check completion status of all phases"""
        completion_status = {}
        
        for phase_name in self.required_phases:
            phase_result = next((pr for pr in phase_results if pr.phase_name == phase_name), None)
            
            if phase_result and phase_result.status == PhaseStatus.COMPLETED:
                # Check component completion from metadata
                components_completed = phase_result.metadata.get("components_completed", [])
                components_failed = phase_result.metadata.get("components_failed", [])
                required_components = self.required_components.get(phase_name, [])
                
                # Phase is complete if all required components are completed
                is_completed = all(comp in components_completed for comp in required_components)
                
                completion_status[phase_name] = PhaseCompletionStatus(
                    phase_name=phase_name,
                    is_completed=is_completed,
                    completion_time=phase_result.timestamp,
                    components_completed=components_completed,
                    components_failed=components_failed,
                    score=phase_result.score,
                    metadata=phase_result.metadata
                )
            else:
                completion_status[phase_name] = PhaseCompletionStatus(
                    phase_name=phase_name,
                    is_completed=False,
                    completion_time=None,
                    components_completed=[],
                    components_failed=[],
                    score=0.0,
                    metadata={}
                )
        
        return completion_status
    
    def check_phase_2_keys(self, completion_status: Dict[str, PhaseCompletionStatus]) -> bool:
        """Check if phase 2 keys are TRUE (all phases completed successfully)"""
        return all(status.is_completed for status in completion_status.values())


# ============================================================================
# L1 COGNITIVE PLANNING IMPLEMENTATION
# ============================================================================

class GetCoreInfoOrchestrator(GetCoreInfoOrchestratorInterface):
    """
    L1 Cognitive Planning implementation for get core info orchestration.
    
    Provides orchestration of general, specific, and utility subsystems with
    comprehensive error handling, rollback capabilities, and phase completion tracking.
    """
    
    def __init__(self, 
                 # General subsystem
                 core_query_builder: CoreQueryBuilderInterface,
                 layer_parameter_extractor: LayerParameterExtractorInterface,
                 registry_intent_parser: RegistryIntentParserInterface,
                 
                 # Specific subsystem
                 layer_requirements_analyzer: LayerRequirementsAnalyzerInterface,
                 layer_dependency_extractor: LayerDependencyExtractorInterface,
                 layer_id_generator: LayerIdGeneratorInterface,
                 layer_interface_mapper: LayerInterfaceMapperInterface,
                 layer_compatibility_validator: LayerCompatibilityValidatorInterface,
                 layer_spec_validator: LayerSpecValidatorInterface,
                 
                 # Utility subsystem
                 prepare_information_orchestrator: PrepareInformationOrchestratorInterface,
                 layer_validation_orchestrator: LayerValidationOrchestratorInterface,
                 
                 safety_policy: Optional[GetCoreInfoSafetyPolicy] = None):
        
        self.safety_policy = safety_policy or GetCoreInfoSafetyPolicy()
        self.safety_validator = GetCoreInfoSafetyValidator(self.safety_policy)
        self.phase_completion_checker = PhaseCompletionChecker()
        self.logger = logging.getLogger(__name__)
        
        # Store subsystem instances
        self.general_subsystem = {
            "core_query_builder": core_query_builder,
            "layer_parameter_extractor": layer_parameter_extractor,
            "registry_intent_parser": registry_intent_parser
        }
        
        self.specific_subsystem = {
            "layer_requirements_analyzer": layer_requirements_analyzer,
            "layer_dependency_extractor": layer_dependency_extractor,
            "layer_id_generator": layer_id_generator,
            "layer_interface_mapper": layer_interface_mapper,
            "layer_compatibility_validator": layer_compatibility_validator,
            "layer_spec_validator": layer_spec_validator
        }
        
        self.utility_subsystem = {
            "prepare_information_orchestrator": prepare_information_orchestrator,
            "layer_validation_orchestrator": layer_validation_orchestrator
        }
        
        # Phase execution state
        self._execution_state: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("GetCoreInfoOrchestrator initialized with L5 safety policies")
    
    async def orchestrate_get_core_info(self, request: GetCoreInfoRequest) -> GetCoreInfoResponse:
        """
        Orchestrate the complete get core info workflow.
        
        Args:
            request: Get core info request with execution mode and options
            
        Returns:
            GetCoreInfoResponse: Unified response with all phase results and completion status
            
        Raises:
            ValidationError: If orchestration fails
            SafetyError: If orchestration violates safety policies
        """
        request_id = f"get_core_info_{request.layer_name}_{datetime.now().isoformat()}"
        self.logger.info(f"Orchestrating get core info for {request.layer_name} with request_id: {request_id}")
        
        try:
            # L5 Safety validation
            is_valid, error_msg = self.safety_validator.validate_orchestrator_request(request)
            if not is_valid:
                raise SafetyError(f"Get core info safety validation failed: {error_msg}")
            
            # Initialize execution state
            self._execution_state[request_id] = {
                "request": request,
                "start_time": datetime.now(),
                "current_phase": None,
                "completed_phases": [],
                "rollback_data": {}
            }
            
            # Execute based on mode
            if request.execution_mode == ExecutionMode.FULL_WORKFLOW:
                phase_results = await self._execute_full_workflow(request, request_id)
            elif request.execution_mode == ExecutionMode.GENERAL_ONLY:
                phase_results = await self._execute_general_phase(request, request_id)
            elif request.execution_mode == ExecutionMode.SPECIFIC_ONLY:
                phase_results = await self._execute_specific_phase(request, request_id)
            elif request.execution_mode == ExecutionMode.UTILITY_ONLY:
                phase_results = await self._execute_utility_phase(request, request_id)
            elif request.execution_mode == ExecutionMode.CUSTOM:
                phase_results = await self._execute_custom_workflow(request, request_id)
            else:
                raise ValueError(f"Unsupported execution mode: {request.execution_mode}")
            
            # Calculate completion status
            completion_status = self.phase_completion_checker.check_phase_completion(phase_results)
            phase_2_keys = self.phase_completion_checker.check_phase_2_keys(completion_status)
            
            # Generate response
            response = await self._generate_response(request, request_id, phase_results, completion_status, phase_2_keys)
            
            # Clean up execution state
            if request_id in self._execution_state:
                del self._execution_state[request_id]
            
            self.logger.info(f"Successfully orchestrated get core info for {request.layer_name}, phase_2_keys: {phase_2_keys}")
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to orchestrate get core info: {str(e)}")
            
            # Clean up execution state on failure
            if request_id in self._execution_state:
                del self._execution_state[request_id]
            
            if self.safety_policy.fail_closed:
                raise
            # Return safe fallback response in non-fail-closed mode
            return self._create_fallback_response(request, request_id, str(e))
    
    async def get_phase_status(self, request_id: str) -> Dict[str, PhaseStatus]:
        """Get current status of all phases"""
        if request_id not in self._execution_state:
            return {}
        
        state = self._execution_state[request_id]
        return {
            "general": state.get("general_status", PhaseStatus.PENDING),
            "specific": state.get("specific_status", PhaseStatus.PENDING),
            "utility": state.get("utility_status", PhaseStatus.PENDING)
        }
    
    async def rollback_to_phase(self, request_id: str, target_phase: str) -> bool:
        """Rollback execution to a specific phase"""
        if request_id not in self._execution_state:
            return False
        
        if not self.safety_policy.enable_rollback_protection:
            self.logger.warning("Rollback protection is disabled")
            return False
        
        state = self._execution_state[request_id]
        
        # Restore rollback data for target phase
        if target_phase in state.get("rollback_data", {}):
            self.logger.info(f"Rolling back {request_id} to {target_phase} phase")
            state["current_phase"] = target_phase
            return True
        
        return False
    
    async def _execute_full_workflow(self, request: GetCoreInfoRequest, request_id: str) -> List[PhaseResult]:
        """Execute the complete workflow: general → specific → utility"""
        phase_results = []
        
        # Phase 1: General (understand request)
        self._execution_state[request_id]["current_phase"] = "general"
        self._execution_state[request_id]["general_status"] = PhaseStatus.IN_PROGRESS
        
        general_result = await self._execute_general_phase(request, request_id)
        phase_results.extend(general_result)
        
        if not general_result[0].is_successful and request.enable_rollback:
            self.logger.warning("General phase failed, stopping workflow")
            self._execution_state[request_id]["general_status"] = PhaseStatus.FAILED
            return phase_results
        
        self._execution_state[request_id]["general_status"] = PhaseStatus.COMPLETED
        
        # Phase 2: Specific (analyze/validate layer)
        self._execution_state[request_id]["current_phase"] = "specific"
        self._execution_state[request_id]["specific_status"] = PhaseStatus.IN_PROGRESS
        
        # Enrich context with general phase output
        enriched_context = request.context.copy()
        if general_result[0].output_data:
            enriched_context["general_output"] = general_result[0].output_data
        
        specific_request = GetCoreInfoRequest(
            layer_name=request.layer_name,
            layer_spec=request.layer_spec,
            execution_mode=ExecutionMode.SPECIFIC_ONLY,
            execution_options=request.execution_options,
            context=enriched_context,
            safety_level=request.safety_level,
            timeout_seconds=request.timeout_seconds,
            enable_rollback=request.enable_rollback,
            collect_metrics=request.collect_metrics
        )
        
        specific_result = await self._execute_specific_phase(specific_request, request_id)
        phase_results.extend(specific_result)
        
        if not specific_result[0].is_successful and request.enable_rollback:
            self.logger.warning("Specific phase failed, rolling back to general")
            self._execution_state[request_id]["specific_status"] = PhaseStatus.FAILED
            await self.rollback_to_phase(request_id, "general")
            return phase_results
        
        self._execution_state[request_id]["specific_status"] = PhaseStatus.COMPLETED
        
        # Phase 3: Utility (prepare/validate information)
        self._execution_state[request_id]["current_phase"] = "utility"
        self._execution_state[request_id]["utility_status"] = PhaseStatus.IN_PROGRESS
        
        # Enrich context with previous phases output
        enriched_context.update({
            "specific_output": specific_result[0].output_data if specific_result[0].output_data else {}
        })
        
        utility_request = GetCoreInfoRequest(
            layer_name=request.layer_name,
            layer_spec=request.layer_spec,
            execution_mode=ExecutionMode.UTILITY_ONLY,
            execution_options=request.execution_options,
            context=enriched_context,
            safety_level=request.safety_level,
            timeout_seconds=request.timeout_seconds,
            enable_rollback=request.enable_rollback,
            collect_metrics=request.collect_metrics
        )
        
        utility_result = await self._execute_utility_phase(utility_request, request_id)
        phase_results.extend(utility_result)
        
        if not utility_result[0].is_successful and request.enable_rollback:
            self.logger.warning("Utility phase failed, rolling back to specific")
            self._execution_state[request_id]["utility_status"] = PhaseStatus.FAILED
            await self.rollback_to_phase(request_id, "specific")
        
        self._execution_state[request_id]["utility_status"] = PhaseStatus.COMPLETED
        
        return phase_results
    
    async def _execute_general_phase(self, request: GetCoreInfoRequest, request_id: str) -> List[PhaseResult]:
        """Execute general phase (understand request)"""
        start_time = datetime.now()
        phase_result = PhaseResult(
            phase_name="general",
            status=PhaseStatus.COMPLETED,
            is_successful=True,
            score=0.0,
            errors=[],
            warnings=[],
            metadata={},
            execution_time=0.0,
            timestamp=start_time,
            output_data={}
        )
        
        try:
            # Execute general subsystem components
            components_completed = []
            components_failed = []
            general_output = {}
            
            # Core Query Builder
            try:
                # Create core query request (simplified for this example)
                core_query_result = await self.general_subsystem["core_query_builder"].build_core_query(
                    # Core query request parameters
                )
                general_output["core_query"] = core_query_result
                components_completed.append("core_query_builder")
            except Exception as e:
                components_failed.append("core_query_builder")
                phase_result.errors.append(f"Core query builder failed: {str(e)}")
            
            # Layer Parameter Extractor
            try:
                # Extract layer parameters (simplified)
                parameter_result = await self.general_subsystem["layer_parameter_extractor"].extract_parameters(
                    # Parameter extraction request parameters
                )
                general_output["parameters"] = parameter_result
                components_completed.append("layer_parameter_extractor")
            except Exception as e:
                components_failed.append("layer_parameter_extractor")
                phase_result.errors.append(f"Layer parameter extractor failed: {str(e)}")
            
            # Registry Intent Parser
            try:
                # Parse registry intent (simplified)
                intent_result = await self.general_subsystem["registry_intent_parser"].parse_registry_intent(
                    # Intent parsing request parameters
                )
                general_output["intent"] = intent_result
                components_completed.append("registry_intent_parser")
            except Exception as e:
                components_failed.append("registry_intent_parser")
                phase_result.errors.append(f"Registry intent parser failed: {str(e)}")
            
            # Update phase result
            phase_result.is_successful = len(components_failed) == 0
            phase_result.score = len(components_completed) / (len(components_completed) + len(components_failed)) * 100
            phase_result.metadata = {
                "components_completed": components_completed,
                "components_failed": components_failed,
                "subsystem": "general"
            }
            phase_result.output_data = general_output
            
            # Store rollback data
            if request.enable_rollback:
                self._execution_state[request_id]["rollback_data"]["general"] = general_output
            
        except Exception as e:
            self.logger.error(f"General phase execution failed: {str(e)}")
            phase_result.status = PhaseStatus.FAILED
            phase_result.is_successful = False
            phase_result.errors.append(f"General phase failed: {str(e)}")
        
        phase_result.execution_time = (datetime.now() - start_time).total_seconds()
        return [phase_result]
    
    async def _execute_specific_phase(self, request: GetCoreInfoRequest, request_id: str) -> List[PhaseResult]:
        """Execute specific phase (analyze/validate layer)"""
        start_time = datetime.now()
        phase_result = PhaseResult(
            phase_name="specific",
            status=PhaseStatus.COMPLETED,
            is_successful=True,
            score=0.0,
            errors=[],
            warnings=[],
            metadata={},
            execution_time=0.0,
            timestamp=start_time,
            output_data={}
        )
        
        try:
            # Execute specific subsystem components
            components_completed = []
            components_failed = []
            specific_output = {}
            
            # Layer Requirements Analyzer
            try:
                requirements_result = await self.specific_subsystem["layer_requirements_analyzer"].analyze_requirements(
                    # Requirements analysis request parameters
                )
                specific_output["requirements"] = requirements_result
                components_completed.append("layer_requirements_analyzer")
            except Exception as e:
                components_failed.append("layer_requirements_analyzer")
                phase_result.errors.append(f"Layer requirements analyzer failed: {str(e)}")
            
            # Layer Dependency Extractor
            try:
                dependency_result = await self.specific_subsystem["layer_dependency_extractor"].extract_dependencies(
                    # Dependency extraction request parameters
                )
                specific_output["dependencies"] = dependency_result
                components_completed.append("layer_dependency_extractor")
            except Exception as e:
                components_failed.append("layer_dependency_extractor")
                phase_result.errors.append(f"Layer dependency extractor failed: {str(e)}")
            
            # Layer ID Generator
            try:
                id_result = await self.specific_subsystem["layer_id_generator"].generate_layer_id(
                    # ID generation request parameters
                )
                specific_output["layer_id"] = id_result
                components_completed.append("layer_id_generator")
            except Exception as e:
                components_failed.append("layer_id_generator")
                phase_result.errors.append(f"Layer ID generator failed: {str(e)}")
            
            # Layer Interface Mapper
            try:
                interface_result = await self.specific_subsystem["layer_interface_mapper"].map_interfaces(
                    # Interface mapping request parameters
                )
                specific_output["interfaces"] = interface_result
                components_completed.append("layer_interface_mapper")
            except Exception as e:
                components_failed.append("layer_interface_mapper")
                phase_result.errors.append(f"Layer interface mapper failed: {str(e)}")
            
            # Layer Compatibility Validator
            try:
                compatibility_result = await self.specific_subsystem["layer_compatibility_validator"].validate_compatibility(
                    # Compatibility validation request parameters
                )
                specific_output["compatibility"] = compatibility_result
                components_completed.append("layer_compatibility_validator")
            except Exception as e:
                components_failed.append("layer_compatibility_validator")
                phase_result.errors.append(f"Layer compatibility validator failed: {str(e)}")
            
            # Layer Spec Validator
            try:
                spec_result = await self.specific_subsystem["layer_spec_validator"].validate_spec(
                    # Spec validation request parameters
                )
                specific_output["spec_validation"] = spec_result
                components_completed.append("layer_spec_validator")
            except Exception as e:
                components_failed.append("layer_spec_validator")
                phase_result.errors.append(f"Layer spec validator failed: {str(e)}")
            
            # Update phase result
            phase_result.is_successful = len(components_failed) == 0
            phase_result.score = len(components_completed) / (len(components_completed) + len(components_failed)) * 100
            phase_result.metadata = {
                "components_completed": components_completed,
                "components_failed": components_failed,
                "subsystem": "specific"
            }
            phase_result.output_data = specific_output
            
            # Store rollback data
            if request.enable_rollback:
                self._execution_state[request_id]["rollback_data"]["specific"] = specific_output
            
        except Exception as e:
            self.logger.error(f"Specific phase execution failed: {str(e)}")
            phase_result.status = PhaseStatus.FAILED
            phase_result.is_successful = False
            phase_result.errors.append(f"Specific phase failed: {str(e)}")
        
        phase_result.execution_time = (datetime.now() - start_time).total_seconds()
        return [phase_result]
    
    async def _execute_utility_phase(self, request: GetCoreInfoRequest, request_id: str) -> List[PhaseResult]:
        """Execute utility phase (prepare/validate information)"""
        start_time = datetime.now()
        phase_result = PhaseResult(
            phase_name="utility",
            status=PhaseStatus.COMPLETED,
            is_successful=True,
            score=0.0,
            errors=[],
            warnings=[],
            metadata={},
            execution_time=0.0,
            timestamp=start_time,
            output_data={}
        )
        
        try:
            # Execute utility subsystem components
            components_completed = []
            components_failed = []
            utility_output = {}
            
            # Prepare Information Orchestrator
            try:
                prepare_request = PrepareInformationRequest(
                    layer_name=request.layer_name,
                    layer_spec=request.layer_spec,
                    preparation_types=[PreparationType.ALL],
                    preparation_mode=PreparationMode.SEQUENTIAL,
                    preparation_options=request.execution_options.get("prepare_options", {}),
                    context=request.context,
                    safety_level=request.safety_level,
                    timeout_seconds=request.timeout_seconds
                )
                
                prepare_result = await self.utility_subsystem["prepare_information_orchestrator"].orchestrate_preparations(prepare_request)
                utility_output["preparation"] = prepare_result
                components_completed.append("prepare_information_orchestrator")
            except Exception as e:
                components_failed.append("prepare_information_orchestrator")
                phase_result.errors.append(f"Prepare information orchestrator failed: {str(e)}")
            
            # Layer Validation Orchestrator
            try:
                validate_request = OrchestratorRequest(
                    layer_name=request.layer_name,
                    layer_spec=request.layer_spec,
                    validation_types=[ValidationType.ALL],
                    orchestration_mode=OrchestrationMode.PARALLEL_WITH_DEPENDENCIES,
                    validation_options=request.execution_options.get("validation_options", {}),
                    context=request.context,
                    safety_level=request.safety_level,
                    timeout_seconds=request.timeout_seconds
                )
                
                validation_result = await self.utility_subsystem["layer_validation_orchestrator"].orchestrate_validations(validate_request)
                utility_output["validation"] = validation_result
                components_completed.append("layer_validation_orchestrator")
            except Exception as e:
                components_failed.append("layer_validation_orchestrator")
                phase_result.errors.append(f"Layer validation orchestrator failed: {str(e)}")
            
            # Update phase result
            phase_result.is_successful = len(components_failed) == 0
            phase_result.score = len(components_completed) / (len(components_completed) + len(components_failed)) * 100
            phase_result.metadata = {
                "components_completed": components_completed,
                "components_failed": components_failed,
                "subsystem": "utility"
            }
            phase_result.output_data = utility_output
            
            # Store rollback data
            if request.enable_rollback:
                self._execution_state[request_id]["rollback_data"]["utility"] = utility_output
            
        except Exception as e:
            self.logger.error(f"Utility phase execution failed: {str(e)}")
            phase_result.status = PhaseStatus.FAILED
            phase_result.is_successful = False
            phase_result.errors.append(f"Utility phase failed: {str(e)}")
        
        phase_result.execution_time = (datetime.now() - start_time).total_seconds()
        return [phase_result]
    
    async def _execute_custom_workflow(self, request: GetCoreInfoRequest, request_id: str) -> List[PhaseResult]:
        """Execute custom workflow with selected phases"""
        phase_results = []
        
        for phase_name in request.phase_selection:
            if phase_name == "general":
                results = await self._execute_general_phase(request, request_id)
            elif phase_name == "specific":
                results = await self._execute_specific_phase(request, request_id)
            elif phase_name == "utility":
                results = await self._execute_utility_phase(request, request_id)
            else:
                self.logger.warning(f"Unknown phase: {phase_name}")
                continue
            
            phase_results.extend(results)
        
        return phase_results
    
    async def _generate_response(self, request: GetCoreInfoRequest, request_id: str, 
                                phase_results: List[PhaseResult], 
                                completion_status: Dict[str, PhaseCompletionStatus],
                                phase_2_keys: bool) -> GetCoreInfoResponse:
        """Generate unified response"""
        total_errors = sum(len(result.errors) for result in phase_results)
        total_warnings = sum(len(result.warnings) for result in phase_results)
        
        # Calculate overall score
        if phase_results:
            overall_score = sum(result.score for result in phase_results) / len(phase_results)
        else:
            overall_score = 0.0
        
        # Determine overall success
        overall_successful = all(result.is_successful for result in phase_results)
        
        # Generate execution summary
        execution_summary = {
            "request_id": request_id,
            "execution_mode": request.execution_mode.value,
            "total_phases": len(phase_results),
            "successful_phases": sum(1 for result in phase_results if result.is_successful),
            "failed_phases": sum(1 for result in phase_results if not result.is_successful),
            "total_execution_time": sum(result.execution_time for result in phase_results),
            "average_execution_time": sum(result.execution_time for result in phase_results) / len(phase_results) if phase_results else 0.0,
            "phases_executed": [result.phase_name for result in phase_results]
        }
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(phase_results)
        
        # Extract flags
        flags = self._extract_flags(phase_results)
        
        # Generate phase completion status
        phase_completion_status = {
            phase_name: status.is_completed 
            for phase_name, status in completion_status.items()
        }
        
        # Get rollback data
        rollback_data = self._execution_state.get(request_id, {}).get("rollback_data", {})
        
        return GetCoreInfoResponse(
            request_id=request_id,
            overall_successful=overall_successful,
            overall_score=round(overall_score, 2),
            phase_results=phase_results,
            total_errors=total_errors,
            total_warnings=total_warnings,
            execution_summary=execution_summary,
            recommendations=recommendations,
            flags=flags,
            phase_completion_status=phase_completion_status,
            phase_2_keys=phase_2_keys,
            execution_time=execution_summary["total_execution_time"],
            timestamp=datetime.now(),
            rollback_data=rollback_data if request.enable_rollback else None
        )
    
    async def _generate_recommendations(self, phase_results: List[PhaseResult]) -> List[str]:
        """Generate recommendations based on phase results"""
        recommendations = []
        
        for result in phase_results:
            if not result.is_successful:
                if result.phase_name == "general":
                    recommendations.append("Review request understanding and parsing logic")
                elif result.phase_name == "specific":
                    recommendations.append("Check layer analysis and validation processes")
                elif result.phase_name == "utility":
                    recommendations.append("Examine information preparation and validation systems")
        
        if not recommendations:
            recommendations.append("All phases completed successfully")
        
        return recommendations
    
    def _extract_flags(self, phase_results: List[PhaseResult]) -> List[str]:
        """Extract flags from phase results"""
        flags = []
        
        for result in phase_results:
            if not result.is_successful:
                flags.append(f"{result.phase_name}_phase_failed")
            if result.errors:
                flags.append(f"{result.phase_name}_has_errors")
            if result.warnings:
                flags.append(f"{result.phase_name}_has_warnings")
        
        return flags
    
    def _create_fallback_response(self, request: GetCoreInfoRequest, request_id: str, error: str) -> GetCoreInfoResponse:
        """Create safe fallback response when orchestration fails"""
        error_result = PhaseResult(
            phase_name="orchestration",
            status=PhaseStatus.FAILED,
            is_successful=False,
            score=0.0,
            errors=[f"Orchestration failed: {error}"],
            warnings=[],
            metadata={"fallback": True, "error": error},
            execution_time=0.0,
            timestamp=datetime.now()
        )
        
        return GetCoreInfoResponse(
            request_id=request_id,
            overall_successful=False,
            overall_score=0.0,
            phase_results=[error_result],
            total_errors=1,
            total_warnings=0,
            execution_summary={"fallback": True},
            recommendations=["Fix orchestration system"],
            flags=["fallback_mode", "orchestration_failed"],
            phase_completion_status={},
            phase_2_keys=False,
            execution_time=0.0,
            timestamp=datetime.now()
        )


# ============================================================================
# EXCEPTIONS
# ============================================================================

class SafetyError(Exception):
    """Raised when get core info orchestration violates safety policies"""
    pass


class GetCoreInfoOrchestrationError(Exception):
    """Raised for general get core info orchestration errors"""
    pass


# ============================================================================
# FACTORY FUNCTIONS
# ============================================================================

def create_get_core_info_orchestrator(
    # General subsystem
    core_query_builder: CoreQueryBuilderInterface,
    layer_parameter_extractor: LayerParameterExtractorInterface,
    registry_intent_parser: RegistryIntentParserInterface,
    
    # Specific subsystem
    layer_requirements_analyzer: LayerRequirementsAnalyzerInterface,
    layer_dependency_extractor: LayerDependencyExtractorInterface,
    layer_id_generator: LayerIdGeneratorInterface,
    layer_interface_mapper: LayerInterfaceMapperInterface,
    layer_compatibility_validator: LayerCompatibilityValidatorInterface,
    layer_spec_validator: LayerSpecValidatorInterface,
    
    # Utility subsystem
    prepare_information_orchestrator: PrepareInformationOrchestratorInterface,
    layer_validation_orchestrator: LayerValidationOrchestratorInterface,
    
    safety_policy: Optional[GetCoreInfoSafetyPolicy] = None
) -> GetCoreInfoOrchestrator:
    """Factory function to create GetCoreInfoOrchestrator"""
    return GetCoreInfoOrchestrator(
        core_query_builder=core_query_builder,
        layer_parameter_extractor=layer_parameter_extractor,
        registry_intent_parser=registry_intent_parser,
        layer_requirements_analyzer=layer_requirements_analyzer,
        layer_dependency_extractor=layer_dependency_extractor,
        layer_id_generator=layer_id_generator,
        layer_interface_mapper=layer_interface_mapper,
        layer_compatibility_validator=layer_compatibility_validator,
        layer_spec_validator=layer_spec_validator,
        prepare_information_orchestrator=prepare_information_orchestrator,
        layer_validation_orchestrator=layer_validation_orchestrator,
        safety_policy=safety_policy
    )
