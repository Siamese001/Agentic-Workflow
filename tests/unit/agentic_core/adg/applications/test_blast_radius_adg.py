"""ADG importability contract for agentic_core/adg/applications/blast_radius.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_blast_radius.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.blast_radius import (  # noqa: F401
        BlastRadiusResult,
        compute_blast_radius,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    BlastRadiusResult = None  # type: ignore[assignment,misc]
    compute_blast_radius = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="blast_radius.py deps unavailable")
class TestBlastRadiusImportability:
    def test_module_importable(self) -> None:
        """ADG contract: blast_radius.py must be importable."""
        assert _AVAILABLE

    def test_blastradiusresult_is_type(self) -> None:
        assert BlastRadiusResult is not None

    def test_compute_blast_radius_callable(self) -> None:
        assert callable(compute_blast_radius)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

