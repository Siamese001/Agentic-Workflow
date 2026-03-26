"""ADG importability contract for agentic_core/L5_safety/enforcement/circuit_breaker_gate.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.enforcement.circuit_breaker_gate  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.enforcement.circuit_breaker_gate  # noqa: F401
        """Module circuit_breaker_gate must be importable."""
        assert agentic_core.L5_safety.enforcement.circuit_breaker_gate is not None

    assert agentic_core.L5_safety.enforcement.circuit_breaker_gate is not None
