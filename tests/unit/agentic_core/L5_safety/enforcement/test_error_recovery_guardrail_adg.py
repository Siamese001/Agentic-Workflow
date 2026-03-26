"""ADG importability contract for agentic_core/L5_safety/enforcement/error_recovery_guardrail.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L5_safety.enforcement.error_recovery_guardrail  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.enforcement.error_recovery_guardrail  # noqa: F401
    """Module error_recovery_guardrail must be importable."""
    assert agentic_core.L5_safety.enforcement.error_recovery_guardrail is not None
