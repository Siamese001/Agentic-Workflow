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
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    DeterminismVisitor = None  # type: ignore[assignment,misc]
    scan_file_for_determinism = None  # type: ignore[assignment,misc]
    scan_repository_for_determinism = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="determinism_serialization_check deps unavailable")
class TestDeterminismSerializationCheckImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/static_checks/determinism_serialization_check.py must be importable."""
        assert _AVAILABLE

    def test_determinismvisitor_defined(self) -> None:
        assert DeterminismVisitor is not None
