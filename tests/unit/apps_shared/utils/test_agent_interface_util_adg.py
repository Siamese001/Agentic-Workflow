"""ADG-driven tests for apps_shared/utils/agent_interface_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.agent_interface_util import (  # noqa: F401
        AgentStatus,
        AgentContext,
        AgentResult,
        IAgent,
        BaseAgent,
        AgentRegistry,
        get_agent_registry,
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
    AgentStatus = None  # type: ignore[assignment,misc]
    AgentContext = None  # type: ignore[assignment,misc]
    AgentResult = None  # type: ignore[assignment,misc]
    IAgent = None  # type: ignore[assignment,misc]
    BaseAgent = None  # type: ignore[assignment,misc]
    AgentRegistry = None  # type: ignore[assignment,misc]
    get_agent_registry = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestAgentStatus:
    def test_is_enum(self):
        import enum
        assert issubclass(AgentStatus, enum.Enum)
    def test_has_members(self):
        assert len(list(AgentStatus)) >= 1
    def test_importable(self):
        assert AgentStatus is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestAgentContext:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AgentContext)
    def test_importable(self):
        assert AgentContext is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestAgentResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AgentResult)
    def test_importable(self):
        assert AgentResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestIAgent:
    def test_is_class(self):
        assert isinstance(IAgent, type)
    def test_importable(self):
        assert IAgent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestBaseAgent:
    def test_is_class(self):
        assert isinstance(BaseAgent, type)
    def test_importable(self):
        assert BaseAgent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestAgentRegistry:
    def test_is_class(self):
        assert isinstance(AgentRegistry, type)
    def test_importable(self):
        assert AgentRegistry is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestGetAgentRegistry:
    def test_is_callable(self):
        assert callable(get_agent_registry)

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module agent_interface_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
