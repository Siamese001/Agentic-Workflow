"""ADG importability contract for agentic_core/L2_execution/tools/ptc_contract.py."""
from __future__ import annotations

import agentic_core.L2_execution.tools.ptc_contract  # noqa: F401


def test_module_importable():
    """Module ptc_contract must be importable."""
    assert agentic_core.L2_execution.tools.ptc_contract is not None
