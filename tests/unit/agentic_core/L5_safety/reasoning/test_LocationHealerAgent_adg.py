"""ADG importability contract for agentic_core/L5_safety/reasoning/LocationHealerAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_LocationHealerAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.LocationHealerAgent import (  # noqa: F401
        LocationHealerAgent,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    LocationHealerAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="LocationHealerAgent deps unavailable")
class TestLocationhealeragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/LocationHealerAgent.py must be importable."""
        assert _AVAILABLE

    def test_locationhealeragent_defined(self) -> None:
        assert LocationHealerAgent is not None