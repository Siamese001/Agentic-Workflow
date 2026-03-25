"""ADG importability contract for agentic_core/L3_orchestration/engines/handshake_state_machine.py."""
from __future__ import annotations

import agentic_core.L3_orchestration.engines.handshake_state_machine  # noqa: F401


def test_module_importable():
    """Module handshake_state_machine must be importable."""
    assert agentic_core.L3_orchestration.engines.handshake_state_machine is not None
