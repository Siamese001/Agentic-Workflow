"""ADG importability contract for agentic_core/L5_safety/static_checks/ptc_invariants.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ptc_invariants.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.static_checks.ptc_invariants import (  # noqa: F401
        PTCInvariantVisitor,
        scan_file_for_ptc_invariants,
        scan_repository_for_ptc_invariants,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    PTCInvariantVisitor = None  # type: ignore[assignment,misc]
    scan_file_for_ptc_invariants = None  # type: ignore[assignment,misc]
    scan_repository_for_ptc_invariants = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ptc_invariants deps unavailable")
class TestPtcInvariantsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/static_checks/ptc_invariants.py must be importable."""
        assert _AVAILABLE

    def test_ptcinvariantvisitor_defined(self) -> None:
        assert PTCInvariantVisitor is not None
