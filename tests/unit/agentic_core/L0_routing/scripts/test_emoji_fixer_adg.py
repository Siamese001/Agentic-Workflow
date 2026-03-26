"""ADG-driven tests for agentic_core/L0_routing/scripts/emoji_fixer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L0_routing.scripts.emoji_fixer  # noqa: F401


def test_module_importable():
    import agentic_core.L0_routing.scripts.emoji_fixer  # noqa: F401
    """Module emoji_fixer must be importable."""
    assert agentic_core.L0_routing.scripts.emoji_fixer is not None
