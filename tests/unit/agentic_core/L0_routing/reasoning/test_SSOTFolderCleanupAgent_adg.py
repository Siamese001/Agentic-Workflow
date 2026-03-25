"""ADG importability contract for agentic_core/L0_routing/reasoning/SSOTFolderCleanupAgent.py."""
from __future__ import annotations

import agentic_core.L0_routing.reasoning.SSOTFolderCleanupAgent  # noqa: F401


def test_module_importable():
    """Module SSOTFolderCleanupAgent must be importable."""
    assert agentic_core.L0_routing.reasoning.SSOTFolderCleanupAgent is not None
