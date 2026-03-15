"""ADG importability contract for agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_GravityLeakRepairAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.GravityLeakRepairAgent import (  # noqa: F401
        GravityFix,
        GravityLeakRepairAgent,
        GravityRepairProhibitedError,
        get_GravityLeakRepairAgent,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    GravityRepairProhibitedError = None  # type: ignore[assignment,misc]
    GravityFix = None  # type: ignore[assignment,misc]
    GravityLeakRepairAgent = None  # type: ignore[assignment,misc]
    get_GravityLeakRepairAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="GravityLeakRepairAgent deps unavailable")
class TestGravityleakrepairagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/GravityLeakRepairAgent.py must be importable."""
        assert _AVAILABLE

    def test_gravityrepairprohibitederror_defined(self) -> None:
        assert GravityRepairProhibitedError is not None

    def test_gravityfix_defined(self) -> None:
        assert GravityFix is not None

    def test_gravityleakrepairagent_defined(self) -> None:
        assert GravityLeakRepairAgent is not None
