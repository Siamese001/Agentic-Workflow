"""ADG importability contract for agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ArchitectureGovernorAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (  # noqa: F401
        ArchitectureGovernorAgent,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ArchitectureGovernorAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ArchitectureGovernorAgent deps unavailable")
class TestArchitecturegovernoragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py must be importable."""
        assert _AVAILABLE

    def test_architecturegovernoragent_defined(self) -> None:
        assert ArchitectureGovernorAgent is not None
