"""Behavioral tests for agentic_core.L0_routing.scripts.base_tool."""

import unittest

from ops_scripts.dev_tools.L0_routing_scripts.base_tool import BaseTool, FunctionalTool, ToolRegistry


class ConcreteTool(BaseTool):
    async def run(self, **kwargs) -> str:
        return "ok"


class GeneratedTest(unittest.TestCase):
    """Generated test class for agentic_core.L0_routing.scripts."""

    def test_register(self):
        """Test register stores a tool in the registry."""
        registry = ToolRegistry()
        tool = ConcreteTool(name="demo", description="demo tool")
        registry.register(tool)
        self.assertIsNotNone(registry.get("demo"))

    def test_get(self):
        """Test get returns the registered tool."""
        registry = ToolRegistry()
        tool = ConcreteTool(name="demo", description="demo tool")
        registry.register(tool)
        result = registry.get("demo")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "demo")

    def test_BaseTool_init(self):
        """Test BaseTool initialization via a concrete subclass."""
        instance = ConcreteTool(name="demo", description="demo tool")
        self.assertIsNotNone(instance)
        self.assertEqual(instance.name, "demo")

    def test_FunctionalTool_init(self):
        """Test FunctionalTool initialization."""
        instance = FunctionalTool(name="functional", description="functional tool", func=lambda: "ok")
        self.assertIsNotNone(instance)
        self.assertEqual(instance.name, "functional")


if __name__ == "__main__":
    unittest.main()
