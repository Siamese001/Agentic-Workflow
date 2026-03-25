""""""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.CodeHealerAgent  # noqa: F401


def test_module_importable():
    """Module CodeHealerAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.CodeHealerAgent is not None
