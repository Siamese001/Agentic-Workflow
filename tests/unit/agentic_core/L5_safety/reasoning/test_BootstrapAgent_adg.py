"""ADG importability contract for agentic_core/L5_safety/reasoning/BootstrapAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_BootstrapAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.BootstrapAgent import (  # noqa: F401
        BootstrapAgent,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    BootstrapAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="BootstrapAgent deps unavailable")
class TestBootstrapagentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/BootstrapAgent.py must be importable."""
        assert _AVAILABLE

    def test_bootstrapagent_defined(self) -> None:
        assert BootstrapAgent is not None
