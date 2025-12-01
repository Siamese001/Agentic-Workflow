"""
L1 Cognitive Planning - Specific Module

Implements pure planning operations for specific layer analysis,
dependency extraction, and validation with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from .analyze_layer_requirements import (
    LayerRequirementsAnalyzer,
    LayerRequirementsAnalyzerInterface,
    create_layer_requirements_analyzer,
    LayerRequirementsSafetyPolicy,
    validate_requirements_analysis_request
)

from .extract_layer_dependencies import (
    LayerDependencyExtractor,
    LayerDependencyExtractorInterface,
    create_layer_dependency_extractor,
    LayerDependencySafetyPolicy,
    validate_dependency_extraction_request
)

from .generate_layer_id import (
    LayerIdGenerator,
    LayerIdGeneratorInterface,
    create_layer_id_generator,
    LayerIdSafetyPolicy,
    validate_id_generation_request
)

from .map_layer_interfaces import (
    LayerInterfaceMapper,
    LayerInterfaceMapperInterface,
    create_layer_interface_mapper,
    LayerInterfaceSafetyPolicy,
    validate_interface_mapping_request
)

from .validate_layer_compatibility import (
    LayerCompatibilityValidator,
    LayerCompatibilityValidatorInterface,
    create_layer_compatibility_validator,
    LayerCompatibilitySafetyPolicy,
    validate_compatibility_validation_request
)

from .validate_layer_spec import (
    LayerSpecValidator,
    LayerSpecValidatorInterface,
    create_layer_spec_validator,
    LayerSpecSafetyPolicy,
    validate_spec_validation_request
)

# Export main classes
__all__ = [
    # Core classes
    "LayerRequirementsAnalyzer",
    "LayerDependencyExtractor",
    "LayerIdGenerator",
    "LayerInterfaceMapper",
    "LayerCompatibilityValidator",
    "LayerSpecValidator",
    
    # Interfaces
    "LayerRequirementsAnalyzerInterface",
    "LayerDependencyExtractorInterface",
    "LayerIdGeneratorInterface",
    "LayerInterfaceMapperInterface",
    "LayerCompatibilityValidatorInterface",
    "LayerSpecValidatorInterface",
    
    # Factory functions
    "create_layer_requirements_analyzer",
    "create_layer_dependency_extractor",
    "create_layer_id_generator",
    "create_layer_interface_mapper",
    "create_layer_compatibility_validator",
    "create_layer_spec_validator",
    
    # Safety policies
    "LayerRequirementsSafetyPolicy",
    "LayerDependencySafetyPolicy",
    "LayerIdSafetyPolicy",
    "LayerInterfaceSafetyPolicy",
    "LayerCompatibilitySafetyPolicy",
    "LayerSpecSafetyPolicy",
    
    # Request validators
    "validate_requirements_analysis_request",
    "validate_dependency_extraction_request",
    "validate_id_generation_request",
    "validate_interface_mapping_request",
    "validate_compatibility_validation_request",
    "validate_spec_validation_request"
]

# Version information
__version__ = "1.0.0"
__author__ = "L1 Cognitive Planning Team"
__description__ = "Specific layer analysis and validation with L5 safety and fail-closed architecture"
