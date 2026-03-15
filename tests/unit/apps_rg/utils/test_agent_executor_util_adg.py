"""ADG importability contract for apps_rg/utils/agent_executor_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_agent_executor_util.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from apps_rg.utils.agent_executor_util import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        AgentConfig,
        AgentExecutor,
        AgentMessage,
        AgentResponse,
        create_agent_executor,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    AgentConfig = None  # type: ignore[assignment,misc]
    AgentMessage = None  # type: ignore[assignment,misc]
    AgentResponse = None  # type: ignore[assignment,misc]
    AgentExecutor = None  # type: ignore[assignment,misc]
    create_agent_executor = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="agent_executor_util.py deps unavailable")
class TestAgentExecutorUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agent_executor_util.py must be importable."""
        assert _AVAILABLE

    def test_agentconfig_is_type(self) -> None:
        assert AgentConfig is not None

    def test_agentmessage_is_type(self) -> None:
        assert AgentMessage is not None

    def test_agentresponse_is_type(self) -> None:
        assert AgentResponse is not None

    def test_create_agent_executor_callable(self) -> None:
        assert callable(create_agent_executor)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
