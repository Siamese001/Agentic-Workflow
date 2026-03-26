"""ADG importability contract for agentic_core/L5_safety/security/side_effect_guard.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.security.side_effect_guard  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.security.side_effect_guard  # noqa: F401
        """Module side_effect_guard must be importable."""
        assert agentic_core.L5_safety.security.side_effect_guard is not None

    assert agentic_core.L5_safety.security.side_effect_guard is not None
