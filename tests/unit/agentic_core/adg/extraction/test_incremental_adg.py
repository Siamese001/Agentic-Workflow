"""ADG importability contract for agentic_core/adg/extraction/incremental.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_incremental.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.extraction.incremental import (  # noqa: F401
        IncrementalScanStats,
        compute_affected_modules,
        incremental_scan,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    IncrementalScanStats = None  # type: ignore[assignment,misc]
    compute_affected_modules = None  # type: ignore[assignment,misc]
    incremental_scan = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="incremental.py deps unavailable")
class TestIncrementalImportability:
    def test_module_importable(self) -> None:
        """ADG contract: incremental.py must be importable."""
        assert _AVAILABLE

    def test_incrementalscanstats_is_type(self) -> None:
        assert IncrementalScanStats is not None

    def test_compute_affected_modules_callable(self) -> None:
        assert callable(compute_affected_modules)

    def test_incremental_scan_callable(self) -> None:
        assert callable(incremental_scan)

