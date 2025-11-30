"""
Example Engine Integration
LEVEL 5 - Simple FastAPI app demonstrating shared API layer usage
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Import shared API components
try:
    from apps.shared.api import (
        BaseRequest,
        BaseResponse,
        PaginatedRequest,
        SearchRequest,
        create_success_response,
        create_error_response,
        create_paginated_response,
        create_search_response,
        create_not_found_response,
        create_validation_response,
        rate_limit,
        handle_errors,
        validate_request,
        log_api_calls,
        APIException,
        ValidationAPIException,
        NotFoundAPIException,
        RateLimiter
    )
    
    # Try to import middleware if FastAPI is available
    try:
        from apps.shared.api import (
            add_shared_middleware,
            DEFAULT_CORS_CONFIG
        )
        MIDDLEWARE_AVAILABLE = True
    except ImportError:
        MIDDLEWARE_AVAILABLE = False
    
    SHARED_API_AVAILABLE = True
    
except ImportError as e:
    print(f"Shared API not available: {e}")
    SHARED_API_AVAILABLE = False
    MIDDLEWARE_AVAILABLE = False

# Example engine-specific models
class ResumeRequest(BaseModel):
    """Resume generation request"""
    name: str
    email: str
    experience_years: int
    skills: List[str]
    target_job: str

class ResumeResponse(BaseModel):
    """Resume generation response"""
    resume_id: str
    content: str
    generated_at: str

class ContactRequest(BaseModel):
    """Contact search request"""
    name: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None

class ContactResponse(BaseModel):
    """Contact search response"""
    contact_id: str
    name: str
    email: str
    company: str
    location: str

# Create FastAPI application
app = FastAPI(
    title="Example Engine API",
    description="Demonstrating shared API layer integration",
    version="1.0.0"
)

# Add shared middleware if available
if SHARED_API_AVAILABLE and MIDDLEWARE_AVAILABLE:
    add_shared_middleware(
        app,
        enable_request_id=True,
        enable_timing=True,
        enable_logging=True,
        enable_error_handling=True,
        enable_security_headers=True,
        cors_config={
            "allow_origins": ["*"],  # Restrict in production
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["*"]
        }
    )
    print("✅ Shared middleware added successfully")
else:
    print("ℹ️  Shared middleware not available (FastAPI dependencies missing)")

# Mock data for demonstration
MOCK_RESUMES = [
    {"id": "1", "name": "John Doe", "email": "john@example.com", "content": "Software Engineer Resume"},
    {"id": "2", "name": "Jane Smith", "email": "jane@example.com", "content": "Data Scientist Resume"},
]

MOCK_CONTACTS = [
    {"id": "1", "name": "Alice Johnson", "email": "alice@company.com", "company": "Tech Corp", "location": "NYC"},
    {"id": "2", "name": "Bob Wilson", "email": "bob@startup.com", "company": "Startup Inc", "location": "SF"},
    {"id": "3", "name": "Carol Davis", "email": "carol@enterprise.com", "company": "Enterprise Ltd", "location": "London"},
]

# Validation functions
def validate_resume_request(request: ResumeRequest) -> None:
    """Validate resume generation request"""
    errors = []
    
    if not request.name or len(request.name.strip()) < 2:
        errors.append({"field": "name", "message": "Name must be at least 2 characters"})
    
    if not request.email or "@" not in request.email:
        errors.append({"field": "email", "message": "Valid email is required"})
    
    if request.experience_years < 0:
        errors.append({"field": "experience_years", "message": "Experience years cannot be negative"})
    
    if not request.skills or len(request.skills) < 3:
        errors.append({"field": "skills", "message": "At least 3 skills are required"})
    
    if errors:
        raise ValidationAPIException(
            message="Resume request validation failed",
            validation_errors=errors
        )

def validate_contact_search(request: SearchRequest) -> None:
    """Validate contact search request"""
    if not request.query and not request.filters:
        raise ValidationAPIException(
            message="Search query or filters are required",
            validation_errors=[{"field": "query", "message": "Provide search query or filters"}]
        )

# API Endpoints demonstrating shared API layer usage

@app.get("/")
async def root():
    """Root endpoint"""
    return create_success_response(
        data={"message": "Example Engine API with Shared Components"},
        message="API is running"
    )

@app.post("/resumes/generate")
@rate_limit(requests_per_minute=5)  # Limit expensive operations
@handle_errors()
@log_api_calls(log_level="info")
async def generate_resume(request: ResumeRequest):
    """Generate a new resume using shared components"""
    try:
        # Validate request using shared validation
        validate_resume_request(request)
        
        # Mock resume generation
        resume_id = f"resume_{len(MOCK_RESUMES) + 1}"
        resume_content = f"""
        Resume for {request.name}
        Email: {request.email}
        Experience: {request.experience_years} years
        Skills: {', '.join(request.skills)}
        Target Job: {request.target_job}
        
        [Resume content would be generated here...]
        """
        
        result = ResumeResponse(
            resume_id=resume_id,
            content=resume_content.strip(),
            generated_at="2025-11-30T12:00:00Z"
        )
        
        return create_success_response(
            data=result.dict(),
            message="Resume generated successfully"
        )
        
    except ValidationAPIException as e:
        # Validation errors are automatically handled by middleware
        raise e
    except Exception as e:
        return create_error_response(
            error_code="RESUME_GENERATION_FAILED",
            message=f"Failed to generate resume: {str(e)}",
            error_type="processing_error"
        )

@app.get("/resumes")
@rate_limit(requests_per_minute=60)
@handle_errors()
async def list_resumes(request: PaginatedRequest):
    """List resumes with pagination using shared components"""
    try:
        # Mock pagination
        start_idx = request.get_offset()
        end_idx = start_idx + request.get_limit()
        
        paginated_resumes = MOCK_RESUMES[start_idx:end_idx]
        
        return create_paginated_response(
            data=paginated_resumes,
            page=request.page,
            page_size=request.page_size,
            total_items=len(MOCK_RESUMES),
            message="Resumes retrieved successfully"
        )
        
    except Exception as e:
        return create_error_response(
            error_code="RESUME_LIST_FAILED",
            message=f"Failed to list resumes: {str(e)}"
        )

@app.post("/contacts/search")
@validate_request(validate_contact_search)
@rate_limit(requests_per_minute=30)
@handle_errors()
async def search_contacts(request: SearchRequest):
    """Search contacts using shared search components"""
    try:
        # Mock search logic
        filtered_contacts = MOCK_CONTACTS.copy()
        
        # Apply filters
        if request.filters:
            if "company" in request.filters:
                company = request.filters["company"]
                filtered_contacts = [c for c in filtered_contacts if company.lower() in c["company"].lower()]
            
            if "location" in request.filters:
                location = request.filters["location"]
                filtered_contacts = [c for c in filtered_contacts if location.lower() in c["location"].lower()]
        
        # Apply text search
        if request.query:
            query = request.query.lower()
            filtered_contacts = [
                c for c in filtered_contacts 
                if query in c["name"].lower() or 
                   query in c["company"].lower() or 
                   query in c["location"].lower()
            ]
        
        # Mock pagination
        start_idx = request.get_offset()
        end_idx = start_idx + request.get_limit()
        paginated_results = filtered_contacts[start_idx:end_idx]
        
        return create_search_response(
            data=paginated_results,
            query=request.query or "",
            page=request.page,
            page_size=request.page_size,
            total_items=len(filtered_contacts),
            search_time_ms=25.5,
            message="Contacts found successfully"
        )
        
    except Exception as e:
        return create_error_response(
            error_code="CONTACT_SEARCH_FAILED",
            message=f"Search failed: {str(e)}"
        )

@app.get("/contacts/{contact_id}")
@handle_errors()
async def get_contact(contact_id: str):
    """Get specific contact using shared error handling"""
    try:
        # Find contact
        contact = next((c for c in MOCK_CONTACTS if c["id"] == contact_id), None)
        
        if not contact:
            raise NotFoundAPIException(
                resource_type="contact",
                resource_id=contact_id
            )
        
        return create_success_response(
            data=contact,
            message="Contact retrieved successfully"
        )
        
    except NotFoundAPIException as e:
        raise e
    except Exception as e:
        return create_error_response(
            error_code="CONTACT_GET_FAILED",
            message=f"Failed to get contact: {str(e)}"
        )

@app.post("/batch/process")
@rate_limit(requests_per_minute=10)
@handle_errors()
async def batch_process(request: Dict[str, Any]):
    """Batch processing example using shared components"""
    try:
        operations = request.get("operations", [])
        results = []
        success_count = 0
        error_count = 0
        
        for i, op in enumerate(operations):
            try:
                # Mock processing
                operation_type = op.get("type")
                operation_id = f"op_{i+1}"
                
                if operation_type == "generate_resume":
                    results.append({
                        "operation_id": operation_id,
                        "status": "success",
                        "result": {"resume_id": f"batch_resume_{i+1}"}
                    })
                    success_count += 1
                elif operation_type == "search_contact":
                    results.append({
                        "operation_id": operation_id,
                        "status": "success",
                        "result": {"contacts_found": 3}
                    })
                    success_count += 1
                else:
                    results.append({
                        "operation_id": operation_id,
                        "status": "error",
                        "error": f"Unknown operation type: {operation_type}"
                    })
                    error_count += 1
                    
            except Exception as e:
                results.append({
                    "operation_id": f"op_{i+1}",
                    "status": "error",
                    "error": str(e)
                })
                error_count += 1
        
        return create_success_response(
            data=results,
            message=f"Batch processing completed: {success_count} successful, {error_count} failed"
        )
        
    except Exception as e:
        return create_error_response(
            error_code="BATCH_PROCESS_FAILED",
            message=f"Batch processing failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check using shared components"""
    health_data = {
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": 3600.0,
        "dependencies": {
            "shared_api": "available" if SHARED_API_AVAILABLE else "unavailable",
            "middleware": "available" if MIDDLEWARE_AVAILABLE else "unavailable"
        },
        "metrics": {
            "total_endpoints": 6,
            "rate_limited_endpoints": 3,
            "validated_endpoints": 1
        }
    }
    
    return create_success_response(
        data=health_data,
        message="Service is healthy"
    )

# Error handling demonstration
@app.get("/test/error")
async def test_error():
    """Test error handling with shared components"""
    raise APIException(
        message="This is a test error",
        error_code="TEST_ERROR",
        error_type="test"
    )

@app.get("/test/validation")
async def test_validation():
    """Test validation error with shared components"""
    raise ValidationAPIException.from_field_error(
        field="test_field",
        message="This field is invalid for testing"
    )

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Example Engine API with Shared Components")
    print(f"✅ Shared API Available: {SHARED_API_AVAILABLE}")
    print(f"✅ Middleware Available: {MIDDLEWARE_AVAILABLE}")
    print("📚 Available endpoints:")
    print("   GET  /                    - Root endpoint")
    print("   POST /resumes/generate    - Generate resume (rate limited: 5/min)")
    print("   GET  /resumes             - List resumes (rate limited: 60/min)")
    print("   POST /contacts/search     - Search contacts (rate limited: 30/min)")
    print("   GET  /contacts/{id}       - Get specific contact")
    print("   POST /batch/process       - Batch processing (rate limited: 10/min)")
    print("   GET  /health              - Health check")
    print("   GET  /test/error          - Test error handling")
    print("   GET  /test/validation     - Test validation errors")
    print("\n🌐 Server will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
