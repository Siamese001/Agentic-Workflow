"""ADG importability contract for agentic_core/L2_execution/types/agent_output_contract_types.py."""
from __future__ import annotations

import agentic_core.L2_execution.types.agent_output_contract_types  # noqa: F401


def test_module_importable():
    """Module agent_output_contract_types must be importable."""
    assert agentic_core.L2_execution.types.agent_output_contract_types is not None
