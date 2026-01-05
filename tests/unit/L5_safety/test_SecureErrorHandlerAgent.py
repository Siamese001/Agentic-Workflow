# New file: tests/unit/test_secure_error_handler_agent.py
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import logging

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentic_core.L5_safety.guardrails.SecureErrorHandlerAgent import (
    SecureError, SecurityError, ValidationError, ExecutionError,
    ErrorSanitizer, SecureErrorHandler, handle_secure_error
)


class TestSecureError:
    """Test SecureError base class."""
    
    def test_instantiation(self):
        """Test SecureError instantiation."""
        error = SecureError("Test message", "ERR001", {"key": "value"})
        
        assert str(error) == "Test message"
        assert error.ErrorCode == "ERR001"
        assert error.context == {"key": "value"}
        assert error.timestamp is None
    
    def test_instantiation_defaults(self):
        """Test SecureError with default values."""
        error = SecureError("Test message")
        
        assert str(error) == "Test message"
        assert error.ErrorCode is None
        assert error.context == {}
    
    def test_to_dict(self):
        """Test to_dict method."""
        error = SecureError("Test message", "ERR001", {"key": "value"})
        result = error.to_dict()
        
        assert isinstance(result, dict)
        # Should contain error details in a safe format


class TestErrorSanitizer:
    """Test ErrorSanitizer class."""
    
    def test_sanitize_message_file_paths(self):
        """Test sanitization of file paths."""
        message = "Error in file /home/user/secret/file.py"
        sanitized = ErrorSanitizer.sanitize_message(message)
        
        assert "/home/user/secret" not in sanitized
        assert "/REDACTED_PATH" in sanitized
    
    def test_sanitize_message_passwords(self):
        """Test sanitization of passwords."""
        message = "Connection failed: password=secret123"
        sanitized = ErrorSanitizer.sanitize_message(message)
        
        assert "secret123" not in sanitized
        assert "password=REDACTED" in sanitized
    
    def test_sanitize_message_api_keys(self):
        """Test sanitization of API keys."""
        message = "API authentication failed: api_key=sk-1234567890abcdef"
        sanitized = ErrorSanitizer.sanitize_message(message)
        
        assert "sk-1234567890abcdef" not in sanitized
        assert "api_key=REDACTED" in sanitized
    
    def test_sanitize_message_emails(self):
        """Test sanitization of email addresses."""
        message = "User john.doe@example.com not found"
        sanitized = ErrorSanitizer.sanitize_message(message)
        
        assert "john.doe@example.com" not in sanitized
        assert "EMAIL@REDACTED" in sanitized
    
    def test_sanitize_message_urls(self):
        """Test sanitization of URLs with parameters."""
        message = "Request failed: https://api.example.com/v1/users?token=abc123"
        sanitized = ErrorSanitizer.sanitize_message(message)
        
        assert "token=abc123" not in sanitized
        assert "https://REDACTED/?parameters=REDACTED" in sanitized
    
    def test_sanitize_message_clean_text(self):
        """Test that clean text remains unchanged."""
        message = "Simple error message without sensitive data"
        sanitized = ErrorSanitizer.sanitize_message(message)
        
        assert sanitized == message
    
    def test_sanitize_stack_trace(self):
        """Test stack trace sanitization."""
        stack_trace = '''File "/home/user/secret/app.py", line 42, in function
    password="secret123"
File "/usr/local/lib/python3.9/site-packages/module.py", line 100'''
        
        sanitized = ErrorSanitizer.sanitize_stack_trace(stack_trace)
        
        assert "/home/user/secret" not in sanitized
        assert "secret123" not in sanitized
        assert "/REDACTED_PATH" in sanitized
        assert "password=REDACTED" in sanitized
    
    def test_create_secure_error_from_exception(self):
        """Test creating secure error from standard exception."""
        original_error = ValueError("Invalid value: password=secret123")
        
        secure_error = ErrorSanitizer.create_secure_error(
            SecurityError, 
            original_error,
            ErrorCode="VAL001"
        )
        
        assert isinstance(secure_error, SecurityError)
        assert secure_error.ErrorCode == "VAL001"
        assert "secret123" not in str(secure_error)
    
    def test_create_secure_error_with_context(self):
        """Test creating secure error with additional context."""
        original_error = Exception("Database connection failed")
        context = {"user_id": "12345", "operation": "login"}
        
        secure_error = ErrorSanitizer.create_secure_error(
            ExecutionError,
            original_error,
            add_context=context
        )
        
        assert isinstance(secure_error, ExecutionError)
        assert secure_error.context is not None


class TestSecureErrorHandler:
    """Test SecureErrorHandler class."""
    
    @pytest.fixture
    def error_handler(self):
        """Fixture for SecureErrorHandler instance."""
        return SecureErrorHandler()
    
    def test_instantiation(self, error_handler):
        """Test SecureErrorHandler instantiation."""
        assert error_handler is not None
        assert hasattr(error_handler, 'Logger')
        assert isinstance(error_handler.Logger, logging.Logger)
    
    def test_handle_error_standard_exception(self, error_handler):
        """Test handling of standard Python exception."""
        original_error = ValueError("Invalid input: api_key=secret123")
        
        result = error_handler.handle_error(original_error)
        
        assert isinstance(result, SecureError)
        assert "secret123" not in str(result)
    
    def test_handle_error_secure_error_passthrough(self, error_handler):
        """Test that SecureError instances pass through unchanged."""
        secure_error = SecurityError("Already secure", "SEC001")
        
        result = error_handler.handle_error(secure_error)
        
        assert result is secure_error
    
    def test_handle_error_with_context(self, error_handler):
        """Test error handling with additional context."""
        original_error = Exception("Connection failed")
        context = {"host": "localhost", "port": 5432}
        
        result = error_handler.handle_error(original_error, context)
        
        assert isinstance(result, SecureError)
    
    def test_handle_error_with_stack_trace(self, error_handler, caplog):
        """Test error handling with stack trace logging."""
        original_error = ValueError("Test error")
        
        with caplog.at_level(logging.DEBUG):
            result = error_handler.handle_error(original_error, include_stack=True)
        
        assert isinstance(result, SecureError)
        # Stack trace should be logged at DEBUG level
    
    def test_raise_secure_error(self, error_handler):
        """Test raising secure errors."""
        with pytest.raises(ValidationError) as exc_info:
            error_handler.raise_secure(
                ValidationError,
                "Invalid data: password=secret123",
                ErrorCode="VAL002"
            )
        
        raised_error = exc_info.value
        assert isinstance(raised_error, ValidationError)
        assert raised_error.ErrorCode == "VAL002"
        assert "secret123" not in str(raised_error)
    
    @pytest.mark.autonomy
    def test_heal_repository_smoke(self, error_handler):
        """Autonomy heal smoke test — ensure no crash."""
        result = error_handler.heal_repository()
        
        # SecureErrorHandler is operational L5 safety - should skip healing
        assert isinstance(result, dict)
        assert result.get("skipped") == 1
    
    def test_heal_repository_cycle_detection(self, error_handler):
        """Test heal_repository cycle detection."""
        call_path = {"SecureErrorHandler"}
        result = error_handler.heal_repository(_call_path=call_path)
        
        assert isinstance(result, dict)
        assert result.get("errors") == 1
        assert result.get("cycle_detected") is True
    
    def test_heal_repository_depth_limit(self, error_handler):
        """Test heal_repository depth limiting."""
        result = error_handler.heal_repository(depth=5, max_depth=3)
        
        assert isinstance(result, dict)
        assert result.get("errors") == 1
        assert result.get("depth_limited") is True
    
    def test_timeout_decorator_applied(self, error_handler):
        """Test that heal_repository has timeout decorator applied."""
        assert hasattr(error_handler.heal_repository, '__wrapped__')


class TestErrorSubclasses:
    """Test specific error subclasses."""
    
    def test_security_error(self):
        """Test SecurityError subclass."""
        error = SecurityError("Security violation", "SEC001")
        assert isinstance(error, SecureError)
        assert str(error) == "Security violation"
    
    def test_validation_error(self):
        """Test ValidationError subclass.""" 
        error = ValidationError("Validation failed", "VAL001")
        assert isinstance(error, SecureError)
        assert str(error) == "Validation failed"
    
    def test_execution_error(self):
        """Test ExecutionError subclass."""
        error = ExecutionError("Execution failed", "EXE001")
        assert isinstance(error, SecureError)
        assert str(error) == "Execution failed"


class TestGlobalFunctions:
    """Test global utility functions."""
    
    def test_handle_secure_error_function(self):
        """Test global handle_secure_error function."""
        original_error = ValueError("Test error with password=secret123")
        
        result = handle_secure_error(original_error)
        
        assert isinstance(result, SecureError)
        assert "secret123" not in str(result)
    
    def test_handle_secure_error_with_context(self):
        """Test global function with context."""
        original_error = Exception("Connection error")
        context = {"service": "database"}
        
        result = handle_secure_error(original_error, context)
        
        assert isinstance(result, SecureError)


class TestSensitivePatterns:
    """Test various sensitive data patterns."""
    
    @pytest.mark.parametrize("sensitive_input,should_be_redacted", [
        ("password=secret123", True),
        ("api_key=sk-1234567890", True), 
        ("token=abc123def456", True),
        ("/home/user/Documents/file.txt", True),
        ("user@example.com", True),
        ("mongodb://user:pass@host", True),
        ("https://api.com?secret=123", True),
        ("$SECRET_KEY", True),
        ("normal error message", False),
        ("file.py line 42", False),
    ])
    def test_pattern_detection(self, sensitive_input, should_be_redacted):
        """Test detection of various sensitive patterns."""
        sanitized = ErrorSanitizer.sanitize_message(f"Error: {sensitive_input}")
        
        if should_be_redacted:
            assert sanitized != f"Error: {sensitive_input}"
            assert "REDACTED" in sanitized
        else:
            assert sanitized == f"Error: {sensitive_input}"


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_message_sanitization(self):
        """Test sanitization of empty message."""
        sanitized = ErrorSanitizer.sanitize_message("")
        assert sanitized == ""
    
    def test_none_message_sanitization(self):
        """Test sanitization of None message."""
        sanitized = ErrorSanitizer.sanitize_message(None)
        assert sanitized == "None"
    
    def test_very_long_message(self):
        """Test sanitization of very long messages."""
        long_message = "Error: " + "x" * 10000 + " password=secret"
        sanitized = ErrorSanitizer.sanitize_message(long_message)
        
        assert "secret" not in sanitized
        assert "REDACTED" in sanitized
    
    def test_multiple_patterns_in_message(self):
        """Test message with multiple sensitive patterns."""
        message = "Error connecting to mysql://user:pass@host with api_key=sk-123 for user@example.com"
        sanitized = ErrorSanitizer.sanitize_message(message)
        
        assert "pass" not in sanitized
        assert "sk-123" not in sanitized
        assert "user@example.com" not in sanitized
        assert sanitized.count("REDACTED") >= 3
