"""
L1 Cognitive Planning - Get Core Info Module

Implements pure planning operations for getting core information including
general request understanding, specific layer analysis, and utility functions
with L5 safety, comprehensive logging, and fail-closed architecture.
"""

# Import general components
from .general import (
    CoreQueryBuilder,
    LayerParameterExtractor,
    RegistryIntentParser,
    CoreQueryBuilderInterface,
    LayerParameterExtractorInterface,
    RegistryIntentParserInterface,
    create_core_query_builder,
    create_layer_parameter_extractor,
    create_registry_intent_parser,
    CoreQuerySafetyPolicy,
    LayerParameterSafetyPolicy,
    RegistryIntentSafetyPolicy,
    validate_core_query_request,
    validate_parameter_extraction_request,
    validate_intent_parsing_request
)

# Import specific components
from .specific import (
    LayerRequirementsAnalyzer,
    LayerDependencyExtractor,
    LayerIdGenerator,
    LayerInterfaceMapper,
    LayerCompatibilityValidator,
    LayerSpecValidator,
    LayerRequirementsAnalyzerInterface,
    LayerDependencyExtractorInterface,
    LayerIdGeneratorInterface,
    LayerInterfaceMapperInterface,
    LayerCompatibilityValidatorInterface,
    LayerSpecValidatorInterface,
    create_layer_requirements_analyzer,
    create_layer_dependency_extractor,
    create_layer_id_generator,
    create_layer_interface_mapper,
    create_layer_compatibility_validator,
    create_layer_spec_validator,
    LayerRequirementsSafetyPolicy,
    LayerDependencySafetyPolicy,
    LayerIdSafetyPolicy,
    LayerInterfaceSafetyPolicy,
    LayerCompatibilitySafetyPolicy,
    LayerSpecSafetyPolicy,
    validate_requirements_analysis_request,
    validate_dependency_extraction_request,
    validate_id_generation_request,
    validate_interface_mapping_request,
    validate_compatibility_validation_request,
    validate_spec_validation_request
)

# Import orchestrator components
from .get_core_info_orchestrator import (
    GetCoreInfoOrchestrator,
    GetCoreInfoRequest,
    GetCoreInfoResponse,
    ExecutionMode,
    PhaseStatus,
    PhaseResult,
    PhaseCompletionStatus,
    GetCoreInfoOrchestratorInterface,
    GetCoreInfoSafetyPolicy,
    PhaseCompletionChecker,
    create_get_core_info_orchestrator
)

# Import utility components
from .utility import (
    # Prepare Information
    RegistryContextFormatter,
    CorePayloadPreparer,
    RegistryContextFormatterInterface,
    CorePayloadPreparerInterface,
    create_registry_context_formatter,
    create_core_payload_preparer,
    RegistryContextSafetyPolicy,
    CorePayloadSafetyPolicy,
    validate_context_formatting_request,
    validate_payload_preparation_request,
    PrepareInformationOrchestrator,
    PrepareInformationRequest,
    PreparationType,
    PreparationMode,
    PreparationResult,
    PreparationSummary,
    create_prepare_information_orchestrator,
    PrepareOrchestratorSafetyPolicy,
    PrepareInformationRegistry,
    PreparerRegistration,
    get_prepare_information_registry,
    PrepareInformationMetrics,
    PrepareOrchestratorMetrics,
    PrepareMetricsCollectorInterface,
    PrepareInMemoryMetricsCollector,
    PreparePrometheusMetricsCollector,
    PrepareMetricsHealthMonitor,
    PrepareHealthStatus,
    collect_prepare_metrics,
    collect_prepare_orchestrator_metrics,
    create_prepare_in_memory_metrics_collector,
    create_prepare_prometheus_metrics_collector,
    create_prepare_metrics_health_monitor,
    get_global_prepare_metrics_collector,
    set_global_prepare_metrics_collector,
    get_global_prepare_health_monitor,
    set_global_prepare_health_monitor,
    # Validate Information
    LayerDependenciesValidator,
    LayerInterfacesValidator, 
    LayerCompatibilityValidator,
    LayerSecurityValidator,
    LayerPerformanceValidator,
    LayerReliabilityValidator,
    LayerScalabilityValidator,
    LayerMaintainabilityValidator,
    LayerCompletenessValidator,
    LayerDependenciesValidatorInterface,
    LayerInterfacesValidatorInterface,
    LayerCompatibilityValidatorInterface, 
    LayerSecurityValidatorInterface,
    LayerPerformanceValidatorInterface,
    LayerReliabilityValidatorInterface,
    LayerScalabilityValidatorInterface,
    LayerMaintainabilityValidatorInterface,
    LayerCompletenessValidatorInterface,
    create_layer_dependencies_validator,
    create_layer_interfaces_validator,
    create_layer_compatibility_validator,
    create_layer_security_validator,
    create_layer_performance_validator,
    create_layer_reliability_validator,
    create_layer_scalability_validator,
    create_layer_maintainability_validator,
    create_layer_completeness_validator,
    LayerDependenciesSafetyPolicy,
    LayerInterfacesSafetyPolicy,
    LayerCompatibilitySafetyPolicy,
    LayerSecuritySafetyPolicy,
    LayerPerformanceSafetyPolicy,
    LayerReliabilitySafetyPolicy,
    LayerScalabilitySafetyPolicy,
    LayerMaintainabilitySafetyPolicy,
    LayerCompletenessSafetyPolicy,
    validate_dependencies_request,
    validate_interfaces_request,
    validate_compatibility_request,
    validate_security_request,
    validate_performance_request,
    validate_reliability_request,
    validate_scalability_request,
    validate_maintainability_request,
    validate_completeness_request,
    ValidationMetrics,
    OrchestratorMetrics,
    MetricsCollectorInterface,
    InMemoryMetricsCollector,
    PrometheusMetricsCollector,
    MetricsHealthMonitor,
    HealthStatus,
    collect_validation_metrics,
    collect_orchestrator_metrics,
    create_in_memory_metrics_collector,
    create_prometheus_metrics_collector,
    create_metrics_health_monitor,
    get_global_metrics_collector,
    set_global_metrics_collector,
    get_global_health_monitor,
    set_global_health_monitor,
    LayerValidationOrchestrator,
    ValidationResult,
    ValidationSummary,
    ValidationRegistry,
    ValidatorRegistration,
    get_validation_registry
)

# Export main classes
__all__ = [
    # Orchestrator - Core classes
    "GetCoreInfoOrchestrator",
    "GetCoreInfoRequest",
    "GetCoreInfoResponse",
    "ExecutionMode",
    "PhaseStatus",
    "PhaseResult",
    "PhaseCompletionStatus",
    
    # Orchestrator - Interfaces
    "GetCoreInfoOrchestratorInterface",
    
    # Orchestrator - Factory functions
    "create_get_core_info_orchestrator",
    
    # Orchestrator - Safety policies
    "GetCoreInfoSafetyPolicy",
    
    # Orchestrator - Utilities
    "PhaseCompletionChecker",
    
    # General - Core classes
    "CoreQueryBuilder",
    "LayerParameterExtractor",
    "RegistryIntentParser",
    
    # General - Interfaces
    "CoreQueryBuilderInterface",
    "LayerParameterExtractorInterface",
    "RegistryIntentParserInterface",
    
    # General - Factory functions
    "create_core_query_builder",
    "create_layer_parameter_extractor",
    "create_registry_intent_parser",
    
    # General - Safety policies
    "CoreQuerySafetyPolicy",
    "LayerParameterSafetyPolicy",
    "RegistryIntentSafetyPolicy",
    
    # General - Request validators
    "validate_core_query_request",
    "validate_parameter_extraction_request",
    "validate_intent_parsing_request",
    
    # Specific - Core classes
    "LayerRequirementsAnalyzer",
    "LayerDependencyExtractor",
    "LayerIdGenerator",
    "LayerInterfaceMapper",
    "LayerCompatibilityValidator",
    "LayerSpecValidator",
    
    # Specific - Interfaces
    "LayerRequirementsAnalyzerInterface",
    "LayerDependencyExtractorInterface",
    "LayerIdGeneratorInterface",
    "LayerInterfaceMapperInterface",
    "LayerCompatibilityValidatorInterface",
    "LayerSpecValidatorInterface",
    
    # Specific - Factory functions
    "create_layer_requirements_analyzer",
    "create_layer_dependency_extractor",
    "create_layer_id_generator",
    "create_layer_interface_mapper",
    "create_layer_compatibility_validator",
    "create_layer_spec_validator",
    
    # Specific - Safety policies
    "LayerRequirementsSafetyPolicy",
    "LayerDependencySafetyPolicy",
    "LayerIdSafetyPolicy",
    "LayerInterfaceSafetyPolicy",
    "LayerCompatibilitySafetyPolicy",
    "LayerSpecSafetyPolicy",
    
    # Specific - Request validators
    "validate_requirements_analysis_request",
    "validate_dependency_extraction_request",
    "validate_id_generation_request",
    "validate_interface_mapping_request",
    "validate_compatibility_validation_request",
    "validate_spec_validation_request",
    
    # Utility - Prepare Information - Core classes
    "RegistryContextFormatter",
    "CorePayloadPreparer",
    
    # Utility - Prepare Information - Interfaces
    "RegistryContextFormatterInterface",
    "CorePayloadPreparerInterface",
    
    # Utility - Prepare Information - Factory functions
    "create_registry_context_formatter",
    "create_core_payload_preparer",
    
    # Utility - Prepare Information - Safety policies
    "RegistryContextSafetyPolicy",
    "CorePayloadSafetyPolicy",
    
    # Utility - Prepare Information - Request validators
    "validate_context_formatting_request",
    "validate_payload_preparation_request",
    
    # Utility - Prepare Information - Orchestration
    "PrepareInformationOrchestrator",
    "PrepareInformationRequest",
    "PreparationType",
    "PreparationMode",
    "PreparationResult",
    "PreparationSummary",
    "create_prepare_information_orchestrator",
    "PrepareOrchestratorSafetyPolicy",
    
    # Utility - Prepare Information - Registry
    "PrepareInformationRegistry",
    "PreparerRegistration",
    "get_prepare_information_registry",
    
    # Utility - Prepare Information - Metrics
    "PrepareInformationMetrics",
    "PrepareOrchestratorMetrics",
    "PrepareMetricsCollectorInterface",
    "PrepareInMemoryMetricsCollector",
    "PreparePrometheusMetricsCollector",
    "PrepareMetricsHealthMonitor",
    "PrepareHealthStatus",
    "collect_prepare_metrics",
    "collect_prepare_orchestrator_metrics",
    "create_prepare_in_memory_metrics_collector",
    "create_prepare_prometheus_metrics_collector",
    "create_prepare_metrics_health_monitor",
    "get_global_prepare_metrics_collector",
    "set_global_prepare_metrics_collector",
    "get_global_prepare_health_monitor",
    "set_global_prepare_health_monitor",
    
    # Utility - Validate Information - Core validators
    "LayerDependenciesValidator",
    "LayerInterfacesValidator", 
    "LayerCompatibilityValidator",
    "LayerSecurityValidator",
    "LayerPerformanceValidator",
    "LayerReliabilityValidator",
    "LayerScalabilityValidator",
    "LayerMaintainabilityValidator",
    "LayerCompletenessValidator",
    
    # Utility - Validate Information - Interfaces
    "LayerDependenciesValidatorInterface",
    "LayerInterfacesValidatorInterface",
    "LayerCompatibilityValidatorInterface", 
    "LayerSecurityValidatorInterface",
    "LayerPerformanceValidatorInterface",
    "LayerReliabilityValidatorInterface",
    "LayerScalabilityValidatorInterface",
    "LayerMaintainabilityValidatorInterface",
    "LayerCompletenessValidatorInterface",
    
    # Utility - Validate Information - Factory functions
    "create_layer_dependencies_validator",
    "create_layer_interfaces_validator",
    "create_layer_compatibility_validator",
    "create_layer_security_validator",
    "create_layer_performance_validator",
    "create_layer_reliability_validator",
    "create_layer_scalability_validator",
    "create_layer_maintainability_validator",
    "create_layer_completeness_validator",
    
    # Utility - Validate Information - Safety policies
    "LayerDependenciesSafetyPolicy",
    "LayerInterfacesSafetyPolicy",
    "LayerCompatibilitySafetyPolicy",
    "LayerSecuritySafetyPolicy",
    "LayerPerformanceSafetyPolicy",
    "LayerReliabilitySafetyPolicy",
    "LayerScalabilitySafetyPolicy",
    "LayerMaintainabilitySafetyPolicy",
    "LayerCompletenessSafetyPolicy",
    
    # Utility - Validate Information - Request validators
    "validate_dependencies_request",
    "validate_interfaces_request",
    "validate_compatibility_request",
    "validate_security_request",
    "validate_performance_request",
    "validate_reliability_request",
    "validate_scalability_request",
    "validate_maintainability_request",
    "validate_completeness_request",
    
    # Utility - Validate Information - Metrics and telemetry
    "ValidationMetrics",
    "OrchestratorMetrics",
    "MetricsCollectorInterface",
    "InMemoryMetricsCollector",
    "PrometheusMetricsCollector",
    "MetricsHealthMonitor",
    "HealthStatus",
    "collect_validation_metrics",
    "collect_orchestrator_metrics",
    "create_in_memory_metrics_collector",
    "create_prometheus_metrics_collector",
    "create_metrics_health_monitor",
    "get_global_metrics_collector",
    "set_global_metrics_collector",
    "get_global_health_monitor",
    "set_global_health_monitor",
    
    # Utility - Validate Information - Orchestration and registry
    "LayerValidationOrchestrator",
    "ValidationResult",
    "ValidationSummary",
    "ValidationRegistry",
    "ValidatorRegistration",
    "get_validation_registry"
]

# Version information
__version__ = "1.0.0"
__author__ = "L1 Cognitive Planning Team"
__description__ = "Get core information system with general, specific, and utility components with L5 safety and fail-closed architecture"
