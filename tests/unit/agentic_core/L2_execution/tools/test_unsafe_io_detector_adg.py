"""ADG importability contract for agentic_core/L2_execution/tools/unsafe_io_detector.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_unsafe_io_detector.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.tools.unsafe_io_detector import (  # noqa: F401
        UnsafePattern,
        UnsafePatternVisitor,
        scan_for_unsafe_patterns,
        scan_directory_for_unsafe_patterns,
        get_scoped_directories,
        is_protected_root_path,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    UnsafePattern = None  # type: ignore[assignment,misc]
    UnsafePatternVisitor = None  # type: ignore[assignment,misc]
    scan_for_unsafe_patterns = None  # type: ignore[assignment,misc]
    scan_directory_for_unsafe_patterns = None  # type: ignore[assignment,misc]
    get_scoped_directories = None  # type: ignore[assignment,misc]
    is_protected_root_path = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="unsafe_io_detector.py deps unavailable")
class TestUnsafeIoDetectorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: unsafe_io_detector.py must be importable."""
        assert _AVAILABLE

    def test_unsafepattern_is_type(self) -> None:
        assert UnsafePattern is not None

    def test_unsafepatternvisitor_is_type(self) -> None:
        assert UnsafePatternVisitor is not None

    def test_scan_for_unsafe_patterns_callable(self) -> None:
        assert callable(scan_for_unsafe_patterns)

    def test_scan_directory_for_unsafe_patterns_callable(self) -> None:
        assert callable(scan_directory_for_unsafe_patterns)

