"""ADG importability contract for agentic_core/L5_safety/enforcement/oscillation_firewall_gate.py."""
from __future__ import annotations

import agentic_core.L5_safety.enforcement.oscillation_firewall_gate  # noqa: F401


def test_module_importable():
    """Module oscillation_firewall_gate must be importable."""
    assert agentic_core.L5_safety.enforcement.oscillation_firewall_gate is not None
