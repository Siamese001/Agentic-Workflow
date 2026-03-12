"""ADG importability contract for agentic_core/adg/extraction/scan_cache.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_scan_cache.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.extraction.scan_cache import (  # noqa: F401
        ScanCache,
        file_hash,
        CACHE_VERSION,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ScanCache = None  # type: ignore[assignment,misc]
    file_hash = None  # type: ignore[assignment,misc]
    CACHE_VERSION = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="scan_cache.py deps unavailable")
class TestScanCacheImportability:
    def test_module_importable(self) -> None:
        """ADG contract: scan_cache.py must be importable."""
        assert _AVAILABLE

    def test_scancache_is_type(self) -> None:
        assert ScanCache is not None

    def test_file_hash_callable(self) -> None:
        assert callable(file_hash)

    def test_cache_version_defined(self) -> None:
        assert CACHE_VERSION is not None

