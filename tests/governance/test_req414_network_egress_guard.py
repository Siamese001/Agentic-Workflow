"""
Test REQ-414: Network Egress Guard

Tests that all outbound HTTP requests to LLM-serving endpoints (including localhost)
MUST originate exclusively from SovereignLLMGateway.
"""

import os
import socket
from unittest.mock import patch

import pytest

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.enforcement.network_egress_guard import (
    NetworkEgressViolation,
    check_network_egress_allowed,
    install_egress_guard,
    is_llm_endpoint,
    simulate_direct_llm_request,
    test_egress_guard,
    uninstall_egress_guard,
)


class TestREQ414NetworkEgressGuard:
    """Test suite for REQ-414 Network Egress Guard."""

    def test_is_llm_endpoint_openai(self):
        """Test detection of OpenAI endpoints."""
        assert is_llm_endpoint("api.openai.com")
        assert is_llm_endpoint("api.openai.com", 443)
        assert is_llm_endpoint("openai.com")
        assert is_llm_endpoint("any.openai.com")

    def test_is_llm_endpoint_anthropic(self):
        """Test detection of Anthropic endpoints."""
        assert is_llm_endpoint("api.anthropic.com")
        assert is_llm_endpoint("anthropic.com")
        assert is_llm_endpoint("any.anthropic.com")

    def test_is_llm_endpoint_google(self):
        """Test detection of Google endpoints."""
        assert is_llm_endpoint("generativelanguage.googleapis.com")
        assert is_llm_endpoint("any.googleapis.com")

    def test_is_llm_endpoint_localhost(self):
        """Test detection of localhost endpoints."""
        assert is_llm_endpoint("localhost")
        assert is_llm_endpoint("localhost", 8000)
        assert is_llm_endpoint("127.0.0.1")
        assert is_llm_endpoint("127.0.0.1", 8080)
        assert is_llm_endpoint("0.0.0.0")
        assert is_llm_endpoint("::1")

    def test_is_llm_endpoint_non_llm(self):
        """Test that non-LLM endpoints are not detected."""
        assert not is_llm_endpoint("example.com")
        assert not is_llm_endpoint("google.com")  # Not the API endpoint
        assert not is_llm_endpoint("github.com")
        assert not is_llm_endpoint("stackoverflow.com")

    def test_check_network_egress_allowed_non_llm(self):
        """Test that non-LLM endpoints are allowed."""
        # Should not raise
        result = check_network_egress_allowed("example.com", 443)
        assert result is True

    def test_check_network_egress_blocked_llm(self):
        """Test that LLM endpoints are blocked outside gateway."""
        with pytest.raises(NetworkEgressViolation) as exc_info:
            check_network_egress_allowed("api.openai.com", 443)

        assert "Unauthorized network egress to LLM endpoint" in str(exc_info.value)
        assert "REQ-414" in str(exc_info.value)

    def test_check_network_egress_blocked_localhost(self):
        """Test that localhost LLM endpoints are blocked."""
        with pytest.raises(NetworkEgressViolation) as exc_info:
            check_network_egress_allowed("localhost", 8000)

        assert "Unauthorized network egress to LLM endpoint" in str(exc_info.value)

    @patch("agentic_core.L2_execution.enforcement.network_egress_guard._is_in_gateway_context")
    def test_check_network_egress_allowed_in_gateway(self, mock_in_gateway):
        """Test that LLM endpoints are allowed within gateway context."""
        mock_in_gateway.return_value = True

        # Should not raise when in gateway context
        result = check_network_egress_allowed("api.openai.com", 443)
        assert result is True

    def test_egress_guard_environment_override(self):
        """Test that EGRESS_GUARD_DISABLED environment variable works."""
        with patch.dict(os.environ, {"EGRESS_GUARD_DISABLED": "1"}):
            # Should not raise even for LLM endpoint
            result = check_network_egress_allowed("api.openai.com", 443)
            assert result is True

    def test_install_egress_guard(self):
        """Test installation of egress guard."""
        # Save original
        original_connect = socket.socket.connect

        try:
            # Install guard
            install_egress_guard()

            # Check that socket.connect was patched
            assert socket.socket.connect != original_connect

        finally:
            # Restore
            uninstall_egress_guard()
            assert socket.socket.connect == original_connect

    def test_simulate_direct_llm_request_blocked(self):
        """Test that simulated direct LLM request is blocked."""
        with pytest.raises(NetworkEgressViolation):
            simulate_direct_llm_request()

    def test_simulate_direct_llm_request_blocked_custom(self):
        """Test that simulated direct LLM request with custom endpoint is blocked."""
        with pytest.raises(NetworkEgressViolation):
            simulate_direct_llm_request("api.anthropic.com", 443)

    def test_test_egress_guard(self):
        """Test the egress guard test function."""
        # Should return True when guard is working
        result = test_egress_guard()
        assert result is True

    def test_socket_connect_guard_integration(self):
        """Test that socket.connect guard works at the socket level."""
        try:
            # Install guard
            install_egress_guard()

            # Create a test socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Try to connect to LLM endpoint - should raise
            with pytest.raises(NetworkEgressViolation):
                sock.connect(("api.openai.com", 443))

            sock.close()

        finally:
            # Restore
            uninstall_egress_guard()

    def test_socket_connect_guard_allows_non_llm(self):
        """Test that socket.connect guard allows non-LLM connections."""
        try:
            # Install guard
            install_egress_guard()

            # Create a test socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Try to connect to non-LLM endpoint - should not raise NetworkEgressViolation
            # (It might raise other connection errors, but not our violation)
            try:
                sock.connect(("example.com", 80))
            except NetworkEgressViolation:
                pytest.fail("Non-LLM connection should not be blocked")
            except:
                # Other connection errors are expected (e.g., connection refused)
                pass

            sock.close()

        finally:
            # Restore
            uninstall_egress_guard()

    def test_caller_module_in_violation_message(self):
        """Test that caller module is included in violation message."""
        with pytest.raises(NetworkEgressViolation) as exc_info:
            check_network_egress_allowed("api.openai.com", 443, "test_module")

        assert "from test_module" in str(exc_info.value)

    def test_multiple_llm_endpoint_patterns(self):
        """Test various LLM endpoint patterns."""
        llm_endpoints = [
            ("api.openai.com", True),
            ("chat.openai.com", True),
            ("openai.com", True),
            ("api.anthropic.com", True),
            ("claude.ai", False),  # Not the API endpoint
            ("generativelanguage.googleapis.com", True),
            ("ai.googleapis.com", True),
            ("google.com", False),  # Not the API endpoint
            ("localhost:11434", True),  # Ollama
            ("127.0.0.1:8000", True),
            ("example.com", False),
            ("github.com", False),
        ]

        for endpoint, should_be_llm in llm_endpoints:
            if ":" in endpoint:
                host, port = endpoint.split(":", 1)
                port = int(port)
                result = is_llm_endpoint(host, port)
            else:
                result = is_llm_endpoint(endpoint)

            assert result == should_be_llm, f"Failed for {endpoint}"

    def test_egress_guard_disabled_skip_installation(self):
        """Test that guard installation is skipped when disabled."""
        with patch.dict(os.environ, {"EGRESS_GUARD_DISABLED": "1"}):
            # Save original
            original_connect = socket.socket.connect

            try:
                # Install guard - should be skipped
                install_egress_guard()

                # Should not have been patched
                assert socket.socket.connect == original_connect

            finally:
                # Cleanup (though not needed)
                uninstall_egress_guard()
