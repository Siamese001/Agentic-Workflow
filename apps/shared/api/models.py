"""
Shared API Models
LEVEL 5 - Common request/response models for API layer
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class HTTPMethod(str, Enum):
    """HTTP methods supported"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class RequestPriority(str, Enum):
    """Request priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class SortOrder(str, Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"

class BaseRequest(BaseModel):
    """Base request model with common fields"""
    
    request_id: Optional[UUID] = Field(
        default_factory=uuid4,
        description="Unique identifier for this request"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Request timestamp"
    )
    client_version: Optional[str] = Field(
        None,
        description="Client application version"
    )
    user_id: Optional[str] = Field(
        None,
        description="User identifier for tracking"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier"
    )
    priority: RequestPriority = Field(
        RequestPriority.NORMAL,
        description="Request processing priority"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional request metadata"
    )
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

class PaginatedRequest(BaseRequest):
    """Base request with pagination support"""
    
    page: int = Field(
        1,
        ge=1,
        description="Page number (1-based)"
    )
    page_size: int = Field(
        20,
        ge=1,
        le=100,
        description="Number of items per page"
    )
    sort_by: Optional[str] = Field(
        None,
        description="Field to sort by"
    )
    sort_order: SortOrder = Field(
        SortOrder.ASC,
        description="Sort direction"
    )
    
    @validator("page_size")
    def validate_page_size(cls, v):
        """Validate page size limits"""
        if v > 100:
            raise ValueError("Page size cannot exceed 100 items")
        if v < 1:
            raise ValueError("Page size must be at least 1")
        return v
    
    def get_offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.page_size
    
    def get_limit(self) -> int:
        """Get limit for database queries"""
        return self.page_size

class SearchRequest(PaginatedRequest):
    """Base request with search capabilities"""
    
    query: Optional[str] = Field(
        None,
        description="Search query string"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Search filters"
    )
    search_fields: Optional[List[str]] = Field(
        None,
        description="Fields to search in"
    )
    fuzzy_search: bool = Field(
        False,
        description="Enable fuzzy search"
    )
    
    @validator("query")
    def validate_query(cls, v):
        """Validate search query"""
        if v is not None:
            v = v.strip()
            if len(v) > 500:
                raise ValueError("Search query cannot exceed 500 characters")
        return v

class FilterRequest(PaginatedRequest):
    """Base request with advanced filtering"""
    
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Filter criteria"
    )
    filter_logic: str = Field(
        "AND",
        description="Logic for combining filters (AND/OR)"
    )
    
    @validator("filter_logic")
    def validate_filter_logic(cls, v):
        """Validate filter logic"""
        if v.upper() not in ["AND", "OR"]:
            raise ValueError("Filter logic must be AND or OR")
        return v.upper()

class BaseResponse(BaseModel):
    """Base response model with common fields"""
    
    success: bool = Field(..., description="Whether the request was successful")
    request_id: Optional[UUID] = Field(
        None,
        description="Request identifier echoed back"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )
    processing_time_ms: Optional[float] = Field(
        None,
        description="Time taken to process request in milliseconds"
    )
    message: Optional[str] = Field(
        None,
        description="Human-readable message"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional response metadata"
    )
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

class PaginatedResponse(BaseResponse):
    """Base response with pagination information"""
    
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    
    @validator("total_pages")
    def calculate_total_pages(cls, v, values):
        """Calculate total pages from total items and page size"""
        if "total_items" in values and "page_size" in values:
            total_items = values["total_items"]
            page_size = values["page_size"]
            if page_size > 0:
                return (total_items + page_size - 1) // page_size
        return v

class SearchResponse(PaginatedResponse):
    """Base response with search results"""
    
    query: Optional[str] = Field(None, description="Search query that was executed")
    search_time_ms: Optional[float] = Field(None, description="Time taken for search in milliseconds")
    result_count: int = Field(..., description="Number of results returned")
    
    @validator("result_count")
    def validate_result_count(cls, v, values):
        """Ensure result count doesn't exceed page size"""
        if "page_size" in values and v > values["page_size"]:
            raise ValueError("Result count cannot exceed page size")
        return v

class ErrorResponse(BaseResponse):
    """Error response model"""
    
    success: bool = Field(False, description="Always false for error responses")
    error_code: str = Field(..., description="Machine-readable error code")
    error_type: str = Field(..., description="Error type/category")
    error_details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )
    stack_trace: Optional[str] = Field(
        None,
        description="Stack trace (development only)"
    )
    retry_after: Optional[int] = Field(
        None,
        description="Seconds to wait before retrying"
    )
    
    class Config:
        use_enum_values = True

class ValidationErrorResponse(ErrorResponse):
    """Validation error response with field-specific errors"""
    
    validation_errors: List[Dict[str, Any]] = Field(
        ...,
        description="List of validation errors"
    )
    
    @validator("validation_errors")
    def validate_validation_errors(cls, v):
        """Ensure validation errors have required structure"""
        for error in v:
            if "field" not in error or "message" not in error:
                raise ValueError("Each validation error must have 'field' and 'message'")
        return v

class RateLimitResponse(ErrorResponse):
    """Rate limit exceeded response"""
    
    error_code: str = Field("RATE_LIMIT_EXCEEDED", description="Rate limit error code")
    error_type: str = Field("rate_limit", description="Rate limit error type")
    limit: int = Field(..., description="Request limit")
    remaining: int = Field(0, description="Remaining requests")
    reset_time: datetime = Field(..., description="When limit resets")
    retry_after: int = Field(..., description="Seconds to wait before retry")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AuthenticationResponse(ErrorResponse):
    """Authentication error response"""
    
    error_code: str = Field("AUTHENTICATION_FAILED", description="Auth error code")
    error_type: str = Field("authentication", description="Auth error type")
    auth_method: Optional[str] = Field(None, description="Authentication method used")
    required_scopes: Optional[List[str]] = Field(None, description="Required permission scopes")

class HealthCheckResponse(BaseResponse):
    """Health check response"""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    dependencies: Optional[Dict[str, str]] = Field(
        None,
        description="Dependency statuses"
    )
    metrics: Optional[Dict[str, Any]] = Field(
        None,
        description="Service metrics"
    )

class BatchRequest(BaseRequest):
    """Batch request for multiple operations"""
    
    operations: List[Dict[str, Any]] = Field(
        ...,
        description="List of operations to perform"
    )
    stop_on_first_error: bool = Field(
        False,
        description="Stop processing on first error"
    )
    return_individual_results: bool = Field(
        True,
        description="Return results for each operation"
    )
    
    @validator("operations")
    def validate_operations(cls, v):
        """Validate operations list"""
        if not v:
            raise ValueError("Operations list cannot be empty")
        if len(v) > 100:
            raise ValueError("Cannot process more than 100 operations in a batch")
        return v

class BatchResponse(BaseResponse):
    """Batch response for multiple operations"""
    
    total_operations: int = Field(..., description="Total operations processed")
    successful_operations: int = Field(..., description="Number of successful operations")
    failed_operations: int = Field(..., description="Number of failed operations")
    operation_results: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Results for individual operations"
    )
    
    @validator("successful_operations", "failed_operations")
    def validate_operation_counts(cls, v, values):
        """Ensure operation counts are consistent"""
        if "total_operations" in values:
            total = values["total_operations"]
            successful = values.get("successful_operations", 0)
            failed = values.get("failed_operations", 0)
            if successful + failed > total:
                raise ValueError("Operation counts exceed total operations")
        return v

# Common field types for reuse
class TimestampField(BaseModel):
    """Standard timestamp field"""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class MetadataField(BaseModel):
    """Standard metadata field"""
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Tags for categorization"
    )
