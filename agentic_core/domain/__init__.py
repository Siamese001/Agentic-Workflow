"""
Domain entities and exceptions for Agentic Core

SSOT: This folder is the canonical source of truth for domain types.
All domain types are defined locally in this module.
"""

# Export consolidated exception hierarchy (SSOT) - LOCAL IMPORTS
from .sovereign_error_types import (
    CircularDependencyError,
    ConfigurationError,
    HealerError,
    HygieneError,
    IntegrityError,
    ResourceNotFoundError,
    SecurityViolationError,
    SovereignError,
    StructuralError,
    ValidationError,
)

# Export event types (SSOT) - LOCAL IMPORTS
from .sovereign_event_types import SovereignEvent, event_emission_mixin

# Export legacy artifacts registry (SSOT) - LOCAL IMPORTS
from .legacy_artifacts_types import (
    LegacyArtifacts,
    WEAK_OPENING_PATTERNS,
    CRITICAL_PLACEHOLDERS,
)

# Public API
__all__ = [
    # Exception Hierarchy (SSOT)
    "SovereignError",
    "HealerError",
    "CircularDependencyError",
    "ConfigurationError",
    "StructuralError",
    "HygieneError",
    "IntegrityError",
    "ValidationError",
    "ResourceNotFoundError",
    "SecurityViolationError",
    # Event Types
    "SovereignEvent",
    "event_emission_mixin",
    # Legacy Artifacts
    "LegacyArtifacts",
    "WEAK_OPENING_PATTERNS",
    "CRITICAL_PLACEHOLDERS",
]
