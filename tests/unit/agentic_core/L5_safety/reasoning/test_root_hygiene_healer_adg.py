"""ADG importability contract for agentic_core/L5_safety/reasoning/root_hygiene_healer.py."""
from __future__ import annotations

import agentic_core.L5_safety.reasoning.root_hygiene_healer  # noqa: F401


def test_module_importable():
    """Module root_hygiene_healer must be importable."""
    assert agentic_core.L5_safety.reasoning.root_hygiene_healer is not None
