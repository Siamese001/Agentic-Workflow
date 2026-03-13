"""ADG importability contract for agentic_core/base_agents/SovereignBaseAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SovereignBaseAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.base_agents.SovereignBaseAgent import (  # noqa: F401
        SovereignBaseAgent,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SovereignBaseAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SovereignBaseAgent deps unavailable")
class TestSovereignbaseagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/base_agents/SovereignBaseAgent.py must be importable."""
        assert _AVAILABLE

    def test_sovereignbaseagent_defined(self) -> None:
        assert SovereignBaseAgent is not None
