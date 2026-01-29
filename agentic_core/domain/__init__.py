"""
Domain entities and exceptions for Agentic Core
HARDENED: Consolidated exception hierarchy with SSOT compliance
"""

# Export core entities
from .BaseEntity import AgentConfig, BaseEntity

# Export core contracts
from .CoreIntegrityVerifier import CoreIntegrityVerifier
from .LegacyArtifacts import LegacyArtifacts

# Export consolidated exception hierarchy (SSOT)
from .SovereignError import (
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

# Public API
__all__ = [
    # Entities
    "BaseEntity",
    "AgentConfig",
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
    # Core Contracts
    "CoreIntegrityVerifier",
    "LegacyArtifacts",
]
