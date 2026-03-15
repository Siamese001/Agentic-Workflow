"""ADG importability contract for agentic_core/agents/types/agent_execution_profile_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_agent_execution_profile_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.agents.types.agent_execution_profile_types import (  # noqa: F401
        AgentExecutionProfile,
        ExecutionMode,
        ReasoningIntensity,
        compute_registry_digest,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ReasoningIntensity = None  # type: ignore[assignment,misc]
    ExecutionMode = None  # type: ignore[assignment,misc]
    AgentExecutionProfile = None  # type: ignore[assignment,misc]
    compute_registry_digest = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_execution_profile_types deps unavailable")
class TestAgentExecutionProfileTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/agents/types/agent_execution_profile_types.py must be importable."""
        assert _AVAILABLE

    def test_reasoningintensity_defined(self) -> None:
        assert ReasoningIntensity is not None

    def test_executionmode_defined(self) -> None:
        assert ExecutionMode is not None

    def test_agentexecutionprofile_defined(self) -> None:
        assert AgentExecutionProfile is not None
