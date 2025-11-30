# Shared API Components

LEVEL 5 - Common API patterns, models, and utilities shared across engines

## Overview

The shared API layer provides a comprehensive foundation for both `resume_engine` and `outreach_engine` to ensure consistent API behavior, error handling, and response formatting across all services.

## Architecture

```
apps/shared/api/
├── __init__.py           # Main exports
├── models.py            # Request/response models
├── responses.py         # Response utilities and formatters
├── decorators.py        # API decorators (rate limiting, auth, etc.)
├── exceptions.py        # Custom exception hierarchy
├── middleware.py        # FastAPI middleware components
├── test_integration.py  # Integration test suite
└── README.md           # This documentation
```

## Quick Start

### Basic FastAPI Application Setup

```python
from fastapi import FastAPI
from apps.shared.api import add_shared_middleware, DEFAULT_CORS_CONFIG

# Create FastAPI app
app = FastAPI(
    title="My Engine API",
    version="1.0.0"
)

# Add shared middleware stack
add_shared_middleware(
    app,
    enable_request_id=True,
    enable_timing=True,
    enable_logging=True,
    enable_error_handling=True,
    enable_security_headers=True,
    cors_config=DEFAULT_CORS_CONFIG
)
```

### Creating API Endpoints

```python
from fastapi import HTTPException, Depends
from apps.shared.api import (
    BaseRequest, 
    create_success_response,
    create_error_response,
    create_not_found_response,
    rate_limit,
    handle_errors,
    ValidationAPIException,
    NotFoundAPIException
)

@app.post("/process")
@rate_limit(requests_per_minute=30)
@handle_errors()
async def process_data(request: BaseRequest):
    try:
        # Your business logic here
        result = {"processed": True, "data": "example"}
        
        return create_success_response(
            data=result,
            message="Data processed successfully",
            request_id=request.request_id
        )
    
    except ValidationAPIException as e:
        # Validation errors are automatically handled by middleware
        raise e
    except Exception as e:
        # Create custom error response
        return create_error_response(
            error_code="PROCESSING_ERROR",
            message=f"Failed to process data: {str(e)}",
            request_id=request.request_id
        )
```

## Core Components

### 1. Request/Response Models

#### Base Models
```python
from apps.shared.api import BaseRequest, BaseResponse

# Base request with common fields
request = BaseRequest(
    user_id="user123",
    priority="high",
    metadata={"source": "web"}
)

# Base response
response = BaseResponse(
    success=True,
    message="Operation completed",
    request_id=request.request_id
)
```

#### Pagination
```python
from apps.shared.api import PaginatedRequest, PaginatedResponse, create_paginated_response

# Paginated request
request = PaginatedRequest(
    page=1,
    page_size=20,
    sort_by="created_at",
    sort_order="desc"
)

# Paginated response
data = ["item1", "item2", "item3"]
response = create_paginated_response(
    data=data,
    page=request.page,
    page_size=request.page_size,
    total_items=100,
    message="Items retrieved"
)
```

#### Search
```python
from apps.shared.api import SearchRequest, create_search_response

# Search request
request = SearchRequest(
    query="python developer",
    filters={"location": "NYC"},
    fuzzy_search=True
)

# Search response
response = create_search_response(
    data=search_results,
    query=request.query,
    page=1,
    page_size=20,
    total_items=50,
    search_time_ms=150.5
)
```

### 2. Response Utilities

#### Creating Consistent Responses
```python
from apps.shared.api import (
    create_success_response,
    create_error_response,
    create_validation_response,
    create_not_found_response,
    create_unauthorized_response
)

# Success response
success = create_success_response(
    data={"id": 123},
    message="Resource created"
)

# Error response
error = create_error_response(
    error_code="VALIDATION_FAILED",
    message="Invalid input data",
    error_details={"field": "email", "issue": "invalid format"}
)

# Validation error response
validation_error = create_validation_response(
    validation_errors=[
        {"field": "email", "message": "Invalid email format"},
        {"field": "name", "message": "Name is required"}
    ]
)
```

#### Response Formatting
```python
from apps.shared.api import ResponseFormatter

# Sanitize metadata
clean_metadata = ResponseFormatter.sanitize_metadata({
    "name": "John",
    "password": "secret123",  # Will be removed
    "api_key": "abc123"       # Will be removed
})

# Format timestamps
from datetime import datetime
iso_timestamp = ResponseFormatter.format_timestamp(datetime.utcnow())

# Truncate long strings
short_text = ResponseFormatter.truncate_string(long_text, max_length=100)
```

### 3. Decorators

#### Rate Limiting
```python
from apps.shared.api import rate_limit

@app.post("/api/endpoint")
@rate_limit(
    requests_per_minute=60,
    requests_per_hour=1000,
    key_func=lambda request: request.user_id  # Custom rate limit key
)
async def my_endpoint():
    return {"message": "Rate limited endpoint"}
```

#### Request Validation
```python
from apps.shared.api import validate_request, ValidationAPIException

def validate_my_request(request):
    if not request.user_id:
        raise ValidationAPIException(
            message="User ID is required",
            validation_errors=[{"field": "user_id", "message": "Required field"}]
        )

@app.post("/validated")
@validate_request(validate_my_request)
async def validated_endpoint(request: BaseRequest):
    return {"message": "Request is valid"}
```

#### Error Handling
```python
from apps.shared.api import handle_errors

@app.get("/risky")
@handle_errors(
    default_error_message="Operation failed",
    log_errors=True,
    include_stack_trace=False  # Set to True for development
)
async def risky_operation():
    # This will automatically handle exceptions
    raise ValueError("Something went wrong")
```

#### API Logging
```python
from apps.shared.api import log_api_calls

@app.post("/logged")
@log_api_calls(
    log_level="info",
    include_args=False,  # Don't log sensitive arguments
    include_kwargs=True,
    sensitive_params=["password", "token"]
)
async def logged_endpoint(data: dict):
    return {"processed": True}
```

#### Caching
```python
from apps.shared.api import cache_response

@app.get("/expensive-operation")
@cache_response(ttl_seconds=300, max_size=1000)
async def expensive_computation():
    # Result will be cached for 5 minutes
    return {"result": "computed_data"}
```

#### Authentication
```python
from apps.shared.api import require_auth, AuthenticationAPIException

def authenticate_user(request):
    # Your authentication logic here
    token = request.headers.get("Authorization")
    if not token or not validate_token(token):
        raise AuthenticationAPIException(message="Invalid token")
    
    return {"user_id": "123", "scopes": ["read", "write"]}

@app.get("/protected")
@require_auth(authenticate_user, required_scopes=["read"])
async def protected_endpoint(current_user: dict):
    return {"user": current_user}
```

### 4. Exception Handling

#### Custom Exceptions
```python
from apps.shared.api import (
    ValidationAPIException,
    NotFoundAPIException,
    RateLimitAPIException,
    create_validation_error,
    create_not_found_error
)

# Create validation exceptions
validation_exc = create_validation_error(
    field="email",
    message="Invalid email format",
    value="invalid-email"
)

# Create not found exceptions
not_found_exc = create_not_found_error(
    resource_type="user",
    resource_id="123"
)

# Raise exceptions in endpoints
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    user = find_user(user_id)
    if not user:
        raise create_not_found_error("user", user_id)
    return user
```

### 5. Middleware Configuration

#### Individual Middleware
```python
from apps.shared.api import (
    RequestIDMiddleware,
    TimingMiddleware,
    LoggingMiddleware,
    ErrorHandlingMiddleware,
    SecurityHeadersMiddleware
)

# Add individual middleware
app.add_middleware(RequestIDMiddleware, header_name="X-Request-ID")
app.add_middleware(TimingMiddleware, header_name="X-Processing-Time")
app.add_middleware(LoggingMiddleware, log_level="info")
app.add_middleware(ErrorHandlingMiddleware, include_stack_trace=False)
app.add_middleware(SecurityHeadersMiddleware)
```

#### Complete Middleware Stack
```python
from apps.shared.api import add_shared_middleware

# Add all shared middleware with custom configuration
add_shared_middleware(
    app,
    enable_request_id=True,
    enable_timing=True,
    enable_logging=True,
    enable_error_handling=True,
    enable_security_headers=True,
    enable_compression=True,
    cors_config={
        "allow_origins": ["https://app.example.com"],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["*"],
        "expose_headers": ["X-Request-ID", "X-Processing-Time"]
    },
    request_id_header="X-Request-ID",
    timing_header="X-Processing-Time",
    log_level="info",
    log_request_body=False,
    log_response_body=False,
    include_stack_trace=False,
    custom_security_headers={
        "X-Custom-Header": "custom-value"
    }
)
```

## Integration Examples

### Resume Engine Example

```python
# apps/resume_engine/api/v1/endpoints/resumes.py
from fastapi import APIRouter, Depends
from apps.shared.api import (
    PaginatedRequest,
    create_success_response,
    create_not_found_response,
    rate_limit,
    handle_errors
)
from apps.resume_engine.schemas import ResumeRequest, ResumeResponse

router = APIRouter(prefix="/resumes", tags=["resumes"])

@router.post("/generate")
@rate_limit(requests_per_minute=10)  # Limit expensive operations
@handle_errors()
async def generate_resume(request: ResumeRequest):
    """Generate a new resume"""
    try:
        # Use shared request model
        result = await resume_service.generate(request)
        
        return create_success_response(
            data=result,
            message="Resume generated successfully",
            request_id=request.request_id
        )
    except ResumeNotFoundError:
        return create_not_found_response("resume template", request.template_id)

@router.get("/")
@rate_limit(requests_per_minute=60)
async def list_resumes(request: PaginatedRequest):
    """List resumes with pagination"""
    resumes = await resume_service.list(
        page=request.page,
        page_size=request.page_size,
        sort_by=request.sort_by
    )
    
    return create_paginated_response(
        data=resumes,
        page=request.page,
        page_size=request.page_size,
        total_items=await resume_service.count(),
        message="Resumes retrieved successfully"
    )
```

### Outreach Engine Example

```python
# apps/outreach_engine/api/v1/endpoints/outreach.py
from fastapi import APIRouter
from apps.shared.api import (
    SearchRequest,
    create_search_response,
    validate_request,
    ValidationAPIException
)

router = APIRouter(prefix="/outreach", tags=["outreach"])

def validate_outreach_request(request):
    if not request.query:
        raise ValidationAPIException(
            message="Search query is required",
            validation_errors=[{"field": "query", "message": "Required field"}]
        )

@router.post("/search")
@validate_request(validate_outreach_request)
async def search_contacts(request: SearchRequest):
    """Search for contacts"""
    try:
        results = await outreach_service.search(
            query=request.query,
            filters=request.filters,
            page=request.page,
            page_size=request.page_size
        )
        
        return create_search_response(
            data=results,
            query=request.query,
            page=request.page,
            page_size=request.page_size,
            total_items=await outreach_service.count_results(request.query),
            search_time_ms=150.0
        )
    except Exception as e:
        raise ValidationAPIException(
            message=f"Search failed: {str(e)}",
            validation_errors=[{"field": "search", "message": str(e)}]
        )
```

## Testing

### Running Integration Tests

```bash
# Run the integration test to verify all components work together
python apps/shared/api/test_integration.py
```

### Testing in Your Engine

```python
# tests/test_api_integration.py
import pytest
from apps.shared.api import BaseRequest, create_success_response

def test_shared_components():
    """Test that shared components work correctly"""
    request = BaseRequest(user_id="test")
    response = create_success_response(data={"test": True})
    
    assert response["success"] is True
    assert response["data"]["test"] is True
```

## Best Practices

### 1. Consistent Error Handling
- Always use shared exception classes
- Include request IDs in error responses
- Provide meaningful error messages

### 2. Rate Limiting
- Set appropriate limits for different endpoint types
- Use user-specific rate limit keys where possible
- Document rate limits for API consumers

### 3. Logging
- Include request IDs in all log entries
- Sanitize sensitive data before logging
- Use appropriate log levels

### 4. Response Formatting
- Always use shared response creators
- Include processing time metrics
- Sanitize metadata before returning

### 5. Security
- Always enable security headers middleware
- Use authentication decorators for protected endpoints
- Never log sensitive information

## Limitations

### Rate Limiting
- The default `RateLimiter` uses in-memory storage
- Not suitable for multi-instance deployments
- Consider Redis-backed rate limiting for production

### Caching
- Default caching is in-memory only
- Cache is lost on application restart
- Consider external cache (Redis) for production

## Production Considerations

1. **Rate Limiting**: Replace in-memory rate limiter with Redis-backed implementation
2. **Caching**: Use external cache like Redis or Memcached
3. **Logging**: Configure structured logging with proper log levels
4. **Security**: Review CORS configuration for production
5. **Monitoring**: Add metrics collection for API performance

## Migration Guide

### From Individual Engine APIs

1. **Replace request models** with shared `BaseRequest` subclasses
2. **Use shared response creators** instead of manual JSON responses
3. **Add shared middleware** to existing FastAPI apps
4. **Update exception handling** to use shared exception classes
5. **Add rate limiting** to expensive endpoints

### Example Migration

**Before:**
```python
@app.post("/generate")
async def generate_resume(data: dict):
    try:
        result = await generate(data)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**After:**
```python
@app.post("/generate")
@rate_limit(requests_per_minute=10)
@handle_errors()
async def generate_resume(request: BaseRequest):
    result = await generate(request.data)
    return create_success_response(
        data=result,
        message="Resume generated successfully",
        request_id=request.request_id
    )
```

## Support

For questions or issues with the shared API layer:
1. Check the integration tests: `apps/shared/api/test_integration.py`
2. Review the examples in this documentation
3. Consult the individual module documentation
4. Contact the architecture team for design questions
