"""
Domain entities and exceptions for Agentic Core
HARDENED: Consolidated exception hierarchy with SSOT compliance
RE-EXPORT: All domain files are in agentic_core.utils - this module re-exports for API stability
"""

# Export core entities (re-export from utils)
from agentic_core.utils.base_entity_config import AgentConfig, BaseEntity

# Export core contracts (re-export from utils)
from agentic_core.utils.core_integrity_verifier_validator import CoreIntegrityVerifier
from agentic_core.utils.LegacyartifactsStrategy import LegacyArtifacts

# Export consolidated exception hierarchy (SSOT) - re-export from utils
from agentic_core.utils.SovereignError import (
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

# Re-export exception module for backward compatibility
from agentic_core.utils import exceptions
from agentic_core.utils.exceptions import SecurityViolationError as SecurityViolationError

# Alias for backward compatibility
entities = type("entities", (), {"BaseEntity": BaseEntity})

# Public API
__all__ = [
    # Entities
    "BaseEntity",
    "AgentConfig",
    "entities",
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
    # Modules
    "exceptions",
]
