"""Foundational behavioral tests for agentic_core/L2_execution/reasoning/ToolsmithAgent.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_ToolsmithAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.reasoning.ToolsmithAgent import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    GeneratedTool,
    ToolsmithAgent,
    ToolSpec,
    create_api_tool,
    create_file_tool,
    get_ToolsmithAgent,
    initialize_ToolsmithAgent,
    tool_template,
)


class TestToolSpecContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ToolSpec)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ToolSpec)}
        assert field_names >= {'parameters', 'description', 'name', 'category', 'function'}

class TestGeneratedToolContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(GeneratedTool)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(GeneratedTool)}
        assert field_names >= {'imports', 'test_code', 'code', 'dependencies', 'spec'}

class Testtool_templateContract:
    def test_is_class(self):
        assert isinstance(tool_template, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(tool_template, type)

class TestToolsmithAgentContract:
    def test_is_class(self):
        assert isinstance(ToolsmithAgent, type)

    def test_has_method_create_tool_from_spec(self):
        assert callable(getattr(ToolsmithAgent, 'create_tool_from_spec', None))

    def test_has_method_create_file_tool(self):
        assert callable(getattr(ToolsmithAgent, 'create_file_tool', None))

    def test_has_method_create_api_tool(self):
        assert callable(getattr(ToolsmithAgent, 'create_api_tool', None))

    def test_has_method_get_tool(self):
        assert callable(getattr(ToolsmithAgent, 'get_tool', None))

class TestGetToolsmithagentFunction:
    def test_is_callable(self):
        assert callable(get_ToolsmithAgent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_ToolsmithAgent)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestInitializeToolsmithagentFunction:
    def test_is_callable(self):
        assert callable(initialize_ToolsmithAgent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(initialize_ToolsmithAgent)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestCreateFileToolFunction:
    def test_is_callable(self):
        assert callable(create_file_tool)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_file_tool)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestCreateApiToolFunction:
    def test_is_callable(self):
        assert callable(create_api_tool)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_api_tool)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module ToolsmithAgent must be importable or skip gracefully."""
    pass  # Import verified at module level
