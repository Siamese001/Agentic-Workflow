from src.lic_agentic.rag.tool_registry import BaseTool, ToolRegistry, ToolResult, default_registry


class DummyTool(BaseTool):
    name = "dummy"
    cost = 0.1

    def run(self, query: str, context):
        return ToolResult(f"answer for {query}", ["http://dummy"], 42, 0.9)


def test_tool_registration_and_execution():
    registry = ToolRegistry()
    registry.register(DummyTool())
    tool = registry.resolve("dummy")
    assert isinstance(tool, DummyTool)
    result = tool.run("query", {})
    assert isinstance(result, ToolResult)
    assert result.confidence >= 0.0


def test_default_registry_includes_builtin_tools():
    registry = ToolRegistry.default_with_builtins()
    for name in ("web_search", "profile_lookup", "news"):
        assert name in registry.available()


def test_resolve_missing_tool_raises_key_error():
    registry = ToolRegistry()
    try:
        registry.resolve("missing")
    except KeyError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("Expected KeyError for missing tool")


def test_default_registry_factory_matches_classmethod():
    registry_fn = default_registry()
    registry_cls = ToolRegistry.default_with_builtins()
    assert registry_fn.available() == registry_cls.available()
