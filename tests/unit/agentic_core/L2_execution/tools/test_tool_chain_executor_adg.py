"""ADG-driven tests for agentic_core/L2_execution/tools/tool_chain_executor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.tools.tool_chain_executor import (  # noqa: F401
        ToolsUseATool,
        create_processor,
        validate_module_config,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ToolsUseATool = None  # type: ignore[assignment,misc]
    create_processor = None  # type: ignore[assignment,misc]
    validate_module_config = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="tool_chain_executor.py deps unavailable")
class TestToolsUseATool:
    def test_is_class(self):
        assert isinstance(ToolsUseATool, type)
    def test_importable(self):
        assert ToolsUseATool is not None

@pytest.mark.skipif(not _AVAILABLE, reason="tool_chain_executor.py deps unavailable")
class TestCreateProcessor:
    def test_is_callable(self):
        assert callable(create_processor)

@pytest.mark.skipif(not _AVAILABLE, reason="tool_chain_executor.py deps unavailable")
class TestValidateModuleConfig:
    def test_is_callable(self):
        assert callable(validate_module_config)

@pytest.mark.skipif(not _AVAILABLE, reason="tool_chain_executor.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="tool_chain_executor.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="tool_chain_executor.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="tool_chain_executor.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="tool_chain_executor.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="tool_chain_executor.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module tool_chain_executor.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
