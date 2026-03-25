"""ADG importability contract for agentic_core/agents/types/agent_execution_profile_types.py."""
from __future__ import annotations

import agentic_core.agents.types.agent_execution_profile_types  # noqa: F401


def test_module_importable():
    """Module agent_execution_profile_types must be importable."""
    assert agentic_core.agents.types.agent_execution_profile_types is not None
