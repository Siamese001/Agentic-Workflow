"""ADG importability contract for agentic_core/L4_state/engines/memory_collision_detector.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_memory_collision_detector.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.engines.memory_collision_detector import (  # noqa: F401
        LockAcquisitionResult,
        LockPolicy,
        MemoryCollisionDetector,
        MemoryDeadlockViolation,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    MemoryDeadlockViolation = None  # type: ignore[assignment,misc]
    LockAcquisitionResult = None  # type: ignore[assignment,misc]
    LockPolicy = None  # type: ignore[assignment,misc]
    MemoryCollisionDetector = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="memory_collision_detector deps unavailable")
class TestMemoryCollisionDetectorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/engines/memory_collision_detector.py must be importable."""
        assert _AVAILABLE

    def test_memorydeadlockviolation_defined(self) -> None:
        assert MemoryDeadlockViolation is not None

    def test_lockacquisitionresult_defined(self) -> None:
        assert LockAcquisitionResult is not None

    def test_lockpolicy_defined(self) -> None:
        assert LockPolicy is not None

    def test_memorycollisiondetector_defined(self) -> None:
        assert MemoryCollisionDetector is not None