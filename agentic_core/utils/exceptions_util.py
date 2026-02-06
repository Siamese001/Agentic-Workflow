# /agentic_core/domain/exceptions_util.py
# Base Exception Hierarchy for the Agentic Core
# HARDENED: Refactored to inherit from SovereignError SSOT
# Strategy: Isolate domain errors from runtime/infrastructure errors

# Import the master exception hierarchy
from .SovereignError import (
    CircularDependencyError,
    ConfigurationError,
    HealerError,
    HygieneError,
    IntegrityError,
    ResourceNotFoundError,
    SecurityViolationError,
    StructuralError,
    ValidationError,
)
from .SovereignError import (
    SovereignError as AgenticCoreError,
)

# Re-export for backward compatibility while maintaining SSOT
__all__ = [
    "AgenticCoreError",
    "HealerError",
    "CircularDependencyError",
    "ConfigurationError",
    "StructuralError",
    "HygieneError",
    "IntegrityError",
    "ValidationError",
    "ResourceNotFoundError",
    "SecurityViolationError",
]
