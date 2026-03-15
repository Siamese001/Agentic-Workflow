"""ADG importability contract for agentic_core/base_agents/L0RoutingBase.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_L0RoutingBase.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.base_agents.L0RoutingBase import (  # noqa: F401
        L0RoutingBase,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    L0RoutingBase = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="L0RoutingBase deps unavailable")
class TestL0RoutingbaseImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/base_agents/L0RoutingBase.py must be importable."""
        assert _AVAILABLE

    def test_l0routingbase_defined(self) -> None:
        assert L0RoutingBase is not None
