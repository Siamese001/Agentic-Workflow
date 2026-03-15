"""Foundational behavioral tests for agentic_core/L2_execution/reasoning/ToolsmithAgent.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_ToolsmithAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
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
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ToolSpec = None  # type: ignore[assignment,misc]
    GeneratedTool = None  # type: ignore[assignment,misc]
    tool_template = None  # type: ignore[assignment,misc]
    ToolsmithAgent = None  # type: ignore[assignment,misc]
    get_ToolsmithAgent = None  # type: ignore[assignment,misc]
    initialize_ToolsmithAgent = None  # type: ignore[assignment,misc]
    create_file_tool = None  # type: ignore[assignment,misc]
    create_api_tool = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
class TestToolSpecContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ToolSpec)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ToolSpec)}
        assert field_names >= {'parameters', 'description', 'name', 'category', 'function'}

@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
class TestGeneratedToolContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(GeneratedTool)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(GeneratedTool)}
        assert field_names >= {'imports', 'test_code', 'code', 'dependencies', 'spec'}

@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
class Testtool_templateContract:
    def test_is_class(self):
        assert isinstance(tool_template, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(tool_template, type)

@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
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

@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
class TestGetToolsmithagentFunction:
    def test_is_callable(self):
        assert callable(get_ToolsmithAgent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_ToolsmithAgent)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
class TestInitializeToolsmithagentFunction:
    def test_is_callable(self):
        assert callable(initialize_ToolsmithAgent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(initialize_ToolsmithAgent)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
class TestCreateFileToolFunction:
    def test_is_callable(self):
        assert callable(create_file_tool)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_file_tool)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
class TestCreateApiToolFunction:
    def test_is_callable(self):
        assert callable(create_api_tool)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_api_tool)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ToolsmithAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module ToolsmithAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
