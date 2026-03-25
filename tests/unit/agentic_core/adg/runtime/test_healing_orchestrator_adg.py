"""ADG importability contract for agentic_core/adg/runtime/healing_orchestrator.py."""
from __future__ import annotations

import agentic_core.adg.runtime.healing_orchestrator  # noqa: F401


def test_module_importable():
    """Module healing_orchestrator must be importable."""
    assert agentic_core.adg.runtime.healing_orchestrator is not None
