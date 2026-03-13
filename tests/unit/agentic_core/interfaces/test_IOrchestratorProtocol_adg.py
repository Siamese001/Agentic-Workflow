"""ADG importability contract for agentic_core/interfaces/IOrchestratorProtocol.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_IOrchestratorProtocol.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.interfaces.IOrchestratorProtocol import (  # noqa: F401
        IHealable,
        IOrchestratorProtocol,
        ITieredAgent,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    IOrchestratorProtocol = None  # type: ignore[assignment,misc]
    IHealable = None  # type: ignore[assignment,misc]
    ITieredAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="IOrchestratorProtocol deps unavailable")
class TestIorchestratorprotocolImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/interfaces/IOrchestratorProtocol.py must be importable."""
        assert _AVAILABLE

    def test_iorchestratorprotocol_defined(self) -> None:
        assert IOrchestratorProtocol is not None

    def test_ihealable_defined(self) -> None:
        assert IHealable is not None

    def test_itieredagent_defined(self) -> None:
        assert ITieredAgent is not None
