"""ADG importability contract for agentic_core/L5_safety/enforcement/verification_gate.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.enforcement.verification_gate  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.enforcement.verification_gate  # noqa: F401
        """Module verification_gate must be importable."""
        assert agentic_core.L5_safety.enforcement.verification_gate is not None

    assert agentic_core.L5_safety.enforcement.verification_gate is not None
