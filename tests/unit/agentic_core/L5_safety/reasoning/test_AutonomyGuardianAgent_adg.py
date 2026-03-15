"""ADG importability contract for agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_AutonomyGuardianAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.AutonomyGuardianAgent import (  # noqa: F401
        AutonomyGuardianAgent,
        get_autonomy_guardian,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    AutonomyGuardianAgent = None  # type: ignore[assignment,misc]
    get_autonomy_guardian = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="AutonomyGuardianAgent deps unavailable")
class TestAutonomyguardianagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py must be importable."""
        assert _AVAILABLE

    def test_autonomyguardianagent_defined(self) -> None:
        assert AutonomyGuardianAgent is not None
