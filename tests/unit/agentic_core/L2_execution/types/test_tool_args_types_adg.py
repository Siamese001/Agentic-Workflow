"""ADG importability contract for agentic_core/L2_execution/types/tool_args_types.py."""
from __future__ import annotations

import agentic_core.L2_execution.types.tool_args_types  # noqa: F401


def test_module_importable():
    """Module tool_args_types must be importable."""
    assert agentic_core.L2_execution.types.tool_args_types is not None
