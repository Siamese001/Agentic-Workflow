"""
agentic_core/domain/exceptions.py - Sovereign Exception Hierarchy
"""

class SovereignError(Exception):
    """Base exception for all Sovereign Agent operations."""
    pass

class HealerError(SovereignError):
    """Raised when self-healing operations fail."""
    pass

class CircularDependencyError(HealerError):
    """Raised when a circular dependency or healing loop is detected."""
    pass

class ConfigurationError(SovereignError):
    """Raised when agent configuration violates security or schema constraints."""
    pass

class StructuralError(HealerError):
    """Raised during structural healing (relocation, fission) failures."""
    pass

class HygieneError(HealerError):
    """Raised when code hygiene validation fails."""
    pass