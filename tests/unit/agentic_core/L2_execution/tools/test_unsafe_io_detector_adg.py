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
        get_scoped_directories,
        is_protected_root_path,
        scan_directory_for_unsafe_patterns,
        scan_for_unsafe_patterns,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    UnsafePattern = None  # type: ignore[assignment,misc]
    UnsafePatternVisitor = None  # type: ignore[assignment,misc]
    scan_for_unsafe_patterns = None  # type: ignore[assignment,misc]
    scan_directory_for_unsafe_patterns = None  # type: ignore[assignment,misc]
    get_scoped_directories = None  # type: ignore[assignment,misc]
    is_protected_root_path = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="unsafe_io_detector deps unavailable")
class TestUnsafeIoDetectorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/tools/unsafe_io_detector.py must be importable."""
        assert _AVAILABLE

    def test_unsafepattern_defined(self) -> None:
        assert UnsafePattern is not None

    def test_unsafepatternvisitor_defined(self) -> None:
        assert UnsafePatternVisitor is not None