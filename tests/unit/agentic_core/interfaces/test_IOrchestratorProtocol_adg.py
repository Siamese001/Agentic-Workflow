"""ADG importability contract for agentic_core/interfaces/IOrchestratorProtocol.py."""
from __future__ import annotations

import agentic_core.interfaces.IOrchestratorProtocol  # noqa: F401


def test_module_importable():
    """Module IOrchestratorProtocol must be importable."""
    assert agentic_core.interfaces.IOrchestratorProtocol is not None
