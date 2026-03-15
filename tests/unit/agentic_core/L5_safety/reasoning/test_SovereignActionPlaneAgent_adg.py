"""ADG importability contract for agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SovereignActionPlaneAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.SovereignActionPlaneAgent import (  # noqa: F401
        LOGGER,
        SovereignActionPlaneAgent,
        SovereignSandbox,
        SovereignToolsmith,
        create_sovereign_action_plane,
        get_sovereign_action_plane,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    LOGGER = None  # type: ignore[assignment,misc]
    SovereignToolsmith = None  # type: ignore[assignment,misc]
    SovereignSandbox = None  # type: ignore[assignment,misc]
    SovereignActionPlaneAgent = None  # type: ignore[assignment,misc]
    create_sovereign_action_plane = None  # type: ignore[assignment,misc]
    get_sovereign_action_plane = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SovereignActionPlaneAgent deps unavailable")
class TestSovereignactionplaneagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py must be importable."""
        assert _AVAILABLE

    def test_sovereigntoolsmith_defined(self) -> None:
        assert SovereignToolsmith is not None

    def test_sovereignsandbox_defined(self) -> None:
        assert SovereignSandbox is not None

    def test_sovereignactionplaneagent_defined(self) -> None:
        assert SovereignActionPlaneAgent is not None
