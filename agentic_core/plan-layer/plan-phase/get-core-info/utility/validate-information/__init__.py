"""
L1 Cognitive Planning - Layer Validation Information Module

Comprehensive validation system for layer dependencies, interfaces, compatibility,
security, performance, reliability, scalability, maintainability, and completeness
with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from .validate_layer_dependencies import (
    LayerDependenciesValidator,
    LayerDependenciesValidatorInterface,
    create_layer_dependencies_validator,
    LayerDependenciesSafetyPolicy,
    validate_dependencies_request
)

from .validate_layer_interfaces import (
    LayerInterfacesValidator,
    LayerInterfacesValidatorInterface,
    create_layer_interfaces_validator,
    LayerInterfacesSafetyPolicy,
    validate_interfaces_request
)

from .validate_layer_compatibility import (
    LayerCompatibilityValidator,
    LayerCompatibilityValidatorInterface,
    create_layer_compatibility_validator,
    LayerCompatibilitySafetyPolicy,
    validate_compatibility_request
)

from .validate_layer_security import (
    LayerSecurityValidator,
    LayerSecurityValidatorInterface,
    create_layer_security_validator,
    LayerSecuritySafetyPolicy,
    validate_security_request
)

from .validate_layer_performance import (
    LayerPerformanceValidator,
    LayerPerformanceValidatorInterface,
    create_layer_performance_validator,
    LayerPerformanceSafetyPolicy,
    validate_performance_request
)

from .validate_layer_reliability import (
    LayerReliabilityValidator,
    LayerReliabilityValidatorInterface,
    create_layer_reliability_validator,
    LayerReliabilitySafetyPolicy,
    validate_reliability_request
)

from .validate_layer_scalability import (
    LayerScalabilityValidator,
    LayerScalabilityValidatorInterface,
    create_layer_scalability_validator,
    LayerScalabilitySafetyPolicy,
    validate_scalability_request
)

from .validate_layer_maintainability import (
    LayerMaintainabilityValidator,
    LayerMaintainabilityValidatorInterface,
    create_layer_maintainability_validator,
    LayerMaintainabilitySafetyPolicy,
    validate_maintainability_request
)

from .validate_layer_completeness import (
    LayerCompletenessValidator,
    LayerCompletenessValidatorInterface,
    create_layer_completeness_validator,
    LayerCompletenessSafetyPolicy,
    validate_completeness_request
)

from .validation_metrics import (
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
    set_global_health_monitor
)

from .validation_orchestrator import (
    LayerValidationOrchestrator,
    ValidationResult,
    ValidationSummary
)

from .validation_registry import (
    ValidationRegistry,
    ValidatorRegistration,
    get_validation_registry
)

# Export main validator classes
__all__ = [
    # Core validators
    "LayerDependenciesValidator",
    "LayerInterfacesValidator", 
    "LayerCompatibilityValidator",
    "LayerSecurityValidator",
    "LayerPerformanceValidator",
    "LayerReliabilityValidator",
    "LayerScalabilityValidator",
    "LayerMaintainabilityValidator",
    "LayerCompletenessValidator",
    
    # Interfaces
    "LayerDependenciesValidatorInterface",
    "LayerInterfacesValidatorInterface",
    "LayerCompatibilityValidatorInterface", 
    "LayerSecurityValidatorInterface",
    "LayerPerformanceValidatorInterface",
    "LayerReliabilityValidatorInterface",
    "LayerScalabilityValidatorInterface",
    "LayerMaintainabilityValidatorInterface",
    "LayerCompletenessValidatorInterface",
    
    # Factory functions
    "create_layer_dependencies_validator",
    "create_layer_interfaces_validator",
    "create_layer_compatibility_validator",
    "create_layer_security_validator",
    "create_layer_performance_validator",
    "create_layer_reliability_validator",
    "create_layer_scalability_validator",
    "create_layer_maintainability_validator",
    "create_layer_completeness_validator",
    
    # Safety policies
    "LayerDependenciesSafetyPolicy",
    "LayerInterfacesSafetyPolicy",
    "LayerCompatibilitySafetyPolicy",
    "LayerSecuritySafetyPolicy",
    "LayerPerformanceSafetyPolicy",
    "LayerReliabilitySafetyPolicy",
    "LayerScalabilitySafetyPolicy",
    "LayerMaintainabilitySafetyPolicy",
    "LayerCompletenessSafetyPolicy",
    
    # Request validators
    "validate_dependencies_request",
    "validate_interfaces_request",
    "validate_compatibility_request",
    "validate_security_request",
    "validate_performance_request",
    "validate_reliability_request",
    "validate_scalability_request",
    "validate_maintainability_request",
    "validate_completeness_request",
    
    # Metrics and telemetry
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
    
    # Orchestration and registry
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
__description__ = "Comprehensive layer validation system with L5 safety and fail-closed architecture"
