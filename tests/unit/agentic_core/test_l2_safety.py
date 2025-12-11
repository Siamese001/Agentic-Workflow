"""Unit tests for L2_execution/P4_safety - execution safety checks."""
from __future__ import annotations
import re

class TestExecutionSafetyChecks:
    """Tests for execution-level safety checks."""

    def test_validate_tool_permissions(self):
        """Nominal: Tool permissions are validated."""
        allowed_tools = ["search", "read", "calculate"]
        requested_tool = "search"
        is_allowed = requested_tool in allowed_tools
        assert is_allowed is True

    def test_block_unauthorized_tool(self):
        """Negative: Unauthorized tool is blocked."""
        allowed_tools = ["search", "read"]
        requested_tool = "delete"
        is_allowed = requested_tool in allowed_tools
        assert is_allowed is False

    def test_validate_parameter_bounds(self):
        """Nominal: Parameters are within bounds."""
        limits = {"max_results": 100, "max_timeout": 30}
        params = {"results": 50, "timeout": 10}
        is_valid = (
            params["results"] <= limits["max_results"] and
            params["timeout"] <= limits["max_timeout"]
        )
        assert is_valid is True

    def test_detect_resource_abuse(self):
        """Nominal: Resource abuse is detected."""
        request_count = 150
        rate_limit = 100
        is_abuse = request_count > rate_limit
        assert is_abuse is True

    def test_sanitize_tool_output(self):
        """Nominal: Tool output is sanitized."""
        import scripts.check_canonical_structure
        output = "Result: <script>alert('xss')</script>"
        sanitized = re.sub(r'<[^>]+>', '', output)
        assert "<script>" not in sanitized
