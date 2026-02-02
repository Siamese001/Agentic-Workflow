"""
Unit tests for Security Utilities.

Tests Phase 5A - Security Hardening.
"""

from apps_shared.utils.security_utils_config import (
    InputSanitizer,
    InputValidator,
    RateLimiter,
    SecureTokenGenerator,
    SecurityAuditLog,
    ValidationResult,
)


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_success(self):
        """Test creating a successful result."""
        result = ValidationResult.success("sanitized")
        assert result.valid is True
        assert result.errors == []
        assert result.sanitized_value == "sanitized"

    def test_failure(self):
        """Test creating a failed result."""
        result = ValidationResult.failure(["Error 1", "Error 2"])
        assert result.valid is False
        assert len(result.errors) == 2


class TestInputSanitizer:
    """Test InputSanitizer functionality."""

    def test_sanitize_string_basic(self):
        """Test basic string sanitization."""
        result = InputSanitizer.sanitize_string("  hello world  ")
        assert result == "hello world"

    def test_sanitize_string_strips_script(self):
        """Test script tag removal."""
        result = InputSanitizer.sanitize_string("Hello <script>alert('xss')</script> World")
        assert "<script>" not in result
        assert "alert" not in result

    def test_sanitize_string_strips_html(self):
        """Test HTML tag removal."""
        result = InputSanitizer.sanitize_string("Hello <b>World</b>")
        assert "<b>" not in result
        assert "</b>" not in result
        assert "Hello World" in result

    def test_sanitize_string_max_length(self):
        """Test max length truncation."""
        long_string = "a" * 1000
        result = InputSanitizer.sanitize_string(long_string, max_length=100)
        assert len(result) == 100

    def test_sanitize_string_removes_null_bytes(self):
        """Test null byte removal."""
        result = InputSanitizer.sanitize_string("hello\x00world")
        assert "\x00" not in result

    def test_sanitize_path_removes_traversal(self):
        """Test path traversal removal."""
        result = InputSanitizer.sanitize_path("../../../etc/passwd")
        assert "../" not in result
        assert "etc/passwd" in result

    def test_sanitize_path_normalizes_separators(self):
        """Test path separator normalization."""
        result = InputSanitizer.sanitize_path("path\\to\\file")
        assert "\\" not in result
        assert "path/to/file" == result

    def test_sanitize_identifier(self):
        """Test identifier sanitization."""
        result = InputSanitizer.sanitize_identifier("user@name!#$%")
        assert result == "username"

    def test_sanitize_identifier_max_length(self):
        """Test identifier max length."""
        result = InputSanitizer.sanitize_identifier("a" * 500, max_length=50)
        assert len(result) == 50


class TestInputValidator:
    """Test InputValidator functionality."""

    def test_validate_email_valid(self):
        """Test valid email validation."""
        result = InputValidator.validate_email("test@example.com")
        assert result.valid is True
        assert result.sanitized_value == "test@example.com"

    def test_validate_email_invalid(self):
        """Test invalid email validation."""
        result = InputValidator.validate_email("not-an-email")
        assert result.valid is False

    def test_validate_email_empty(self):
        """Test empty email validation."""
        result = InputValidator.validate_email("")
        assert result.valid is False

    def test_validate_email_too_long(self):
        """Test email too long."""
        long_email = "a" * 250 + "@example.com"
        result = InputValidator.validate_email(long_email)
        assert result.valid is False

    def test_validate_url_valid_http(self):
        """Test valid HTTP URL."""
        result = InputValidator.validate_url("http://example.com/path")
        assert result.valid is True

    def test_validate_url_valid_https(self):
        """Test valid HTTPS URL."""
        result = InputValidator.validate_url("https://example.com/path")
        assert result.valid is True

    def test_validate_url_require_https(self):
        """Test HTTPS requirement."""
        result = InputValidator.validate_url("http://example.com", require_https=True)
        assert result.valid is False

    def test_validate_url_invalid(self):
        """Test invalid URL."""
        result = InputValidator.validate_url("not-a-url")
        assert result.valid is False

    def test_validate_length_valid(self):
        """Test valid length."""
        result = InputValidator.validate_length("hello", min_length=1, max_length=10)
        assert result.valid is True

    def test_validate_length_too_short(self):
        """Test too short."""
        result = InputValidator.validate_length("hi", min_length=5)
        assert result.valid is False

    def test_validate_length_too_long(self):
        """Test too long."""
        result = InputValidator.validate_length("hello world", max_length=5)
        assert result.valid is False

    def test_validate_not_empty_valid(self):
        """Test not empty with value."""
        result = InputValidator.validate_not_empty("hello")
        assert result.valid is True

    def test_validate_not_empty_none(self):
        """Test not empty with None."""
        result = InputValidator.validate_not_empty(None)
        assert result.valid is False

    def test_validate_not_empty_whitespace(self):
        """Test not empty with whitespace."""
        result = InputValidator.validate_not_empty("   ")
        assert result.valid is False

    def test_validate_not_empty_empty_list(self):
        """Test not empty with empty list."""
        result = InputValidator.validate_not_empty([])
        assert result.valid is False

    def test_check_sql_injection_clean(self):
        """Test clean input passes SQL injection check."""
        result = InputValidator.check_sql_injection("hello world")
        assert result.valid is True

    def test_check_sql_injection_detected(self):
        """Test SQL injection detection."""
        result = InputValidator.check_sql_injection("'; DROP TABLE users; --")
        assert result.valid is False

    def test_check_path_traversal_clean(self):
        """Test clean path passes traversal check."""
        result = InputValidator.check_path_traversal("/valid/path/file.txt")
        assert result.valid is True

    def test_check_path_traversal_detected(self):
        """Test path traversal detection."""
        result = InputValidator.check_path_traversal("../../../etc/passwd")
        assert result.valid is False


class TestSecureTokenGenerator:
    """Test SecureTokenGenerator functionality."""

    def test_generate_token_length(self):
        """Test token generation with default length."""
        token = SecureTokenGenerator.generate_token()
        assert len(token) >= 32

    def test_generate_token_custom_length(self):
        """Test token generation with custom length."""
        token = SecureTokenGenerator.generate_token(length=64)
        assert len(token) >= 64

    def test_generate_token_unique(self):
        """Test tokens are unique."""
        tokens = [SecureTokenGenerator.generate_token() for _ in range(100)]
        assert len(set(tokens)) == 100

    def test_generate_api_key_format(self):
        """Test API key format."""
        key = SecureTokenGenerator.generate_api_key(prefix="test")
        assert key.startswith("test_")

    def test_hash_value(self):
        """Test value hashing."""
        hash1 = SecureTokenGenerator.hash_value("password")
        hash2 = SecureTokenGenerator.hash_value("password")
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex

    def test_hash_value_with_salt(self):
        """Test value hashing with salt."""
        hash1 = SecureTokenGenerator.hash_value("password", salt="salt1")
        hash2 = SecureTokenGenerator.hash_value("password", salt="salt2")
        assert hash1 != hash2

    def test_verify_hash_correct(self):
        """Test hash verification with correct value."""
        value = "secret"
        hashed = SecureTokenGenerator.hash_value(value)
        assert SecureTokenGenerator.verify_hash(value, hashed) is True

    def test_verify_hash_incorrect(self):
        """Test hash verification with incorrect value."""
        hashed = SecureTokenGenerator.hash_value("secret")
        assert SecureTokenGenerator.verify_hash("wrong", hashed) is False

    def test_generate_session_id(self):
        """Test session ID generation."""
        session_id = SecureTokenGenerator.generate_session_id()
        assert len(session_id) >= 48


class TestRateLimiter:
    """Test RateLimiter functionality."""

    def test_allows_under_limit(self):
        """Test requests under limit are allowed."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)

        for _ in range(5):
            assert limiter.is_allowed("user1") is True

    def test_blocks_over_limit(self):
        """Test requests over limit are blocked."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)

        for _ in range(3):
            limiter.is_allowed("user1")

        assert limiter.is_allowed("user1") is False

    def test_separate_keys(self):
        """Test separate keys have separate limits."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)

        limiter.is_allowed("user1")
        limiter.is_allowed("user1")
        limiter.is_allowed("user2")

        assert limiter.is_allowed("user1") is False
        assert limiter.is_allowed("user2") is True

    def test_get_remaining(self):
        """Test getting remaining requests."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)

        assert limiter.get_remaining("user1") == 5

        limiter.is_allowed("user1")
        limiter.is_allowed("user1")

        assert limiter.get_remaining("user1") == 3

    def test_reset_key(self):
        """Test resetting a specific key."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)

        limiter.is_allowed("user1")
        limiter.is_allowed("user1")
        limiter.reset("user1")

        assert limiter.is_allowed("user1") is True

    def test_reset_all(self):
        """Test resetting all keys."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)

        limiter.is_allowed("user1")
        limiter.is_allowed("user2")
        limiter.reset()

        assert limiter.get_remaining("user1") == 2
        assert limiter.get_remaining("user2") == 2


class TestSecurityAuditLog:
    """Test SecurityAuditLog functionality."""

    def test_log_event(self):
        """Test logging an event."""
        audit = SecurityAuditLog("test")

        audit.log_event("test_event", "Test message", severity="info")

        events = audit.get_events()
        assert len(events) == 1
        assert events[0]["type"] == "test_event"

    def test_log_validation_failure(self):
        """Test logging validation failure."""
        audit = SecurityAuditLog("test")

        audit.log_validation_failure("email", ["Invalid format"])

        events = audit.get_events(event_type="validation_failure")
        assert len(events) == 1

    def test_log_rate_limit(self):
        """Test logging rate limit."""
        audit = SecurityAuditLog("test")

        audit.log_rate_limit("user123")

        events = audit.get_events(event_type="rate_limit")
        assert len(events) == 1

    def test_log_suspicious_activity(self):
        """Test logging suspicious activity."""
        audit = SecurityAuditLog("test")

        audit.log_suspicious_activity("SQL injection attempt")

        events = audit.get_events(event_type="suspicious_activity")
        assert len(events) == 1
        assert events[0]["severity"] == "error"

    def test_filter_by_severity(self):
        """Test filtering events by severity."""
        audit = SecurityAuditLog("test")

        audit.log_event("event1", "Info event", severity="info")
        audit.log_event("event2", "Warning event", severity="warning")

        warning_events = audit.get_events(severity="warning")
        assert len(warning_events) == 1

    def test_clear_events(self):
        """Test clearing events."""
        audit = SecurityAuditLog("test")

        audit.log_event("event1", "Message 1")
        audit.log_event("event2", "Message 2")
        audit.clear()

        assert len(audit.get_events()) == 0
