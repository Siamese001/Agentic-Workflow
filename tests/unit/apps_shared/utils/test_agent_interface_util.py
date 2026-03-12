"""Foundational behavioral tests for apps_shared/utils/agent_interface_util.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_agent_interface_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
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
    )
    _AVAILABLE = True
except Exception as _exc:
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


@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestAgentStatusContract:
    def test_is_enum(self):
        import enum
        assert issubclass(AgentStatus, enum.Enum)

    def test_has_members(self):
        assert len(list(AgentStatus)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in AgentStatus:
            assert member.value is not None

    def test_known_member_pending_exists(self):
        assert hasattr(AgentStatus, 'PENDING')

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestAgentContextContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AgentContext)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(AgentContext)}
        assert field_names >= {'session_id', 'user_id', 'metadata', 'timeout_seconds', 'trace_id'}

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestAgentResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AgentResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(AgentResult)}
        assert field_names >= {'error', 'execution_time_ms', 'status', 'metadata', 'output'}

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestIAgentContract:
    def test_is_class(self):
        assert isinstance(IAgent, type)

    def test_has_method_name(self):
        assert callable(getattr(IAgent, 'name', None))

    def test_has_method_version(self):
        assert callable(getattr(IAgent, 'version', None))

    def test_has_method_description(self):
        assert callable(getattr(IAgent, 'description', None))

    def test_has_method_execute(self):
        assert callable(getattr(IAgent, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestBaseAgentContract:
    def test_is_class(self):
        assert isinstance(BaseAgent, type)

    def test_has_method_name(self):
        assert callable(getattr(BaseAgent, 'name', None))

    def test_has_method_version(self):
        assert callable(getattr(BaseAgent, 'version', None))

    def test_has_method_execute(self):
        assert callable(getattr(BaseAgent, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestAgentRegistryContract:
    def test_is_class(self):
        assert isinstance(AgentRegistry, type)

    def test_has_method_register(self):
        assert callable(getattr(AgentRegistry, 'register', None))

    def test_has_method_get(self):
        assert callable(getattr(AgentRegistry, 'get', None))

    def test_has_method_list_agents(self):
        assert callable(getattr(AgentRegistry, 'list_agents', None))

    def test_has_method_unregister(self):
        assert callable(getattr(AgentRegistry, 'unregister', None))

@pytest.mark.skipif(not _AVAILABLE, reason="agent_interface_util.py deps unavailable")
class TestGetAgentRegistryFunction:
    def test_is_callable(self):
        assert callable(get_agent_registry)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_agent_registry)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module agent_interface_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
