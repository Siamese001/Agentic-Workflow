"""
Tool Contract Validation Tests - Guardian Tool Contract Tests.

Tests deterministic tool selection and parameter validation.
All tests use inline fixtures and are deterministic.
"""

import hashlib
import json
from typing import Any

import pytest


class TestToolContractValidation:
    """Test tool contract validation functionality."""

    def test_deterministic_tool_selection_hash(self):
        """Test that tool selection produces deterministic hash."""
        # Define tool selection with parameters
        tool_selection = {
            "tool": "web_search",
            "parameters": {"query": "python programming", "max_results": 10, "include_snippets": True},
        }

        # Create canonical representation (sorted keys)
        canonical = json.dumps(tool_selection, sort_keys=True, separators=(",", ":"))

        # Generate hash
        expected_hash = hashlib.sha256(canonical.encode()).hexdigest()

        # Verify hash is deterministic
        hash2 = hashlib.sha256(
            json.dumps(tool_selection, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        assert hash2 == expected_hash

        # Verify the actual expected hash for this specific tool selection
        assert expected_hash == "9aec53e0abb9f1c3a91483752900ea1b16062a7a7f60007c20152bba698457a0"

    def test_tool_selection_change_changes_hash(self):
        """Test that changing tool selection changes hash."""
        # Original selection
        selection1 = {"tool": "web_search", "parameters": {"query": "python programming", "max_results": 10}}

        # Changed tool
        selection2 = {"tool": "file_search", "parameters": {"query": "python programming", "max_results": 10}}

        # Generate hashes
        hash1 = hashlib.sha256(
            json.dumps(selection1, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        hash2 = hashlib.sha256(
            json.dumps(selection2, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        # Hashes should be different
        assert hash1 != hash2

    def test_parameter_change_changes_hash(self):
        """Test that changing parameters changes hash."""
        # Original selection
        selection1 = {"tool": "web_search", "parameters": {"query": "python programming", "max_results": 10}}

        # Changed parameter
        selection2 = {
            "tool": "web_search",
            "parameters": {
                "query": "java programming",  # Changed query
                "max_results": 10,
            },
        }

        # Generate hashes
        hash1 = hashlib.sha256(
            json.dumps(selection1, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        hash2 = hashlib.sha256(
            json.dumps(selection2, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        # Hashes should be different
        assert hash1 != hash2

    def test_reject_extra_parameters(self):
        """Test that extra parameters are rejected."""
        # Define expected tool contract
        expected_contract = {
            "tool": "web_search",
            "required_parameters": ["query"],
            "optional_parameters": ["max_results", "include_snippets"],
            "parameter_types": {"query": str, "max_results": int, "include_snippets": bool},
        }

        # Tool call with extra parameter
        tool_call = {
            "tool": "web_search",
            "parameters": {
                "query": "python programming",
                "max_results": 10,
                "include_snippets": True,
                "unexpected_param": "should_not_be_here",  # Extra parameter
            },
        }

        # Validate and reject extra parameters
        provided_params = set(tool_call["parameters"].keys())
        allowed_params = set(
            expected_contract["required_parameters"] + expected_contract["optional_parameters"]
        )

        extra_params = provided_params - allowed_params
        assert extra_params == {"unexpected_param"}

        # Should raise validation error for extra parameters
        with pytest.raises(ValueError, match="Unexpected parameters"):
            self._validate_tool_call(tool_call, expected_contract)

    def test_reject_type_mismatch(self):
        """Test that parameter type mismatches are rejected."""
        # Define expected tool contract
        expected_contract = {
            "tool": "web_search",
            "required_parameters": ["query"],
            "optional_parameters": ["max_results"],
            "parameter_types": {"query": str, "max_results": int},
        }

        # Tool call with wrong type
        tool_call = {
            "tool": "web_search",
            "parameters": {
                "query": "python programming",
                "max_results": "ten",  # Should be int, not str
            },
        }

        # Should raise validation error for type mismatch
        with pytest.raises(TypeError, match="Parameter max_results expected int, got str"):
            self._validate_tool_call(tool_call, expected_contract)

    def test_missing_required_parameter(self):
        """Test that missing required parameters are rejected."""
        # Define expected tool contract
        expected_contract = {
            "tool": "web_search",
            "required_parameters": ["query"],
            "optional_parameters": ["max_results"],
            "parameter_types": {"query": str, "max_results": int},
        }

        # Tool call missing required parameter
        tool_call = {
            "tool": "web_search",
            "parameters": {
                "max_results": 10
                # Missing "query" parameter
            },
        }

        # Should raise validation error for missing required parameter
        with pytest.raises(ValueError, match="Missing required parameter"):
            self._validate_tool_call(tool_call, expected_contract)

    def test_valid_tool_call_passes(self):
        """Test that valid tool calls pass validation."""
        # Define expected tool contract
        expected_contract = {
            "tool": "web_search",
            "required_parameters": ["query"],
            "optional_parameters": ["max_results", "include_snippets"],
            "parameter_types": {"query": str, "max_results": int, "include_snippets": bool},
        }

        # Valid tool call
        tool_call = {
            "tool": "web_search",
            "parameters": {"query": "python programming", "max_results": 10, "include_snippets": True},
        }

        # Should pass validation
        self._validate_tool_call(tool_call, expected_contract)  # Should not raise

    def _validate_tool_call(self, tool_call: dict[str, Any], contract: dict[str, Any]) -> None:
        """Validate tool call against contract."""
        # Check tool name matches
        if tool_call["tool"] != contract["tool"]:
            raise ValueError(f"Tool mismatch: expected {contract['tool']}, got {tool_call['tool']}")

        provided_params = set(tool_call["parameters"].keys())
        required_params = set(contract["required_parameters"])
        optional_params = set(contract["optional_parameters"])
        allowed_params = required_params | optional_params

        # Check for unexpected parameters
        extra_params = provided_params - allowed_params
        if extra_params:
            raise ValueError(f"Unexpected parameters: {extra_params}")

        # Check for missing required parameters
        missing_params = required_params - provided_params
        if missing_params:
            raise ValueError(f"Missing required parameter: {missing_params}")

        # Check parameter types
        for param_name, param_value in tool_call["parameters"].items():
            expected_type = contract["parameter_types"][param_name]
            if not isinstance(param_value, expected_type):
                raise TypeError(
                    f"Parameter {param_name} expected {expected_type.__name__}, got {type(param_value).__name__}"
                )


class TestComplexQueryValidation:
    """Test validation for complex multi-tool queries."""

    def test_complex_query_deterministic_hash(self):
        """Test that complex queries produce deterministic hashes."""
        complex_query = {
            "query_id": "complex_search_001",
            "tools": [
                {"tool": "web_search", "parameters": {"query": "python tutorials", "max_results": 5}},
                {"tool": "file_search", "parameters": {"pattern": "*.py", "directory": "/src"}},
                {
                    "tool": "code_analysis",
                    "parameters": {"file_path": "/src/main.py", "analysis_type": "syntax"},
                },
            ],
        }

        # Create canonical representation
        canonical = json.dumps(complex_query, sort_keys=True, separators=(",", ":"))

        # Generate deterministic hash
        hash1 = hashlib.sha256(canonical.encode()).hexdigest()
        hash2 = hashlib.sha256(
            json.dumps(complex_query, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 length

    def test_tool_order_affects_hash(self):
        """Test that changing tool order affects hash."""
        base_query = {
            "query_id": "test_query",
            "tools": [
                {"tool": "tool_a", "parameters": {"param": "value"}},
                {"tool": "tool_b", "parameters": {"param": "value"}},
            ],
        }

        reordered_query = {
            "query_id": "test_query",
            "tools": [
                {"tool": "tool_b", "parameters": {"param": "value"}},
                {"tool": "tool_a", "parameters": {"param": "value"}},
            ],
        }

        hash1 = hashlib.sha256(
            json.dumps(base_query, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        hash2 = hashlib.sha256(
            json.dumps(reordered_query, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        # Different order should produce different hash
        assert hash1 != hash2
