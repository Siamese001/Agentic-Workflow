"""
L1 Cognitive Planning - General Module

Implements pure planning operations for general layer understanding
and request parsing with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from .understand_request import (
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
    "validate_core_query_request",
    "validate_parameter_extraction_request",
    "validate_intent_parsing_request"
]

# Version information
__version__ = "1.0.0"
__author__ = "L1 Cognitive Planning Team"
__description__ = "General layer understanding and request parsing with L5 safety and fail-closed architecture"
