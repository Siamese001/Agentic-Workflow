"""
exceptions.py - V3.8 Complete Exceptions Module
Contains all custom exceptions for the Resume Generation System
"""

# Base Exceptions
class ResumeGenerationException(Exception):
    """Base exception for all resume generation errors"""
    pass

class ValidationException(ResumeGenerationException):
    """Exception for validation failures"""
    pass

class ConfigurationException(ResumeGenerationException):
    """Exception for configuration issues"""
    pass

class ProcessingException(ResumeGenerationException):
    """Exception for processing errors"""
    pass

class RenderingException(ResumeGenerationException):
    """Exception for rendering errors"""
    pass

class WorkflowException(ResumeGenerationException):
    """Exception for workflow errors"""
    pass

class APIException(ResumeGenerationException):
    """Exception for API-related errors"""
    pass

class DataException(ResumeGenerationException):
    """Exception for data-related errors"""
    pass

class TimeoutException(ResumeGenerationException):
    """Exception for timeout-related errors"""
    pass

class CircuitBreakerException(ResumeGenerationException):
    """Base exception for circuit breaker"""
    pass

# Specific Exceptions
class PhaseTimeoutError(TimeoutException):
    """Raised when a phase times out"""
    pass

class CircuitBreakerOpenError(CircuitBreakerException):
    """Raised when circuit breaker is open"""
    pass

class FactualFailureException(ValidationException):
    """Raised when factual validation fails"""
    pass

class HopExecutionError(WorkflowException):
    """Raised when hop execution fails"""
    pass

class StagingBufferError(DataException):
    """Raised when staging buffer operations fail"""
    pass

class ConfigLoadError(ConfigurationException):
    """Raised when configuration cannot be loaded"""
    pass

class InvalidInputError(ValidationException):
    """Raised when input validation fails"""
    pass

class ModelNotAvailableError(APIException):
    """Raised when a requested model is not available"""
    pass

class RateLimitError(APIException):
    """Raised when API rate limit is exceeded"""
    pass

class ContentGenerationError(ProcessingException):
    """Raised when content generation fails"""
    pass

class FileSystemError(ProcessingException):
    """Raised for file system operations errors"""
    pass

class JSONParseError(DataException):
    """Raised when JSON parsing fails"""
    pass

class SchemaValidationError(ValidationException):
    """Raised when schema validation fails"""
    pass

class ConstraintViolationError(ValidationException):
    """Raised when constraints are violated"""
    pass

class ThemeAnalysisError(ProcessingException):
    """Raised when theme analysis fails"""
    pass

class EnrichmentError(ProcessingException):
    """Raised when data enrichment fails"""
    pass

class ManifestError(WorkflowException):
    """Raised for manifest-related errors"""
    pass

class CheckpointError(WorkflowException):
    """Raised for checkpoint-related errors"""
    pass

class CriticalValidationError(ValidationException):
    """Raised for critical validation failures that must halt workflow"""
    pass

class RAGException(ProcessingException):
    """Raised for RAG-related errors"""
    pass

class VectorDBException(DataException):
    """Raised for vector database errors"""
    pass

# Export all exceptions
__all__ = [
    # Base exceptions
    'ResumeGenerationException',
    'ValidationException',
    'ConfigurationException',
    'ProcessingException',
    'RenderingException',
    'WorkflowException',
    'APIException',
    'DataException',
    'TimeoutException',
    'CircuitBreakerException',
    
    # Specific exceptions
    'PhaseTimeoutError',
    'CircuitBreakerOpenError',
    'FactualFailureException',
    'HopExecutionError',
    'StagingBufferError',
    'ConfigLoadError',
    'InvalidInputError',
    'ModelNotAvailableError',
    'RateLimitError',
    'ContentGenerationError',
    'FileSystemError',
    'JSONParseError',
    'SchemaValidationError',
    'ConstraintViolationError',
    'ThemeAnalysisError',
    'EnrichmentError',
    'ManifestError',
    'CheckpointError',
    'CriticalValidationError',
    'RAGException',
    'VectorDBException'
]
