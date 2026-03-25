"""ADG importability contract for agentic_core/L5_safety/enforcement/circuit_breaker_gate.py."""
from __future__ import annotations

import agentic_core.L5_safety.enforcement.circuit_breaker_gate  # noqa: F401


def test_module_importable():
    """Module circuit_breaker_gate must be importable."""
    assert agentic_core.L5_safety.enforcement.circuit_breaker_gate is not None
