"""ADG importability contract for agentic_core/L2_execution/types/llm_replay_types.py."""
from __future__ import annotations

import agentic_core.L2_execution.types.llm_replay_types  # noqa: F401


def test_module_importable():
    """Module llm_replay_types must be importable."""
    assert agentic_core.L2_execution.types.llm_replay_types is not None
