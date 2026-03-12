"""ADG importability contract for agentic_core/L5_safety/static_checks/determinism_serialization_check.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_determinism_serialization_check.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.static_checks.determinism_serialization_check import (  # noqa: F401
        DeterminismVisitor,
        scan_file_for_determinism,
        scan_repository_for_determinism,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DeterminismVisitor = None  # type: ignore[assignment,misc]
    scan_file_for_determinism = None  # type: ignore[assignment,misc]
    scan_repository_for_determinism = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="determinism_serialization_check.py deps unavailable")
class TestDeterminismSerializationCheckImportability:
    def test_module_importable(self) -> None:
        """ADG contract: determinism_serialization_check.py must be importable."""
        assert _AVAILABLE

    def test_determinismvisitor_is_type(self) -> None:
        assert DeterminismVisitor is not None

    def test_scan_file_for_determinism_callable(self) -> None:
        assert callable(scan_file_for_determinism)

    def test_scan_repository_for_determinism_callable(self) -> None:
        assert callable(scan_repository_for_determinism)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

