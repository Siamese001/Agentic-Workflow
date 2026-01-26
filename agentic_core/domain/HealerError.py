"""
Domain exceptions for the agentic core system.
"""

class HealerError(Exception):
    """Base exception for healer-related errors."""
    pass

class CircularDependencyError(Exception):
    """Exception raised when circular dependencies are detected."""
    pass

class SovereignError(Exception):
    """Base exception for sovereign system errors."""
    pass

class ConfigurationError(Exception):
    """Exception raised when configuration is invalid."""
    pass

class IntegrityError(Exception):
    """Exception raised when system integrity is compromised."""
    pass

class ValidationError(Exception):
    """Exception raised when validation fails."""
    pass
