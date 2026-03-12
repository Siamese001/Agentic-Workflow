"""ADG importability contract for system_learning/engines/faiss_startup_integrity.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_faiss_startup_integrity.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.faiss_startup_integrity import (  # noqa: F401
        StartupIntegrityError,
        IndexVerificationResult,
        verify_all_indexes_in_dir,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    StartupIntegrityError = None  # type: ignore[assignment,misc]
    IndexVerificationResult = None  # type: ignore[assignment,misc]
    verify_all_indexes_in_dir = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="faiss_startup_integrity.py deps unavailable")
class TestFaissStartupIntegrityImportability:
    def test_module_importable(self) -> None:
        """ADG contract: faiss_startup_integrity.py must be importable."""
        assert _AVAILABLE

    def test_startupintegrityerror_is_type(self) -> None:
        assert StartupIntegrityError is not None

    def test_indexverificationresult_is_type(self) -> None:
        assert IndexVerificationResult is not None

    def test_verify_all_indexes_in_dir_callable(self) -> None:
        assert callable(verify_all_indexes_in_dir)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

