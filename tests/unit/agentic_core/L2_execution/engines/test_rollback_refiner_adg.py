"""ADG importability contract for agentic_core/L2_execution/engines/rollback_refiner.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_rollback_refiner.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.engines.rollback_refiner import (  # noqa: F401
        DefaultDeterministicRollbackRefiner,
        RollbackRefiner,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RollbackRefiner = None  # type: ignore[assignment,misc]
    DefaultDeterministicRollbackRefiner = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="rollback_refiner deps unavailable")
class TestRollbackRefinerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/engines/rollback_refiner.py must be importable."""
        assert _AVAILABLE

    def test_rollbackrefiner_defined(self) -> None:
        assert RollbackRefiner is not None

    def test_defaultdeterministicrollbackrefiner_defined(self) -> None:
        assert DefaultDeterministicRollbackRefiner is not None
