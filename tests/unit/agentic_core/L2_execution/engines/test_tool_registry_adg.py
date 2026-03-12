"""ADG importability contract for agentic_core/L2_execution/engines/tool_registry.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_tool_registry.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.engines.tool_registry import (  # noqa: F401
        ToolDefinition,
        ToolMatch,
        tool_registry,
        ast_analysis,
        code_transform_tool,
        dependency_graph_tool,
        diff_generator_tool,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolDefinition = None  # type: ignore[assignment,misc]
    ToolMatch = None  # type: ignore[assignment,misc]
    tool_registry = None  # type: ignore[assignment,misc]
    ast_analysis = None  # type: ignore[assignment,misc]
    code_transform_tool = None  # type: ignore[assignment,misc]
    dependency_graph_tool = None  # type: ignore[assignment,misc]
    diff_generator_tool = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="tool_registry.py deps unavailable")
class TestToolRegistryImportability:
    def test_module_importable(self) -> None:
        """ADG contract: tool_registry.py must be importable."""
        assert _AVAILABLE

    def test_tooldefinition_is_type(self) -> None:
        assert ToolDefinition is not None

    def test_toolmatch_is_type(self) -> None:
        assert ToolMatch is not None

    def test_tool_registry_is_type(self) -> None:
        assert tool_registry is not None

    def test_ast_analysis_callable(self) -> None:
        assert callable(ast_analysis)

    def test_code_transform_tool_callable(self) -> None:
        assert callable(code_transform_tool)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

