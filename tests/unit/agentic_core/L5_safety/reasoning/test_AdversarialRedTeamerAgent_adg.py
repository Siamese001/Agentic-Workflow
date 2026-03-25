"""ADG importability contract for agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.AdversarialRedTeamerAgent  # noqa: F401


def test_module_importable():
    """Module AdversarialRedTeamerAgent must be importable."""
    assert agentic_core.L5_safety.reasoning.AdversarialRedTeamerAgent is not None
