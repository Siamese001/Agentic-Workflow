"""
Shared API Integration Test
LEVEL 5 - Integration test to verify all shared.api components work correctly
"""

import sys
import traceback
from typing import Dict, Any
from datetime import datetime

def test_imports() -> Dict[str, Any]:
    """Test that all shared.api components can be imported without errors"""
    results = {
        "success": True,
        "import_errors": [],
        "imported_components": [],
        "total_components": 0
    }
    
    # Test imports from main __init__.py
    try:
        from apps.shared.api import (
            BaseRequest,
            BaseResponse,
            PaginatedRequest,
            PaginatedResponse,
            SearchRequest,
            create_success_response,
            create_error_response,
            create_paginated_response,
            APIResponse,
            rate_limit,
            validate_request,
            handle_errors,
            log_api_calls,
            APIException,
            ValidationAPIException,
            AuthenticationAPIException,
            RateLimitAPIException
        )
        
        results["imported_components"].extend([
            "BaseRequest", "BaseResponse", "PaginatedRequest", "PaginatedResponse",
            "SearchRequest", "create_success_response", "create_error_response",
            "create_paginated_response", "APIResponse", "rate_limit", "validate_request",
            "handle_errors", "log_api_calls", "APIException", "ValidationAPIException",
            "AuthenticationAPIException", "RateLimitAPIException"
        ])
        
    except ImportError as e:
        results["success"] = False
        results["import_errors"].append(f"Main import error: {str(e)}")
        return results
    
    # Test direct imports from models
    try:
        from apps.shared.api.models import (
            BaseRequest as BaseModelRequest,
            BaseResponse as BaseModelResponse,
            PaginatedRequest as PaginatedModelRequest,
            PaginatedResponse as PaginatedModelResponse,
            SearchRequest as SearchModelRequest,
            ErrorResponse,
            ValidationErrorResponse,
            RateLimitResponse,
            AuthenticationResponse,
            HealthCheckResponse,
            BatchRequest,
            BatchResponse
        )
        
        results["imported_components"].extend([
            "BaseModelRequest", "BaseModelResponse", "PaginatedModelRequest",
            "PaginatedModelResponse", "SearchModelRequest", "ErrorResponse",
            "ValidationErrorResponse", "RateLimitResponse", "AuthenticationResponse",
            "HealthCheckResponse", "BatchRequest", "BatchResponse"
        ])
        
    except ImportError as e:
        results["success"] = False
        results["import_errors"].append(f"Models import error: {str(e)}")
    
    # Test direct imports from responses
    try:
        from apps.shared.api.responses import (
            APIResponse as ResponseAPIResponse,
            create_success_response as create_success,
            create_error_response as create_error,
            create_validation_response,
            create_not_found_response,
            create_unauthorized_response,
            create_forbidden_response,
            create_rate_limit_response,
            create_paginated_response as create_paginated,
            create_search_response,
            create_health_check_response,
            create_batch_response,
            ResponseFormatter
        )
        
        results["imported_components"].extend([
            "ResponseAPIResponse", "create_success", "create_error",
            "create_validation_response", "create_not_found_response",
            "create_unauthorized_response", "create_forbidden_response",
            "create_rate_limit_response", "create_paginated", "create_search_response",
            "create_health_check_response", "create_batch_response", "ResponseFormatter"
        ])
        
    except ImportError as e:
        results["success"] = False
        results["import_errors"].append(f"Responses import error: {str(e)}")
    
    # Test direct imports from decorators
    try:
        from apps.shared.api.decorators import (
            rate_limit as rate_limit_decorator,
            validate_request as validate_decorator,
            handle_errors as handle_errors_decorator,
            log_api_calls as log_decorator,
            cache_response as cache_decorator,
            require_auth as auth_decorator,
            RateLimiter
        )
        
        results["imported_components"].extend([
            "rate_limit_decorator", "validate_decorator", "handle_errors_decorator",
            "log_decorator", "cache_decorator", "auth_decorator", "RateLimiter"
        ])
        
    except ImportError as e:
        results["success"] = False
        results["import_errors"].append(f"Decorators import error: {str(e)}")
    
    # Test direct imports from exceptions
    try:
        from apps.shared.api.exceptions import (
            APIException as ExceptionAPIException,
            ValidationAPIException as ExceptionValidationAPIException,
            AuthenticationAPIException as ExceptionAuthAPIException,
            AuthorizationAPIException,
            RateLimitAPIException as ExceptionRateLimitAPIException,
            NotFoundAPIException,
            ConflictAPIException,
            BadRequestAPIException,
            ServiceUnavailableAPIException,
            TimeoutAPIException,
            QuotaExceededAPIException,
            create_validation_error as create_validation_exc,
            create_not_found_error as create_not_found_exc,
            create_auth_error as create_auth_exc,
            create_rate_limit_error as create_rate_limit_exc,
            create_permission_error as create_permission_exc,
            create_service_unavailable_error as create_service_unavailable_exc
        )
        
        results["imported_components"].extend([
            "ExceptionAPIException", "ExceptionValidationAPIException",
            "ExceptionAuthAPIException", "AuthorizationAPIException",
            "ExceptionRateLimitAPIException", "NotFoundAPIException",
            "ConflictAPIException", "BadRequestAPIException",
            "ServiceUnavailableAPIException", "TimeoutAPIException",
            "QuotaExceededAPIException", "create_validation_exc", "create_not_found_exc",
            "create_auth_exc", "create_rate_limit_exc", "create_permission_exc",
            "create_service_unavailable_exc"
        ])
        
    except ImportError as e:
        results["success"] = False
        results["import_errors"].append(f"Exceptions import error: {str(e)}")
    
    results["total_components"] = len(results["imported_components"])
    return results

def test_basic_functionality() -> Dict[str, Any]:
    """Test basic functionality of key components"""
    results = {
        "success": True,
        "functionality_errors": [],
        "tested_components": []
    }
    
    try:
        # Test basic request/response creation
        from apps.shared.api.models import BaseRequest, BaseResponse
        from apps.shared.api.responses import create_success_response, create_error_response
        from apps.shared.api.exceptions import APIException, ValidationAPIException
        
        # Test BaseRequest
        request = BaseRequest()
        assert request.request_id is not None
        assert request.priority.value == "normal"
        results["tested_components"].append("BaseRequest creation")
        
        # Test BaseResponse
        response = BaseResponse(success=True, message="Test")
        assert response.success is True
        assert response.message == "Test"
        results["tested_components"].append("BaseResponse creation")
        
        # Test response creation
        success_resp = create_success_response(data={"test": "data"}, message="Success")
        assert success_resp["success"] is True
        assert success_resp["data"]["test"] == "data"
        results["tested_components"].append("Success response creation")
        
        error_resp = create_error_response(error_code="TEST_ERROR", message="Test error")
        assert error_resp["success"] is False
        assert error_resp["error_code"] == "TEST_ERROR"
        results["tested_components"].append("Error response creation")
        
        # Test exception creation
        exc = APIException(message="Test exception", error_code="TEST")
        assert exc.message == "Test exception"
        assert exc.error_code == "TEST"
        
        exc_dict = exc.to_dict()
        assert exc_dict["success"] is False
        assert exc_dict["error_code"] == "TEST"
        results["tested_components"].append("APIException creation and serialization")
        
        # Test validation exception
        val_exc = ValidationAPIException.from_field_error("email", "Invalid email")
        assert len(val_exc.validation_errors) == 1
        assert val_exc.validation_errors[0]["field"] == "email"
        results["tested_components"].append("ValidationAPIException field error creation")
        
    except Exception as e:
        results["success"] = False
        results["functionality_errors"].append(f"Basic functionality error: {str(e)}")
        results["functionality_errors"].append(traceback.format_exc())
    
    return results

def test_rate_limiter() -> Dict[str, Any]:
    """Test rate limiter functionality"""
    results = {
        "success": True,
        "rate_limiter_errors": [],
        "tested_features": []
    }
    
    try:
        from apps.shared.api.decorators import RateLimiter
        from datetime import datetime, timedelta
        
        limiter = RateLimiter()
        
        # Test basic rate limiting
        allowed, reset_time = limiter.is_allowed("test_key", 5, 60)
        assert allowed is True
        results["tested_features"].append("Basic rate limit allowance")
        
        # Test rate limit enforcement
        for i in range(4):  # Already used 1, so 4 more to hit limit
            allowed, _ = limiter.is_allowed("test_key", 5, 60)
            assert allowed is True
        
        # Should be rate limited now
        allowed, reset_time = limiter.is_allowed("test_key", 5, 60)
        assert allowed is False
        assert reset_time > datetime.utcnow()
        results["tested_features"].append("Rate limit enforcement")
        
        # Test different keys don't interfere
        allowed, _ = limiter.is_allowed("different_key", 5, 60)
        assert allowed is True
        results["tested_features"].append("Key isolation")
        
    except Exception as e:
        results["success"] = False
        results["rate_limiter_errors"].append(f"Rate limiter error: {str(e)}")
        results["rate_limiter_errors"].append(traceback.format_exc())
    
    return results

def run_integration_tests() -> Dict[str, Any]:
    """Run all integration tests"""
    print("🔎 Running Shared API Integration Tests...")
    
    test_results = {
        "overall_success": True,
        "import_tests": test_imports(),
        "functionality_tests": test_basic_functionality(),
        "rate_limiter_tests": test_rate_limiter(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Check overall success
    if not test_results["import_tests"]["success"]:
        test_results["overall_success"] = False
        print("❌ Import tests failed")
    else:
        print(f"✅ Import tests passed - {test_results['import_tests']['total_components']} components imported")
    
    if not test_results["functionality_tests"]["success"]:
        test_results["overall_success"] = False
        print("❌ Functionality tests failed")
    else:
        print(f"✅ Functionality tests passed - {len(test_results['functionality_tests']['tested_components'])} components tested")
    
    if not test_results["rate_limiter_tests"]["success"]:
        test_results["overall_success"] = False
        print("❌ Rate limiter tests failed")
    else:
        print(f"✅ Rate limiter tests passed - {len(test_results['rate_limiter_tests']['tested_features'])} features tested")
    
    if test_results["overall_success"]:
        print("🎉 All Shared API integration tests passed!")
    else:
        print("💥 Some integration tests failed")
    
    return test_results

if __name__ == "__main__":
    # Run tests when script is executed directly
    results = run_integration_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results["overall_success"] else 1)
