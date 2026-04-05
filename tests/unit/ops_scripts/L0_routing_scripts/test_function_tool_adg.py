"""Behavioral tests for agentic_core.L0_routing.scripts.function_tool."""

import unittest

from ops_scripts.dev_tools.L0_routing_scripts.function_tool import FunctionTool, tool_registry


class GeneratedTest(unittest.TestCase):
    """Generated test class for agentic_core.L0_routing.scripts."""

    def test_execute(self):
        """Test FunctionTool.execute returns the wrapped function result."""
        tool = FunctionTool(name="demo", func=lambda: "ok", description="demo tool")
        result = tool.execute()
        self.assertEqual(result, "ok")

    def test_FunctionTool_init(self):
        """Test FunctionTool initialization."""
        instance = FunctionTool(name="demo", func=lambda: "ok", description="demo tool")
        self.assertIsNotNone(instance)
        self.assertEqual(instance.name, "demo")

    def test_FunctionTool_execute(self):
        """Test FunctionTool.execute method."""
        instance = FunctionTool(name="demo", func=lambda: "ok", description="demo tool")
        result = instance.execute()
        self.assertEqual(result, "ok")

    def test_tool_registry_exposed(self):
        """Test module exposes the registry object."""
        self.assertIsNotNone(tool_registry)


if __name__ == '__main__':
    unittest.main()
