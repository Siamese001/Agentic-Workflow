"""
L1 Cognitive Planning - Understand Request Module

Implements pure planning operations for understanding and parsing
layer requests with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from .build_core_query import (
    CoreQueryBuilder,
    CoreQueryBuilderInterface,
    create_core_query_builder,
    CoreQuerySafetyPolicy,
    validate_query_request
)

from .extract_layer_parameters import (
    LayerParameterExtractor,
    LayerParameterExtractorInterface,
    create_layer_parameter_extractor,
    LayerParameterSafetyPolicy,
    validate_parameter_request
)

from .parse_registry_intent import (
    RegistryIntentParser,
    RegistryIntentParserInterface,
    create_registry_intent_parser,
    RegistryIntentSafetyPolicy,
    validate_intent_request
)

# Export main classes
__all__ = [
    # Core classes
    "CoreQueryBuilder",
    "LayerParameterExtractor",
    "RegistryIntentParser",
    
    # Interfaces
    "CoreQueryBuilderInterface",
    "LayerParameterExtractorInterface",
    "RegistryIntentParserInterface",
    
    # Factory functions
    "create_core_query_builder",
    "create_layer_parameter_extractor",
    "create_registry_intent_parser",
    
    # Safety policies
    "CoreQuerySafetyPolicy",
    "LayerParameterSafetyPolicy",
    "RegistryIntentSafetyPolicy",
    
    # Request validators
    "validate_query_request",
    "validate_parameter_request",
    "validate_intent_request"
]

# Version information
__version__ = "1.0.0"
__author__ = "L1 Cognitive Planning Team"
__description__ = "Layer request understanding and parsing with L5 safety and fail-closed architecture"
