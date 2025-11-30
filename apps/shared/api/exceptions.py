"""
Shared API Exceptions
LEVEL 5 - Common exception classes for API layer
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import UUID

class APIException(Exception):
    """Base exception for API errors"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "API_ERROR",
        error_type: str = "general",
        error_details: Optional[Dict[str, Any]] = None,
        request_id: Optional[UUID] = None,
        stack_trace: Optional[str] = None,
        retry_after: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.error_type = error_type
        self.error_details = error_details
        self.request_id = request_id
        self.stack_trace = stack_trace
        self.retry_after = retry_after
        self.metadata = metadata
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        result = {
            "success": False,
            "error_code": self.error_code,
            "error_type": self.error_type,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }
        
        if self.request_id:
            result["request_id"] = str(self.request_id)
        if self.error_details:
            result["error_details"] = self.error_details
        if self.stack_trace:
            result["stack_trace"] = self.stack_trace
        if self.retry_after is not None:
            result["retry_after"] = self.retry_after
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result

class ValidationAPIException(APIException):
    """Exception for validation errors"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        validation_errors: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="VALIDATION_FAILED",
            error_type="validation",
            **kwargs
        )
        self.validation_errors = validation_errors or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation exception to dictionary"""
        result = super().to_dict()
        result["validation_errors"] = self.validation_errors
        return result
    
    @classmethod
    def from_field_error(cls, field: str, message: str, value: Any = None):
        """Create validation exception from field error"""
        error = {"field": field, "message": message}
        if value is not None:
            error["value"] = value
        
        return cls(
            message=f"Validation failed for field: {field}",
            validation_errors=[error]
        )
    
    @classmethod
    def from_multiple_errors(cls, errors: List[Dict[str, Any]]):
        """Create validation exception from multiple field errors"""
        return cls(
            message="Multiple validation errors occurred",
            validation_errors=errors
        )

class AuthenticationAPIException(APIException):
    """Exception for authentication errors"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        auth_method: Optional[str] = None,
        required_scopes: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            error_type="authentication",
            **kwargs
        )
        self.auth_method = auth_method
        self.required_scopes = required_scopes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert authentication exception to dictionary"""
        result = super().to_dict()
        
        error_details = {}
        if self.auth_method:
            error_details["auth_method"] = self.auth_method
        if self.required_scopes:
            error_details["required_scopes"] = self.required_scopes
        
        if error_details:
            result["error_details"] = error_details
            
        return result

class AuthorizationAPIException(APIException):
    """Exception for authorization errors"""
    
    def __init__(
        self,
        message: str = "Access denied",
        required_permissions: Optional[List[str]] = None,
        current_permissions: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="ACCESS_DENIED",
            error_type="authorization",
            **kwargs
        )
        self.required_permissions = required_permissions
        self.current_permissions = current_permissions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert authorization exception to dictionary"""
        result = super().to_dict()
        
        error_details = {}
        if self.required_permissions:
            error_details["required_permissions"] = self.required_permissions
        if self.current_permissions:
            error_details["current_permissions"] = self.current_permissions
        
        if error_details:
            result["error_details"] = error_details
            
        return result

class RateLimitAPIException(APIException):
    """Exception for rate limiting errors"""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: int = 0,
        reset_time: Optional[datetime] = None,
        retry_after: int = 60,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            error_type="rate_limit",
            retry_after=retry_after,
            **kwargs
        )
        self.limit = limit
        self.reset_time = reset_time or (datetime.utcnow().timestamp() + retry_after)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert rate limit exception to dictionary"""
        result = super().to_dict()
        
        error_details = {
            "limit": self.limit,
            "reset_time": datetime.fromtimestamp(self.reset_time).isoformat(),
            "remaining": 0
        }
        
        result["error_details"] = error_details
        return result

class NotFoundAPIException(APIException):
    """Exception for resource not found errors"""
    
    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: str = "resource",
        resource_id: Optional[str] = None,
        **kwargs
    ):
        if resource_id:
            full_message = f"{resource_type.title()} not found: {resource_id}"
        else:
            full_message = f"{resource_type.title()} not found"
        
        super().__init__(
            message=full_message,
            error_code="NOT_FOUND",
            error_type="not_found",
            **kwargs
        )
        self.resource_type = resource_type
        self.resource_id = resource_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert not found exception to dictionary"""
        result = super().to_dict()
        
        error_details = {
            "resource_type": self.resource_type
        }
        if self.resource_id:
            error_details["resource_id"] = self.resource_id
        
        result["error_details"] = error_details
        return result

class ConflictAPIException(APIException):
    """Exception for conflict errors"""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        conflict_type: str = "general",
        conflicting_resource: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            error_type="conflict",
            **kwargs
        )
        self.conflict_type = conflict_type
        self.conflicting_resource = conflicting_resource
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conflict exception to dictionary"""
        result = super().to_dict()
        
        error_details = {
            "conflict_type": self.conflict_type
        }
        if self.conflicting_resource:
            error_details["conflicting_resource"] = self.conflicting_resource
        
        result["error_details"] = error_details
        return result

class BadRequestAPIException(APIException):
    """Exception for bad request errors"""
    
    def __init__(
        self,
        message: str = "Bad request",
        request_details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="BAD_REQUEST",
            error_type="bad_request",
            **kwargs
        )
        self.request_details = request_details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert bad request exception to dictionary"""
        result = super().to_dict()
        
        if self.request_details:
            result["error_details"] = self.request_details
            
        return result

class ServiceUnavailableAPIException(APIException):
    """Exception for service unavailable errors"""
    
    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        service_name: Optional[str] = None,
        retry_after: int = 300,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            error_type="service_unavailable",
            retry_after=retry_after,
            **kwargs
        )
        self.service_name = service_name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert service unavailable exception to dictionary"""
        result = super().to_dict()
        
        error_details = {}
        if self.service_name:
            error_details["service_name"] = self.service_name
        
        if error_details:
            result["error_details"] = error_details
            
        return result

class TimeoutAPIException(APIException):
    """Exception for timeout errors"""
    
    def __init__(
        self,
        message: str = "Request timeout",
        timeout_seconds: Optional[int] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="TIMEOUT",
            error_type="timeout",
            **kwargs
        )
        self.timeout_seconds = timeout_seconds
        self.operation = operation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert timeout exception to dictionary"""
        result = super().to_dict()
        
        error_details = {}
        if self.timeout_seconds:
            error_details["timeout_seconds"] = self.timeout_seconds
        if self.operation:
            error_details["operation"] = self.operation
        
        if error_details:
            result["error_details"] = error_details
            
        return result

class QuotaExceededAPIException(APIException):
    """Exception for quota exceeded errors"""
    
    def __init__(
        self,
        message: str = "Quota exceeded",
        quota_type: str = "general",
        current_usage: int = 0,
        quota_limit: int = 0,
        reset_time: Optional[datetime] = None,
        **kwargs
    ):
        super().__init__(
            message=message,
            error_code="QUOTA_EXCEEDED",
            error_type="quota_exceeded",
            **kwargs
        )
        self.quota_type = quota_type
        self.current_usage = current_usage
        self.quota_limit = quota_limit
        self.reset_time = reset_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert quota exceeded exception to dictionary"""
        result = super().to_dict()
        
        error_details = {
            "quota_type": self.quota_type,
            "current_usage": self.current_usage,
            "quota_limit": self.quota_limit
        }
        if self.reset_time:
            error_details["reset_time"] = self.reset_time.isoformat()
        
        result["error_details"] = error_details
        return result

# Utility functions for creating common exceptions
def create_validation_error(field: str, message: str, value: Any = None) -> ValidationAPIException:
    """Create a validation error for a specific field"""
    return ValidationAPIException.from_field_error(field, message, value)

def create_not_found_error(resource_type: str, resource_id: Optional[str] = None) -> NotFoundAPIException:
    """Create a not found error"""
    return NotFoundAPIException(resource_type=resource_type, resource_id=resource_id)

def create_auth_error(message: str = "Authentication required") -> AuthenticationAPIException:
    """Create an authentication error"""
    return AuthenticationAPIException(message=message)

def create_rate_limit_error(limit: int, retry_after: int = 60) -> RateLimitAPIException:
    """Create a rate limit error"""
    return RateLimitAPIException(limit=limit, retry_after=retry_after)

def create_permission_error(required_permissions: List[str]) -> AuthorizationAPIException:
    """Create an authorization error"""
    return AuthorizationAPIException(
        message="Insufficient permissions",
        required_permissions=required_permissions
    )

def create_service_unavailable_error(service_name: str, retry_after: int = 300) -> ServiceUnavailableAPIException:
    """Create a service unavailable error"""
    return ServiceUnavailableAPIException(
        message=f"Service {service_name} is temporarily unavailable",
        service_name=service_name,
        retry_after=retry_after
    )
