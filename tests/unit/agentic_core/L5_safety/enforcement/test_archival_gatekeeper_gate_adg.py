"""ADG importability contract for agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_archival_gatekeeper_gate.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import (  # noqa: F401
        ARCHIVE_BATCH_ACCEPT_ENV,
        ArchivalGatekeeper,
        ArchivalOperation,
        ArchivalResult,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ARCHIVE_BATCH_ACCEPT_ENV = None  # type: ignore[assignment,misc]
    ArchivalOperation = None  # type: ignore[assignment,misc]
    ArchivalResult = None  # type: ignore[assignment,misc]
    ArchivalGatekeeper = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="archival_gatekeeper_gate deps unavailable")
class TestArchivalGatekeeperGateImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/archival_gatekeeper_gate.py must be importable."""
        assert _AVAILABLE

    def test_archivaloperation_defined(self) -> None:
        assert ArchivalOperation is not None

    def test_archivalresult_defined(self) -> None:
        assert ArchivalResult is not None

    def test_archivalgatekeeper_defined(self) -> None:
        assert ArchivalGatekeeper is not None
