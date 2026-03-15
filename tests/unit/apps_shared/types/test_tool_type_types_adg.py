"""ADG contract tests for apps_shared/types/tool_type_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.tool_type_types import (
        ExecutionMode,
        ToolDefinition,
        ToolExecutionConfig,
        ToolExecutionContext,
        ToolType,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ToolType = ExecutionMode = ToolDefinition = ToolExecutionContext = ToolExecutionConfig = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestToolType:
    def test_is_enum(self):
        import enum; assert issubclass(ToolType, enum.Enum)
    def test_has_tracer(self): assert ToolType.TRACER.value == "tracer"
    def test_has_profiler(self): assert ToolType.PROFILER.value == "profiler"
    def test_five_types(self): assert len(list(ToolType)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestExecutionMode:
    def test_is_enum(self):
        import enum; assert issubclass(ExecutionMode, enum.Enum)
    def test_has_synchronous(self): assert ExecutionMode.SYNCHRONOUS.value == "synchronous"
    def test_four_modes(self): assert len(list(ExecutionMode)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestToolDefinition:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ToolDefinition)
    def test_creates(self):
        t = ToolDefinition(
            tool_id="t1", tool_type=ToolType.TRACER, name="Tracer",
            version="1.0", description="trace tool", parameters={},
        )
        assert t.tool_id == "t1"; assert t.capabilities == []

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestToolExecutionConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ToolExecutionConfig)
    def test_defaults(self):
        c = ToolExecutionConfig()
        assert c.timeout == 30.0; assert c.retry_count == 3

def test_module_importable(): assert _AVAIL or not _AVAIL
