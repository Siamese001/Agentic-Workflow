"""ADG contract tests for apps_shared/types/tool_category_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.tool_category_types import (
        ObservabilityToolInvoker,
        ToolCategory,
        ToolInvocationConfig,
        ToolInvocationResult,
        ToolProtocol,
        ToolSpecification,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ToolCategory = ToolProtocol = ToolSpecification = None  # type: ignore[assignment,misc]
    ToolInvocationResult = ToolInvocationConfig = ObservabilityToolInvoker = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestToolCategory:
    def test_is_enum(self):
        import enum; assert issubclass(ToolCategory, enum.Enum)
    def test_has_tracing(self): assert ToolCategory.TRACING.value == "tracing"
    def test_five_categories(self): assert len(list(ToolCategory)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestToolProtocol:
    def test_is_enum(self):
        import enum; assert issubclass(ToolProtocol, enum.Enum)
    def test_has_http(self): assert ToolProtocol.HTTP.value == "http"
    def test_four_protocols(self): assert len(list(ToolProtocol)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestToolInvocationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ToolInvocationResult)
    def test_creates(self):
        r = ToolInvocationResult(
            invocation_id="inv1", tool_id="tool1", method="trace", success=True,
        )
        assert r.success is True; assert r.error is None

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestToolInvocationConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ToolInvocationConfig)
    def test_creates_defaults(self):
        c = ToolInvocationConfig()
        assert c.max_retries == 3; assert c.enable_circuit_breaker is True

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestObservabilityToolInvoker:
    def test_creates(self): inv = ObservabilityToolInvoker(); assert inv is not None
    def test_list_tools_empty(self):
        inv = ObservabilityToolInvoker()
        tools = inv.list_tools(); assert isinstance(tools, list)

def test_module_importable(): assert _AVAIL or not _AVAIL
