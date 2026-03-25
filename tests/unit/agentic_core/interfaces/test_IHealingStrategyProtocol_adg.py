"""ADG importability contract for agentic_core/interfaces/IHealingStrategyProtocol.py."""
from __future__ import annotations

import agentic_core.interfaces.IHealingStrategyProtocol  # noqa: F401


def test_module_importable():
    """Module IHealingStrategyProtocol must be importable."""
    assert agentic_core.interfaces.IHealingStrategyProtocol is not None
