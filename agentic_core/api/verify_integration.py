"""
Shared API Layer Verification Script
LEVEL 5 - Simple verification that core components work correctly
"""

import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime

def verify_core_components():
    """Verify that core shared API components work correctly"""
    print("🔍 Verifying Shared API Layer Components...")
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Import core models
    total_tests += 1
    try:
        from agentic_core.api import (
            BaseRequest, BaseResponse, PaginatedRequest, PaginatedResponse, SearchRequest, ErrorResponse
        )
        
        from agentic_core.api import (
            create_success_response, create_error_response, create_paginated_response, APIResponse, ResponseFormatter
        )
        
        from agentic_core.api import (
            rate_limit, validate_request, handle_errors, log_api_calls, RateLimiter
        )
        
        from agentic_core.api import (
            APIException, ValidationAPIException, AuthenticationAPIException, RateLimitAPIException
        )
        
        # Test basic functionality
        request = BaseRequest(user_id="test_user")
        response = BaseResponse(success=True, message="Test response")
        
        assert request.request_id is not None
        assert response.success is True
        print("✅ Core models import and basic functionality work")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Core models failed: {e}")
    
    # Test 2: Import response utilities
    total_tests += 1
    try:
        from agentic_core.api import (
            create_success_response, create_error_response, 
            create_paginated_response, APIResponse, ResponseFormatter
        )
        
        # Test response creation
        success_resp = create_success_response(data={"test": True})
        error_resp = create_error_response(error_code="TEST_ERROR", message="Test error")
        
        assert success_resp["success"] is True
        assert error_resp["success"] is False
        
        print("✅ Response utilities import and work correctly")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Response utilities failed: {e}")
    
    # Test 3: Import decorators
    total_tests += 1
    try:
        from agentic_core.api import (
            rate_limit, validate_request, handle_errors, 
            log_api_calls, RateLimiter
        )
        
        # Test rate limiter
        limiter = RateLimiter()
        allowed, reset_time = limiter.is_allowed("test_key", 5, 60)
        assert allowed is True
        
        print("✅ Decorators import and rate limiter works")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Decorators failed: {e}")
    
    # Test 4: Import exceptions
    total_tests += 1
    try:
        from agentic_core.api import (
            APIException, ValidationAPIException, 
            AuthenticationAPIException, RateLimitAPIException
        )
        
        # Test exception creation
        exc = APIException(message="Test exception", error_code="TEST")
        exc_dict = exc.to_dict()
        
        assert exc_dict["success"] is False
        assert exc_dict["error_code"] == "TEST"
        
        print("✅ Exceptions import and serialization works")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Exceptions failed: {e}")
    
    # Test 5: Test pagination functionality
    total_tests += 1
    try:
        from agentic_core.api import PaginatedRequest, create_paginated_response
        
        request = PaginatedRequest(page=1, page_size=20)
        response = create_paginated_response(
            data=["item1", "item2"], 
            page=request.page, 
            page_size=request.page_size, 
            total_items=100
        )
        
        assert response["success"] is True
        assert response["pagination"]["page"] == 1
        assert response["pagination"]["total_items"] == 100
        
        print("✅ Pagination functionality works")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Pagination failed: {e}")
    
    # Test 6: Test validation exceptions
    total_tests += 1
    try:
        from agentic_core.api import ValidationAPIException
        
        validation_exc = ValidationAPIException.from_field_error("email", "Invalid email")
        assert len(validation_exc.validation_errors) == 1
        assert validation_exc.validation_errors[0]["field"] == "email"
        
        print("✅ Validation exceptions work")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Validation exceptions failed: {e}")
    
    # Test 7: Test response formatting
    total_tests += 1
    try:
        from agentic_core.api import ResponseFormatter
        
        # Test sanitization
        metadata = {"name": "John", "password": "secret", "api_key": "abc123"}
        clean = ResponseFormatter.sanitize_metadata(metadata)
        
        assert "name" in clean
        assert "password" not in clean
        assert "api_key" not in clean
        
        print("✅ Response formatting works")
        success_count += 1
        
    except Exception as e:
        print(f"❌ Response formatting failed: {e}")
    
    # Test 8: Check middleware availability (optional)
    total_tests += 1
    try:
        from agentic_core.api import _MIDDLEWARE_AVAILABLE
        
        if _MIDDLEWARE_AVAILABLE:
            print("✅ FastAPI middleware is available")
        else:
            print("ℹ️  FastAPI middleware not available (FastAPI not installed)")
        
        success_count += 1
        
    except Exception as e:
        print(f"❌ Middleware check failed: {e}")
    
    # Summary
    print(f"\n📊 VERIFICATION SUMMARY:")
    print(f"   Passed: {success_count}/{total_tests} tests")
    print(f"   Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 SHARED API LAYER IS READY FOR ENGINE INTEGRATION!")
        return True
    else:
        print("⚠️  Some components have issues - review failures above")
        return False

if __name__ == "__main__":
    success = verify_core_components()
    exit(0 if success else 1)
