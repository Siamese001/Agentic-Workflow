"""
L2 Execution Layer Unit Tests - SDK Integration

Tests for SDK integration and external service calls without planning logic.
Focuses on API clients, authentication, rate limiting, and error handling.
"""

import pytest
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import time
import json

# Mark all tests in this module as L2 execution unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l2, pytest.mark.execution]


class APIStatus(Enum):
    """API status codes for testing."""
    SUCCESS = "success"
    RATE_LIMITED = "rate_limited"
    AUTH_ERROR = "auth_error"
    SERVER_ERROR = "server_error"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class MockAPIResponse:
    """Mock API response for SDK testing."""
    status: APIStatus
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    headers: Dict[str, str]
    response_time: float


@dataclass(frozen=True)
class MockSDKConfig:
    """Mock SDK configuration for testing."""
    api_key: str
    base_url: str
    timeout: float
    max_retries: int
    rate_limit_rpm: int
    retry_delays: List[float]


class TestSDKAuthentication:
    """Test L2 SDK authentication and authorization."""
    
    def test_api_key_authentication(self):
        """Test API key-based authentication."""
        config = MockSDKConfig(
            api_key="test_api_key_12345",
            base_url="https://api.example.com",
            timeout=30.0,
            max_retries=3,
            rate_limit_rpm=60,
            retry_delays=[1.0, 2.0, 4.0]
        )
        
        # Mock API client with authentication
        class MockAPIClient:
            def __init__(self, config: MockSDKConfig):
                self.config = config
                self.auth_headers = {}
            
            def authenticate(self):
                """Set up authentication headers."""
                self.auth_headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "X-API-Key": self.config.api_key,
                    "Content-Type": "application/json"
                }
                return True
            
            def make_authenticated_request(self, endpoint: str, data: Dict[str, Any]) -> MockAPIResponse:
                """Make authenticated API request."""
                if not self.auth_headers:
                    return MockAPIResponse(
                        status=APIStatus.AUTH_ERROR,
                        data=None,
                        error="No authentication headers set",
                        headers={},
                        response_time=0.1
                    )
                
                # Simulate successful authenticated request
                return MockAPIResponse(
                    status=APIStatus.SUCCESS,
                    data={"result": "authenticated_request_success"},
                    error=None,
                    headers={"X-Rate-Limit-Remaining": "59"},
                    response_time=0.5
                )
        
        client = MockAPIClient(config)
        
        # Test authentication
        auth_result = client.authenticate()
        assert auth_result is True
        assert "Authorization" in client.auth_headers
        assert client.auth_headers["Authorization"] == f"Bearer {config.api_key}"
        
        # Test authenticated request
        response = client.make_authenticated_request("/analyze", {"text": "test"})
        assert response.status == APIStatus.SUCCESS
        assert response.data is not None
        assert response.error is None
    
    def test_invalid_api_key_handling(self):
        """Test handling of invalid API keys."""
        invalid_configs = [
            MockSDKConfig("", "https://api.example.com", 30.0, 3, 60, [1.0]),
            MockSDKConfig("invalid_key", "https://api.example.com", 30.0, 3, 60, [1.0]),
            MockSDKConfig("expired_key", "https://api.example.com", 30.0, 3, 60, [1.0])
        ]
        
        # Mock authentication validation
        def validate_api_key(api_key: str) -> Tuple[bool, Optional[str]]:
            if not api_key:
                return False, "API key cannot be empty"
            elif api_key == "invalid_key":
                return False, "Invalid API key format"
            elif api_key == "expired_key":
                return False, "API key has expired"
            elif len(api_key) < 10:
                return False, "API key too short"
            else:
                return True, None
        
        validation_results = []
        for config in invalid_configs:
            is_valid, error = validate_api_key(config.api_key)
            validation_results.append({
                "api_key": config.api_key,
                "is_valid": is_valid,
                "error": error
            })
        
        # Validate all invalid keys are rejected
        assert all(not result["is_valid"] for result in validation_results)
        assert all(result["error"] is not None for result in validation_results)
        
        # Validate specific error messages
        empty_key_result = next(r for r in validation_results if r["api_key"] == "")
        assert "cannot be empty" in empty_key_result["error"]
        
        invalid_key_result = next(r for r in validation_results if r["api_key"] == "invalid_key")
        assert "Invalid API key" in invalid_key_result["error"]
    
    def test_token_refresh_mechanism(self):
        """Test automatic token refresh mechanism."""
        
        class MockTokenManager:
            def __init__(self):
                self.current_token = "initial_token_123"
                self.refresh_count = 0
                self.token_expiry = time.time() + 3600  # 1 hour from now
            
            def is_token_expired(self) -> bool:
                return time.time() > self.token_expiry
            
            def refresh_token(self) -> str:
                """Simulate token refresh."""
                self.refresh_count += 1
                self.current_token = f"refreshed_token_{self.refresh_count}_{int(time.time())}"
                self.token_expiry = time.time() + 3600
                return self.current_token
            
            def get_valid_token(self) -> str:
                """Get valid token, refreshing if necessary."""
                if self.is_token_expired():
                    return self.refresh_token()
                return self.current_token
        
        token_manager = MockTokenManager()
        
        # Test initial token
        initial_token = token_manager.get_valid_token()
        assert initial_token == "initial_token_123"
        assert token_manager.refresh_count == 0
        
        # Simulate token expiry
        token_manager.token_expiry = time.time() - 1  # Expired
        
        # Test automatic refresh
        refreshed_token = token_manager.get_valid_token()
        assert refreshed_token != initial_token
        assert refreshed_token.startswith("refreshed_token_1_")
        assert token_manager.refresh_count == 1
        
        # Test multiple refreshes
        token_manager.token_expiry = time.time() - 1
        second_refresh = token_manager.get_valid_token()
        assert second_refresh != refreshed_token
        assert token_manager.refresh_count == 2


class TestRateLimiting:
    """Test L2 SDK rate limiting and throttling."""
    
    def test_rate_limit_calculation(self):
        """Test rate limit calculation and enforcement."""
        rate_limit_configs = [
            {"rpm": 60, "expected_rps": 1.0, "expected_interval": 1.0},
            {"rpm": 120, "expected_rps": 2.0, "expected_interval": 0.5},
            {"rpm": 1000, "expected_rps": 16.67, "expected_interval": 0.06}
        ]
        
        # Mock rate limiter
        class MockRateLimiter:
            def __init__(self, requests_per_minute: int):
                self.rpm = requests_per_minute
                self.rps = requests_per_minute / 60.0
                self.min_interval = 1.0 / self.rps
                self.last_request_time = 0.0
                self.request_count = 0
            
            def can_make_request(self) -> bool:
                """Check if request can be made without exceeding rate limit."""
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                
                if time_since_last >= self.min_interval:
                    self.last_request_time = current_time
                    self.request_count += 1
                    return True
                return False
            
            def get_wait_time(self) -> float:
                """Get time to wait before next request."""
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                return max(0, self.min_interval - time_since_last)
        
        rate_limit_results = []
        for config in rate_limit_configs:
            limiter = MockRateLimiter(config["rpm"])
            
            # Test rate limit calculation
            actual_rps = limiter.rps
            actual_interval = limiter.min_interval
            
            rate_limit_results.append({
                "rpm": config["rpm"],
                "expected_rps": config["expected_rps"],
                "actual_rps": actual_rps,
                "expected_interval": config["expected_interval"],
                "actual_interval": actual_interval,
                "rps_correct": abs(actual_rps - config["expected_rps"]) < 0.01,
                "interval_correct": abs(actual_interval - config["expected_interval"]) < 0.01
            })
        
        # Validate rate limit calculations
        assert all(result["rps_correct"] for result in rate_limit_results)
        assert all(result["interval_correct"] for result in rate_limit_results)
    
    def test_rate_limit_enforcement(self):
        """Test enforcement of rate limits."""
        limiter = MockRateLimiter(requests_per_minute=60)  # 1 request per second
        
        # Test immediate requests
        request_results = []
        start_time = time.time()
        
        for i in range(3):
            can_make = limiter.can_make_request()
            wait_time = limiter.get_wait_time()
            
            request_results.append({
                "request_num": i + 1,
                "can_make": can_make,
                "wait_time": wait_time,
                "timestamp": time.time() - start_time
            })
            
            if i > 0:  # Wait for rate limit after first request
                time.sleep(0.1)
        
        # Validate rate limiting behavior
        assert request_results[0]["can_make"] is True  # First request always allowed
        assert request_results[0]["wait_time"] == 0.0
        
        # Subsequent requests should be rate limited
        assert request_results[1]["wait_time"] > 0.8  # Should wait ~1 second
        assert request_results[2]["wait_time"] > 0.8
    
    @pytest.mark.asyncio
    async def test_async_rate_limiting(self):
        """Test rate limiting in async context."""
        
        class AsyncRateLimiter:
            def __init__(self, requests_per_second: float):
                self.rps = requests_per_second
                self.min_interval = 1.0 / requests_per_second
                self.last_request_time = 0.0
                self.request_count = 0
            
            async def acquire(self):
                """Acquire rate limit permit asynchronously."""
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                
                if time_since_last < self.min_interval:
                    wait_time = self.min_interval - time_since_last
                    await asyncio.sleep(wait_time)
                
                self.last_request_time = time.time()
                self.request_count += 1
        
        limiter = AsyncRateLimiter(requests_per_second=2.0)  # 2 requests per second
        
        # Test concurrent rate limiting
        async def make_request(request_id: int):
            await limiter.acquire()
            return {"request_id": request_id, "completed_at": time.time()}
        
        # Start multiple requests concurrently
        tasks = [make_request(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # Validate rate limiting
        assert len(results) == 5
        
        # Check that requests are properly spaced
        completion_times = [r["completed_at"] for r in results]
        completion_times.sort()
        
        # Verify minimum spacing between requests
        for i in range(1, len(completion_times)):
            time_diff = completion_times[i] - completion_times[i-1]
            assert time_diff >= 0.45  # Should be ~0.5 seconds apart (allowing some tolerance)


class TestErrorHandlingAndRetries:
    """Test L2 SDK error handling and retry mechanisms."""
    
    def test_retry_logic_configuration(self):
        """Test retry logic configuration and behavior."""
        retry_configs = [
            {"max_retries": 0, "delays": [], "expected_total_attempts": 1},
            {"max_retries": 3, "delays": [1.0, 2.0, 4.0], "expected_total_attempts": 4},
            {"max_retries": 5, "delays": [0.5, 1.0, 2.0, 4.0, 8.0], "expected_total_attempts": 6}
        ]
        
        # Mock retry executor
        class MockRetryExecutor:
            def __init__(self, max_retries: int, delays: List[float]):
                self.max_retries = max_retries
                self.delays = delays
                self.attempt_count = 0
                self.total_delay = 0.0
            
            def execute_with_retry(self, func, *args, **kwargs):
                """Execute function with retry logic."""
                for attempt in range(self.max_retries + 1):
                    self.attempt_count += 1
                    
                    try:
                        result = func(*args, **kwargs)
                        if result.get("success", False):
                            return result
                    except Exception as e:
                        if attempt == self.max_retries:
                            raise e
                    
                    # Add delay if not last attempt
                    if attempt < self.max_retries and attempt < len(self.delays):
                        delay = self.delays[attempt]
                        self.total_delay += delay
                        time.sleep(0.001)  # Minimal sleep for testing
                
                return {"success": False, "attempts": self.attempt_count}
        
        retry_results = []
        for config in retry_configs:
            def failing_function():
                return {"success": False, "error": "Simulated failure"}
            
            executor = MockRetryExecutor(config["max_retries"], config["delays"])
            result = executor.execute_with_retry(failing_function)
            
            retry_results.append({
                "config": config,
                "attempts": executor.attempt_count,
                "expected_attempts": config["expected_total_attempts"],
                "correct_attempts": executor.attempt_count == config["expected_total_attempts"],
                "total_delay": executor.total_delay
            })
        
        # Validate retry behavior
        assert all(result["correct_attempts"] for result in retry_results)
        
        # Validate delay accumulation
        retry_with_delays = next(r for r in retry_results if r["config"]["max_retries"] == 3)
        expected_delay = sum(retry_with_delays["config"]["delays"])
        assert retry_with_delays["total_delay"] == expected_delay
    
    def test_exponential_backoff(self):
        """Test exponential backoff retry strategy."""
        
        class ExponentialBackoffRetry:
            def __init__(self, base_delay: float, max_delay: float, multiplier: float):
                self.base_delay = base_delay
                self.max_delay = max_delay
                self.multiplier = multiplier
                self.retry_delays = []
            
            def calculate_delay(self, attempt: int) -> float:
                """Calculate delay for given attempt number."""
                delay = self.base_delay * (self.multiplier ** attempt)
                delay = min(delay, self.max_delay)
                self.retry_delays.append(delay)
                return delay
        
        backoff = ExponentialBackoffRetry(base_delay=1.0, max_delay=10.0, multiplier=2.0)
        
        # Calculate delays for first 5 attempts
        expected_delays = [1.0, 2.0, 4.0, 8.0, 10.0]  # Last one capped at max_delay
        actual_delays = []
        
        for attempt in range(5):
            delay = backoff.calculate_delay(attempt)
            actual_delays.append(delay)
        
        # Validate exponential backoff
        assert actual_delays == expected_delays
        
        # Validate backoff properties
        assert actual_delays[1] == actual_delays[0] * 2
        assert actual_delays[2] == actual_delays[1] * 2
        assert actual_delays[4] == backoff.max_delay  # Capped at maximum
    
    def test_circuit_breaker_pattern(self):
        """Test circuit breaker pattern for API failures."""
        
        class MockCircuitBreaker:
            def __init__(self, failure_threshold: int, timeout: float):
                self.failure_threshold = failure_threshold
                self.timeout = timeout
                self.failure_count = 0
                self.last_failure_time = 0.0
                self.state = "closed"  # closed, open, half_open
            
            def call(self, func, *args, **kwargs):
                """Execute function with circuit breaker protection."""
                if self.state == "open":
                    if time.time() - self.last_failure_time > self.timeout:
                        self.state = "half_open"
                    else:
                        raise Exception("Circuit breaker is open")
                
                try:
                    result = func(*args, **kwargs)
                    if self.state == "half_open":
                        self.state = "closed"
                        self.failure_count = 0
                    return result
                except Exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    
                    if self.failure_count >= self.failure_threshold:
                        self.state = "open"
                    
                    raise e
        
        circuit_breaker = MockCircuitBreaker(failure_threshold=3, timeout=5.0)
        
        def failing_function():
            raise Exception("Simulated API failure")
        
        def working_function():
            return {"success": True}
        
        # Test circuit breaker behavior
        # First few failures should trigger circuit breaker
        for i in range(3):
            with pytest.raises(Exception):
                circuit_breaker.call(failing_function)
        
        assert circuit_breaker.state == "open"
        assert circuit_breaker.failure_count == 3
        
        # Next call should fail due to open circuit
        with pytest.raises(Exception, match="Circuit breaker is open"):
            circuit_breaker.call(working_function)
        
        # Simulate timeout passing
        circuit_breaker.last_failure_time = time.time() - 6.0
        
        # Should now be half-open and allow one attempt
        result = circuit_breaker.call(working_function)
        assert result["success"] is True
        assert circuit_breaker.state == "closed"


class TestSDKResponseHandling:
    """Test L2 SDK response parsing and validation."""
    
    def test_response_parsing(self):
        """Test parsing of different API response formats."""
        
        # Mock response parser
        class MockResponseParser:
            @staticmethod
            def parse_json_response(response_text: str) -> Dict[str, Any]:
                """Parse JSON response with error handling."""
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError as e:
                    return {"error": f"JSON parsing failed: {str(e)}"}
            
            @staticmethod
            def extract_result_data(parsed_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
                """Extract result data from parsed response."""
                if "error" in parsed_response:
                    return None
                
                return parsed_response.get("data", parsed_response.get("result", {}))
            
            @staticmethod
            def validate_response_structure(response: Dict[str, Any], required_fields: List[str]) -> bool:
                """Validate response has required structure."""
                return all(field in response for field in required_fields)
        
        parser = MockResponseParser()
        
        # Test valid JSON response
        valid_json = '{"data": {"analysis": "complete", "score": 0.85}, "status": "success"}'
        parsed_valid = parser.parse_json_response(valid_json)
        assert "error" not in parsed_valid
        assert parsed_valid["data"]["score"] == 0.85
        
        # Test invalid JSON response
        invalid_json = '{"data": {"analysis": "incomplete", "score": 0.85'  # Missing closing brace
        parsed_invalid = parser.parse_json_response(invalid_json)
        assert "error" in parsed_invalid
        assert "JSON parsing failed" in parsed_invalid["error"]
        
        # Test data extraction
        result_data = parser.extract_result_data(parsed_valid)
        assert result_data is not None
        assert result_data["analysis"] == "complete"
        
        # Test extraction from error response
        error_data = parser.extract_result_data(parsed_invalid)
        assert error_data is None
        
        # Test structure validation
        required_fields = ["data", "status"]
        is_valid = parser.validate_response_structure(parsed_valid, required_fields)
        assert is_valid is True
        
        is_invalid = parser.validate_response_structure(parsed_invalid, required_fields)
        assert is_invalid is False
    
    def test_response_error_classification(self):
        """Test classification of different response errors."""
        error_responses = [
            {
                "status_code": 400,
                "response_body": {"error": "Bad Request", "message": "Invalid parameters"},
                "expected_class": "client_error"
            },
            {
                "status_code": 401,
                "response_body": {"error": "Unauthorized", "message": "Invalid API key"},
                "expected_class": "auth_error"
            },
            {
                "status_code": 429,
                "response_body": {"error": "Rate Limited", "message": "Too many requests"},
                "expected_class": "rate_limit_error"
            },
            {
                "status_code": 500,
                "response_body": {"error": "Internal Server Error", "message": "Server failure"},
                "expected_class": "server_error"
            },
            {
                "status_code": 200,
                "response_body": {"data": "success", "result": "completed"},
                "expected_class": "success"
            }
        ]
        
        # Mock error classifier
        def classify_response_error(status_code: int, response_body: Dict[str, Any]) -> str:
            if status_code == 200:
                return "success"
            elif 400 <= status_code < 500:
                if status_code == 401:
                    return "auth_error"
                elif status_code == 429:
                    return "rate_limit_error"
                else:
                    return "client_error"
            elif 500 <= status_code < 600:
                return "server_error"
            else:
                return "unknown_error"
        
        classification_results = []
        for error_response in error_responses:
            classification = classify_response_error(
                error_response["status_code"],
                error_response["response_body"]
            )
            
            classification_results.append({
                "status_code": error_response["status_code"],
                "expected_class": error_response["expected_class"],
                "actual_class": classification,
                "correct": classification == error_response["expected_class"]
            })
        
        # Validate error classification
        assert all(result["correct"] for result in classification_results)
        
        # Validate specific classifications
        auth_result = next(r for r in classification_results if r["status_code"] == 401)
        assert auth_result["actual_class"] == "auth_error"
        
        rate_limit_result = next(r for r in classification_results if r["status_code"] == 429)
        assert rate_limit_result["actual_class"] == "rate_limit_error"
    
    def test_response_timeout_handling(self):
        """Test handling of response timeouts."""
        
        class MockTimeoutHandler:
            def __init__(self, default_timeout: float):
                self.default_timeout = default_timeout
                self.timeout_occurrences = []
            
            def make_request_with_timeout(self, response_delay: float) -> Dict[str, Any]:
                """Simulate request with configurable response delay."""
                start_time = time.time()
                
                if response_delay > self.default_timeout:
                    self.timeout_occurrences.append(response_delay)
                    return {
                        "success": False,
                        "error": f"Request timed out after {self.default_timeout}s",
                        "actual_delay": response_delay
                    }
                else:
                    # Simulate successful response within timeout
                    time.sleep(min(response_delay, 0.01))  # Minimal sleep for testing
                    return {
                        "success": True,
                        "data": "response_data",
                        "actual_delay": response_delay
                    }
        
        timeout_handler = MockTimeoutHandler(default_timeout=2.0)
        
        # Test various response delays
        test_delays = [0.5, 1.0, 1.5, 2.5, 3.0, 5.0]
        request_results = []
        
        for delay in test_delays:
            result = timeout_handler.make_request_with_timeout(delay)
            request_results.append({
                "delay": delay,
                "success": result["success"],
                "timed_out": not result["success"],
                "actual_delay": result["actual_delay"]
            })
        
        # Validate timeout handling
        successful_requests = [r for r in request_results if r["success"]]
        timed_out_requests = [r for r in request_results if r["timed_out"]]
        
        assert len(successful_requests) == 3  # Delays <= 2.0
        assert len(timed_out_requests) == 3   # Delays > 2.0
        
        # Validate timeout detection
        assert all(r["delay"] > 2.0 for r in timed_out_requests)
        assert all(r["delay"] <= 2.0 for r in successful_requests)
        
        # Validate timeout tracking
        assert len(timeout_handler.timeout_occurrences) == 3
        assert all(delay > 2.0 for delay in timeout_handler.timeout_occurrences)
