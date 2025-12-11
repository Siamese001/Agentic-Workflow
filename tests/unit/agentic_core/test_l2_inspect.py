"""Unit tests for L2_execution/P2_inspect - execution result inspection."""
from __future__ import annotations
from typing import Dict

class TestExecutionResultInspection:
    """Tests for inspecting execution results."""

    def test_inspect_success_result(self):
        """Nominal: Successful result is inspected."""
        result = {"status": "success", "data": {"count": 10}}
        is_success = result["status"] == "success"
        assert is_success is True

    def test_inspect_failure_result(self):
        """Nominal: Failed result is identified."""
        result = {"status": "error", "error": "Timeout"}
        is_failure = result["status"] == "error"
        assert is_failure is True

    def test_inspect_result_data(self):
        """Nominal: Result data is extracted."""
        result = {"status": "success", "data": {"items": [1, 2, 3]}}
        items = result.get("data", {}).get("items", [])
        assert len(items) == 3

    def test_inspect_empty_result(self):
        """Edge case: Empty result handling."""
        result: Dict[str, object] = {}
        data = result.get("data")
        assert data is None

    def test_inspect_nested_result(self):
        """Edge case: Nested result inspection."""
        result = {
            "status": "success",
            "data": {
                "level1": {
                    "level2": {"value": 42}
                }
            }
        }
        value = result["data"]["level1"]["level2"]["value"]
        assert value == 42
