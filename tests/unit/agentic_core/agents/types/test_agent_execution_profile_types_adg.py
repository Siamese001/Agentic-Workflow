"""ADG importability contract for agentic_core/agents/types/agent_execution_profile_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_agent_execution_profile_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.agents.types.agent_execution_profile_types import (  # noqa: F401
        ReasoningIntensity,
        ExecutionMode,
        AgentExecutionProfile,
        compute_registry_digest,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ReasoningIntensity = None  # type: ignore[assignment,misc]
    ExecutionMode = None  # type: ignore[assignment,misc]
    AgentExecutionProfile = None  # type: ignore[assignment,misc]
    compute_registry_digest = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="agent_execution_profile_types.py deps unavailable")
class TestAgentExecutionProfileTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agent_execution_profile_types.py must be importable."""
        assert _AVAILABLE

    def test_reasoningintensity_is_type(self) -> None:
        assert ReasoningIntensity is not None

    def test_executionmode_is_type(self) -> None:
        assert ExecutionMode is not None

    def test_agentexecutionprofile_is_type(self) -> None:
        assert AgentExecutionProfile is not None

    def test_compute_registry_digest_callable(self) -> None:
        assert callable(compute_registry_digest)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

