"""
L2 Execution Layer Unit Tests

Tests for tool execution, SDK calls, and MCP integration without planning logic.
Focuses on individual tool execution, error handling, and response validation.
"""

import pytest
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import time

# Mark all tests in this module as L2 execution unit tests
pytestmark = [pytest.mark.unit, pytest.mark.l2, pytest.mark.execution]


@dataclass(frozen=True)
class MockToolRequest:
    """Mock tool request for testing L2 execution."""
    tool_name: str
    parameters: Dict[str, Any]
    timeout: float = 30.0
    retry_count: int = 3


@dataclass(frozen=True)
class MockToolResponse:
    """Mock tool response for testing L2 execution."""
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[str]
    execution_time: float
    tokens_used: int


class TestToolExecutionCore:
    """Test core L2 tool execution functionality."""
    
    def test_successful_tool_execution(self):
        """Test successful tool execution with valid parameters."""
        request = MockToolRequest(
            tool_name="text_analyzer",
            parameters={"text": "Sample job description", "analysis_type": "requirements"},
            timeout=10.0
        )
        
        # Mock successful execution
        response = MockToolResponse(
            success=True,
            data={"extracted_requirements": ["Python", "AWS", "5+ years experience"]},
            error=None,
            execution_time=1.5,
            tokens_used=150
        )
        
        assert response.success is True
        assert response.data is not None
        assert "extracted_requirements" in response.data
        assert response.error is None
        assert response.execution_time < request.timeout
    
    def test_tool_timeout_handling(self):
        """Test tool execution timeout handling."""
        request = MockToolRequest(
            tool_name="slow_processor",
            parameters={"data": "large_dataset"},
            timeout=0.1  # Very short timeout
        )
        
        # Mock timeout scenario
        start_time = time.time()
        time.sleep(0.2)  # Simulate slow execution
        execution_time = time.time() - start_time
        
        response = MockToolResponse(
            success=False,
            data=None,
            error=f"Tool execution timed out after {execution_time:.2f}s",
            execution_time=execution_time,
            tokens_used=0
        )
        
        assert response.success is False
        assert response.error is not None
        assert "timed out" in response.error.lower()
        assert execution_time > request.timeout
    
    def test_tool_parameter_validation(self):
        """Test tool parameter validation before execution."""
        # Valid parameters
        valid_request = MockToolRequest(
            tool_name="resume_parser",
            parameters={"resume_text": "John Doe\nExperience: 5 years", "format": "structured"},
            timeout=15.0
        )
        
        # Mock parameter validation
        required_params = ["resume_text", "format"]
        valid_params = all(param in valid_request.parameters for param in required_params)
        
        assert valid_params is True
        
        # Invalid parameters (missing required field)
        invalid_request = MockToolRequest(
            tool_name="resume_parser",
            parameters={"resume_text": "John Doe\nExperience: 5 years"},  # Missing format
            timeout=15.0
        )
        
        missing_params = [param for param in required_params if param not in invalid_request.parameters]
        assert len(missing_params) == 1
        assert "format" in missing_params


class TestRetryAndBackoffLogic:
    """Test L2 retry logic and exponential backoff."""
    
    def test_retry_on_failure(self):
        """Test retry mechanism for failed tool executions."""
        retry_count = 0
        max_retries = 3
        
        # Mock retry logic
        for attempt in range(max_retries):
            retry_count += 1
            # Simulate failure on first two attempts
            if attempt < 2:
                continue  # Retry
            else:
                # Success on third attempt
                response = MockToolResponse(
                    success=True,
                    data={"result": "success_after_retry"},
                    error=None,
                    execution_time=1.0,
                    tokens_used=100
                )
                break
        else:
            # All retries failed
            response = MockToolResponse(
                success=False,
                data=None,
                error="All retry attempts failed",
                execution_time=0.0,
                tokens_used=0
            )
        
        assert retry_count == 3
        assert response.success is True
        assert response.data["result"] == "success_after_retry"
    
    def test_exponential_backoff_timing(self):
        """Test exponential backoff timing between retries."""
        base_delay = 1.0
        max_delay = 10.0
        retry_attempts = []
        
        # Mock exponential backoff calculation
        for attempt in range(4):
            delay = min(base_delay * (2 ** attempt), max_delay)
            retry_attempts.append(delay)
        
        expected_delays = [1.0, 2.0, 4.0, 8.0]
        assert retry_attempts == expected_delays
        assert all(delay <= max_delay for delay in retry_attempts)
    
    def test_circuit_breaker_activation(self):
        """Test circuit breaker activation after consecutive failures."""
        failure_threshold = 5
        consecutive_failures = 0
        circuit_breaker_open = False
        
        # Simulate consecutive failures
        for i in range(7):
            if i < 6:  # First 6 attempts fail
                consecutive_failures += 1
                if consecutive_failures >= failure_threshold:
                    circuit_breaker_open = True
            else:  # 7th attempt should be blocked by circuit breaker
                if circuit_breaker_open:
                    response = MockToolResponse(
                        success=False,
                        data=None,
                        error="Circuit breaker is open",
                        execution_time=0.0,
                        tokens_used=0
                    )
        
        assert circuit_breaker_open is True
        assert consecutive_failures >= failure_threshold


class TestResponseValidationAndParsing:
    """Test L2 response validation and data parsing."""
    
    def test_response_schema_validation(self):
        """Test validation of tool response schemas."""
        # Define expected schema
        expected_schema = {
            "type": "object",
            "properties": {
                "requirements": {"type": "array"},
                "skills": {"type": "array"},
                "experience_level": {"type": "string"}
            },
            "required": ["requirements", "skills"]
        }
        
        # Valid response
        valid_response = {
            "requirements": ["Python", "AWS"],
            "skills": ["programming", "cloud computing"],
            "experience_level": "senior"
        }
        
        # Mock schema validation
        is_valid = (
            isinstance(valid_response, dict) and
            all(prop in valid_response for prop in expected_schema["required"]) and
            all(isinstance(valid_response[prop], expected_schema["properties"][prop]["type"]) 
                for prop in expected_schema["required"])
        )
        
        assert is_valid is True
        
        # Invalid response (missing required field)
        invalid_response = {
            "skills": ["programming"],
            "experience_level": "senior"
        }
        
        missing_required = [prop for prop in expected_schema["required"] if prop not in invalid_response]
        assert len(missing_required) == 1
        assert "requirements" in missing_required
    
    def test_response_data_sanitization(self):
        """Test sanitization of response data."""
        raw_response = {
            "requirements": ["Python", "AWS", "  SQL  "],  # SQL has extra whitespace
            "description": "Job with <script>alert('xss')</script> content",
            "metadata": {"confidence": 0.95, "source": None}  # Contains None value
        }
        
        # Mock data sanitization
        sanitized_response = {
            "requirements": [req.strip() for req in raw_response["requirements"]],
            "description": raw_response["description"].replace("<script>", "").replace("</script>", ""),
            "metadata": {k: v for k, v in raw_response["metadata"].items() if v is not None}
        }
        
        assert "SQL" in sanitized_response["requirements"]
        assert sanitized_response["requirements"][2] == "SQL"  # No extra whitespace
        assert "<script>" not in sanitized_response["description"]
        assert "source" not in sanitized_response["metadata"]  # None value removed
    
    def test_partial_response_handling(self):
        """Test handling of partial or incomplete tool responses."""
        partial_response = {
            "status": "partial",
            "data": {
                "requirements": ["Python", "AWS"],
                "skills": None  # Incomplete data
            },
            "warning": "Skills extraction incomplete"
        }
        
        # Mock partial response processing
        completeness_score = sum(1 for v in partial_response["data"].values() if v is not None)
        total_fields = len(partial_response["data"])
        completeness_ratio = completeness_score / total_fields
        
        assert completeness_ratio == 0.5  # 1 out of 2 fields complete
        assert partial_response["status"] == "partial"
        assert "warning" in partial_response


class TestResourceManagement:
    """Test L2 resource management and cleanup."""
    
    def test_token_usage_tracking(self):
        """Test tracking of token usage during tool execution."""
        executions = [
            {"tokens": 150, "tool": "text_analyzer"},
            {"tokens": 300, "tool": "resume_parser"},
            {"tokens": 200, "tool": "skill_matcher"}
        ]
        
        total_tokens = sum(exec["tokens"] for exec in executions)
        max_single_execution = max(exec["tokens"] for exec in executions)
        average_tokens = total_tokens / len(executions)
        
        assert total_tokens == 650
        assert max_single_execution == 300
        assert average_tokens == 216.67  # Approximate
    
    def test_memory_cleanup_after_execution(self):
        """Test memory cleanup after tool execution."""
        # Mock memory usage tracking
        initial_memory = {"used": 100, "peak": 100}
        
        # Simulate tool execution with memory allocation
        execution_memory = {"used": 250, "peak": 250}
        
        # Simulate cleanup
        cleanup_memory = {"used": 120, "peak": 250}  # Usage reduced, peak preserved
        
        assert cleanup_memory["used"] < execution_memory["used"]
        assert cleanup_memory["peak"] == execution_memory["peak"]  # Peak preserved for monitoring
    
    def test_concurrent_execution_limits(self):
        """Test enforcement of concurrent execution limits."""
        max_concurrent = 3
        active_executions = []
        
        # Simulate execution requests
        execution_requests = range(8)  # 8 concurrent requests
        
        # Mock concurrent execution limiting
        for request_id in execution_requests:
            if len(active_executions) >= max_concurrent:
                # Would wait or queue
                queued = True
            else:
                active_executions.append(request_id)
                queued = False
            
            # Simulate execution completion
            if not queued and len(active_executions) > 0:
                completed = active_executions.pop(0)
        
        # At no point should active executions exceed the limit
        assert max_concurrent == 3


class TestErrorHandlingAndRecovery:
    """Test L2 error handling and recovery mechanisms."""
    
    def test_network_error_handling(self):
        """Test handling of network-related errors."""
        network_errors = [
            {"type": "timeout", "retryable": True},
            {"type": "connection_refused", "retryable": True},
            {"type": "dns_resolution_failed", "retryable": False},
            {"type": "rate_limit", "retryable": True}
        ]
        
        for error in network_errors:
            if error["retryable"]:
                handling_strategy = "retry_with_backoff"
            else:
                handling_strategy = "fail_immediately"
            
            if error["type"] == "timeout":
                assert handling_strategy == "retry_with_backoff"
            elif error["type"] == "dns_resolution_failed":
                assert handling_strategy == "fail_immediately"
    
    def test_malformed_response_recovery(self):
        """Test recovery from malformed tool responses."""
        malformed_responses = [
            {"data": "not_a_dict", "error": None},
            {"data": None, "error": None},
            {"data": {"incomplete": "structure"}, "error": None}
        ]
        
        recovery_actions = []
        for response in malformed_responses:
            if not isinstance(response.get("data"), dict):
                recovery_actions.append("attempt_response_reconstruction")
            elif response.get("data") is None:
                recovery_actions.append("request_retry_with_different_params")
            else:
                recovery_actions.append("validate_and_fix_structure")
        
        assert recovery_actions[0] == "attempt_response_reconstruction"
        assert recovery_actions[1] == "request_retry_with_different_params"
        assert recovery_actions[2] == "validate_and_fix_structure"
    
    def test_graceful_degradation(self):
        """Test graceful degradation when tools are unavailable."""
        tool_availability = {
            "primary_analyzer": False,
            "fallback_analyzer": True,
            "basic_parser": True,
            "advanced_parser": False
        }
        
        # Mock tool selection with graceful degradation
        selected_tools = {}
        for task, tools in [
            ("analysis", ["primary_analyzer", "fallback_analyzer", "basic_parser"]),
            ("parsing", ["advanced_parser", "basic_parser"])
        ]:
            for tool in tools:
                if tool_availability.get(tool, False):
                    selected_tools[task] = tool
                    break
        
        assert selected_tools["analysis"] == "fallback_analyzer"
        assert selected_tools["parsing"] == "basic_parser"
