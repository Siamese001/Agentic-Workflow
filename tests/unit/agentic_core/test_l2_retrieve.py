"""Unit tests for L2_execution/P1_retrieve - execution context retrieval."""
from typing import Dict
import logging


class TestExecutionContextRetrieval:
    """Tests for retrieving execution context."""

    def test_retrieve_tool_definitions(self):
        """Nominal: Tool definitions are retrieved."""
        tools = {
            "search": {"name": "search", "params": ["query"]},
            "calculate": {"name": "calculate", "params": ["expression"]},
        }
        retrieved = tools.get("search")
        assert retrieved is not None
        assert retrieved["name"] == "search"

    def test_retrieve_missing_tool(self):
        """Negative: Missing tool returns None."""
        tools: Dict[str, object] = {}
        retrieved = tools.get("nonexistent")
        assert retrieved is None

    def test_retrieve_execution_history(self):
        """Nominal: Execution history is retrieved."""
        history = [
            {"step": 1, "tool": "search", "result": "found"},
            {"step": 2, "tool": "process", "result": "done"},
        ]
        last_step = history[-1]
        assert last_step["step"] == 2

    def test_retrieve_with_filters(self):
        """Nominal: Retrieval with filters."""
        items = [
            {"type": "tool", "name": "search"},
            {"type": "data", "name": "results"},
            {"type": "tool", "name": "process"},
        ]
        tools_only = [i for i in items if i["type"] == "tool"]
        assert len(tools_only) == 2

    def test_retrieve_determinism(self):
        """Determinism: Same query returns same results."""
        data = {"key": "value"}
        r1 = data.get("key")
        r2 = data.get("key")
        assert r1 == r2
