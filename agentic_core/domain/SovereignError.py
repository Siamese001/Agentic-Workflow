"""
agentic_core/domain/SovereignError.py - Sovereign Exception Hierarchy
HARDENED: Consolidated exception hierarchy with HealerError migration
"""

# MIGRATED: HealerError exceptions consolidated here
class SovereignError(Exception):
    """Base exception for all Sovereign Agent operations."""
    def __init__(self, message: str, error_code: str = "SOVEREIGN_ERROR"):  # SSOT: Mandatory error codes
        super().__init__(message)  # Critical: Maintain standard Exception behavior
        self.message = message 
        self.error_code = error_code

class HealerError(SovereignError):
    """Raised when self-healing operations fail."""
    def __init__(self, message: str):
        super().__init__(message, error_code="HEALER_ERROR")

class CircularDependencyError(HealerError):
    """Raised when a circular dependency or healing loop is detected."""
    def __init__(self, message: str):
        super().__init__(message)
        self.error_code = "CIRCULAR_DEPENDENCY"

class ConfigurationError(SovereignError):
    """Raised when agent configuration violates security or schema constraints."""
    def __init__(self, message: str):
        super().__init__(message, error_code="CONFIG_ERROR")

class StructuralError(HealerError):
    """Raised during structural healing (relocation, fission) failures."""
    def __init__(self, message: str):
        super().__init__(message)
        self.error_code = "STRUCTURAL_ERROR"

class HygieneError(HealerError):
    """Raised when code hygiene validation fails."""
    def __init__(self, message: str):
        super().__init__(message)
        self.error_code = "HYGIENE_ERROR"

class IntegrityError(SovereignError):
    """Raised when system integrity is compromised."""
    def __init__(self, message: str):
        super().__init__(message, error_code="INTEGRITY_ERROR")

class ValidationError(SovereignError):
    """Raised when validation fails."""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, error_code="VALIDATION_ERROR")

class ResourceNotFoundError(SovereignError):
    """Raised when a requested domain object cannot be found."""
    def __init__(self, message: str):
        super().__init__(message, error_code="RESOURCE_NOT_FOUND")

class SecurityViolationError(SovereignError):
    """Raised when an input or output violates governance policies."""
    def __init__(self, message: str, violation_type: str):
        self.violation_type = violation_type
        super().__init__(f"Security Violation [{violation_type}]: {message}", error_code="SECURITY_ERROR")