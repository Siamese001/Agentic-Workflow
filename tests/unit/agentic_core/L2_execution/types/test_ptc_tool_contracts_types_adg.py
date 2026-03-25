"""ADG importability contract for agentic_core/L2_execution/types/ptc_tool_contracts_types.py."""
from __future__ import annotations

import agentic_core.L2_execution.types.ptc_tool_contracts_types  # noqa: F401


def test_module_importable():
    """Module ptc_tool_contracts_types must be importable."""
    assert agentic_core.L2_execution.types.ptc_tool_contracts_types is not None
