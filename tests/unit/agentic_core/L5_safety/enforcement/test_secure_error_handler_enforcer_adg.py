"""ADG importability contract for agentic_core/L5_safety/enforcement/secure_error_handler_enforcer.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.enforcement.secure_error_handler_enforcer  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.enforcement.secure_error_handler_enforcer  # noqa: F401
        """Module secure_error_handler_enforcer must be importable."""
        assert agentic_core.L5_safety.enforcement.secure_error_handler_enforcer is not None

    assert agentic_core.L5_safety.enforcement.secure_error_handler_enforcer is not None
