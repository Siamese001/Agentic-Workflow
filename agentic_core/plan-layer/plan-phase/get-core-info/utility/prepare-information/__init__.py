"""
L1 Cognitive Planning - Prepare Information Module

Implements pure planning operations for preparing and formatting
layer information with L5 safety, comprehensive logging, and fail-closed architecture.
"""

from .format_registry_context import (
    RegistryContextFormatter,
    RegistryContextFormatterInterface,
    create_registry_context_formatter,
    RegistryContextSafetyPolicy,
    validate_context_formatting_request
)

from .prepare_core_payload import (
    CorePayloadPreparer,
    CorePayloadPreparerInterface,
    create_core_payload_preparer,
    CorePayloadSafetyPolicy,
    validate_payload_preparation_request
)

# Export main classes
__all__ = [
    # Core classes
    "RegistryContextFormatter",
    "CorePayloadPreparer",
    
    # Interfaces
    "RegistryContextFormatterInterface",
    "CorePayloadPreparerInterface",
    
    # Factory functions
    "create_registry_context_formatter",
    "create_core_payload_preparer",
    
    # Safety policies
    "RegistryContextSafetyPolicy",
    "CorePayloadSafetyPolicy",
    
    # Request validators
    "validate_context_formatting_request",
    "validate_payload_preparation_request"
]

# Version information
__version__ = "1.0.0"
__author__ = "L1 Cognitive Planning Team"
__description__ = "Layer information preparation and formatting with L5 safety and fail-closed architecture"
