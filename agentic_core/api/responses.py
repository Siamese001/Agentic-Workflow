"""
Shared API Response Utilities
LEVEL 5 - Common response creation and formatting utilities
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import UUID
import json


class APIResponse:
    """Utility class for creating consistent API responses"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation completed successfully",
        request_id: Optional[UUID] = None,
        processing_time_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a success response"""
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }

        if request_id:
            response["request_id"] = str(request_id)
        if processing_time_ms is not None:
            response["processing_time_ms"] = processing_time_ms
        if metadata:
            response["metadata"] = metadata

        return response

    @staticmethod
    def error(
        error_code: str,
        message: str,
        error_type: str = "general",
        error_details: Optional[Dict[str, Any]] = None,
        request_id: Optional[UUID] = None,
        stack_trace: Optional[str] = None,
        retry_after: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create an error response"""
        response = {
            "success": False,
            "error_code": error_code,
            "error_type": error_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }

        if request_id:
            response["request_id"] = str(request_id)
        if error_details:
            response["error_details"] = error_details
        if stack_trace:
            response["stack_trace"] = stack_trace
        if retry_after is not None:
            response["retry_after"] = retry_after
        if metadata:
            response["metadata"] = metadata

        return response

    @staticmethod
    def validation_error(
        validation_errors: List[Dict[str, Any]],
        message: str = "Validation failed",
        request_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a validation error response"""
        return APIResponse.error(
            error_code="VALIDATION_FAILED",
            message=message,
            error_type="validation",
            error_details={"validation_errors": validation_errors},
            request_id=request_id,
            metadata=metadata
        )

    @staticmethod
    def not_found(
        resource: str = "Resource",
        resource_id: Optional[str] = None,
        request_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a not found error response"""
        message = f"{resource} not found"
        if resource_id:
            message += f" with ID: {resource_id}"

        return APIResponse.error(
            error_code="NOT_FOUND",
            message=message,
            error_type="not_found",
            request_id=request_id
        )

    @staticmethod
    def unauthorized(
        message: str = "Authentication required",
        auth_method: Optional[str] = None,
        required_scopes: Optional[List[str]] = None,
        request_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create an unauthorized error response"""
        error_details = {}
        if auth_method:
            error_details["auth_method"] = auth_method
        if required_scopes:
            error_details["required_scopes"] = required_scopes

        return APIResponse.error(
            error_code="UNAUTHORIZED",
            message=message,
            error_type="authentication",
            error_details=error_details if error_details else None,
            request_id=request_id
        )

    @staticmethod
    def forbidden(
        message: str = "Access denied",
        required_permissions: Optional[List[str]] = None,
        request_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a forbidden error response"""
        error_details = {}
        if required_permissions:
            error_details["required_permissions"] = required_permissions

        return APIResponse.error(
            error_code="FORBIDDEN",
            message=message,
            error_type="authorization",
            error_details=error_details if error_details else None,
            request_id=request_id
        )

    @staticmethod
    def rate_limit(
        limit: int,
        reset_time: datetime,
        retry_after: int,
        request_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a rate limit error response"""
        return APIResponse.error(
            error_code="RATE_LIMIT_EXCEEDED",
            message="Rate limit exceeded",
            error_type="rate_limit",
            error_details={
                "limit": limit,
                "reset_time": reset_time.isoformat(),
                "remaining": 0
            },
            retry_after=retry_after,
            request_id=request_id
        )

    @staticmethod
    def paginated(
        data: List[Any],
        page: int,
        page_size: int,
        total_items: int,
        message: str = "Data retrieved successfully",
        request_id: Optional[UUID] = None,
        processing_time_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a paginated response"""
        total_pages = (total_items + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1

        response = APIResponse.success(
            data=data,
            message=message,
            request_id=request_id,
            processing_time_ms=processing_time_ms,
            metadata=metadata
        )

        # Add pagination info
        response.update({
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous
            }
        })

        return response

    @staticmethod
    def search(
        data: List[Any],
        query: str,
        page: int,
        page_size: int,
        total_items: int,
        search_time_ms: Optional[float] = None,
        message: str = "Search completed successfully",
        request_id: Optional[UUID] = None,
        processing_time_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a search response"""
        response = APIResponse.paginated(
            data=data,
            page=page,
            page_size=page_size,
            total_items=total_items,
            message=message,
            request_id=request_id,
            processing_time_ms=processing_time_ms,
            metadata=metadata
        )

        # Add search info
        search_info = {
            "query": query,
            "result_count": len(data)
        }
        if search_time_ms is not None:
            search_info["search_time_ms"] = search_time_ms

        response["search"] = search_info

        return response

    @staticmethod
    def health_check(
        status: str,
        version: str,
        uptime_seconds: float,
        dependencies: Optional[Dict[str, str]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        message: str = "Health check completed"
    ) -> Dict[str, Any]:
        """Create a health check response"""
        response = {
            "success": True,
            "status": status,
            "version": version,
            "uptime_seconds": uptime_seconds,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        }

        if dependencies:
            response["dependencies"] = dependencies
        if metrics:
            response["metrics"] = metrics

        return response

    @staticmethod
    def batch(
        operation_results: List[Dict[str, Any]],
        successful_operations: int,
        failed_operations: int,
        message: str = "Batch operation completed",
        request_id: Optional[UUID] = None,
        processing_time_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a batch operation response"""
        total_operations = successful_operations + failed_operations

        response = APIResponse.success(
            data=operation_results,
            message=message,
            request_id=request_id,
            processing_time_ms=processing_time_ms,
            metadata=metadata
        )

        # Add batch info
        response.update({
            "batch": {
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "failed_operations": failed_operations
            }
        })

        return response

# Convenience functions for common response types
def create_success_response(**kwargs) -> Dict[str, Any]:
    """Create a success response"""
    return APIResponse.success(**kwargs)

def create_error_response(**kwargs) -> Dict[str, Any]:
    """Create an error response"""
    return APIResponse.error(**kwargs)

def create_validation_response(**kwargs) -> Dict[str, Any]:
    """Create a validation error response"""
    return APIResponse.validation_error(**kwargs)

def create_not_found_response(**kwargs) -> Dict[str, Any]:
    """Create a not found response"""
    return APIResponse.not_found(**kwargs)

def create_unauthorized_response(**kwargs) -> Dict[str, Any]:
    """Create an unauthorized response"""
    return APIResponse.unauthorized(**kwargs)

def create_forbidden_response(**kwargs) -> Dict[str, Any]:
    """Create a forbidden response"""
    return APIResponse.forbidden(**kwargs)

def create_rate_limit_response(**kwargs) -> Dict[str, Any]:
    """Create a rate limit response"""
    return APIResponse.rate_limit(**kwargs)

def create_paginated_response(**kwargs) -> Dict[str, Any]:
    """Create a paginated response"""
    return APIResponse.paginated(**kwargs)

def create_search_response(**kwargs) -> Dict[str, Any]:
    """Create a search response"""
    return APIResponse.search(**kwargs)

def create_health_check_response(**kwargs) -> Dict[str, Any]:
    """Create a health check response"""
    return APIResponse.health_check(**kwargs)

def create_batch_response(**kwargs) -> Dict[str, Any]:
    """Create a batch response"""
    return APIResponse.batch(**kwargs)

# Response formatting utilities
class ResponseFormatter:
    """Utility class for formatting response data"""

    @staticmethod
    def format_timestamp(dt: datetime) -> str:
        """Format datetime for API responses"""
        return dt.isoformat()

    @staticmethod
    def format_uuid(uuid_obj: UUID) -> str:
        """Format UUID for API responses"""
        return str(uuid_obj)

    @staticmethod
    def sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata for API responses"""
        if not metadata:
            return {}

        # Remove sensitive keys
        sensitive_keys = ["password", "token", "secret", "key", "auth"]
        sanitized = {}

        for key, value in metadata.items():
            if not any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = value

        return sanitized

    @staticmethod
    def format_error_details(error_details: Dict[str, Any]) -> Dict[str, Any]:
        """Format error details for API responses"""
        if not error_details:
            return {}

        # Ensure error details are JSON serializable
        try:
            json.dumps(error_details)
            return error_details
        except (TypeError, ValueError):
            # Convert non-serializable objects to strings
            formatted = {}
            for key, value in error_details.items():
                try:
                    json.dumps(value)
                    formatted[key] = value
                except (TypeError, ValueError):
                    formatted[key] = str(value)
            return formatted

    @staticmethod
    def truncate_string(value: str, max_length: int = 1000) -> str:
        """Truncate string for API responses"""
        if not value or len(value) <= max_length:
            return value
        return value[:max_length] + "... (truncated)"

    @staticmethod
    def format_list_response(
        items: List[Any],
        max_items: int = 1000,
        truncate_strings: bool = True,
        max_string_length: int = 500
    ) -> List[Any]:
        """Format list for API responses"""
        if not items:
            return []

        # Limit number of items
        formatted_items = items[:max_items]

        if truncate_strings:
            # Truncate string values in items
            result = []
            for item in formatted_items:
                if isinstance(item, str):
                    result.append(ResponseFormatter.truncate_string(item, max_string_length))
                elif isinstance(item, dict):
                    formatted_dict = {}
                    for key, value in item.items():
                        if isinstance(value, str):
                            formatted_dict[key] = ResponseFormatter.truncate_string(value, max_string_length)
                        else:
                            formatted_dict[key] = value
                    result.append(formatted_dict)
                else:
                    result.append(item)
            return result

        return formatted_items
