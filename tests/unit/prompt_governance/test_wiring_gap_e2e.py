""""""
from __future__ import annotations


def test_module_importable():
    """Module CodeHealerAgent must be importable."""
    import agentic_core.L5_safety.reasoning.CodeHealerAgent  # noqa: F401

    assert agentic_core.L5_safety.reasoning.CodeHealerAgent is not None
