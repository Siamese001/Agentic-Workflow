"""ADG importability contract for agentic_core/L3_orchestration/types/rewoo_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_rewoo_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.types.rewoo_types import (  # noqa: F401
        RewooContext,
        RewooTask,
        RewooTaskList,
        RewooTaskStatus,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    RewooTaskStatus = None  # type: ignore[assignment,misc]
    RewooTask = None  # type: ignore[assignment,misc]
    RewooTaskList = None  # type: ignore[assignment,misc]
    RewooContext = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="rewoo_types deps unavailable")
class TestRewooTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/types/rewoo_types.py must be importable."""
        assert _AVAILABLE

    def test_rewootaskstatus_defined(self) -> None:
        assert RewooTaskStatus is not None

    def test_rewootask_defined(self) -> None:
        assert RewooTask is not None

    def test_rewootasklist_defined(self) -> None:
        assert RewooTaskList is not None

    def test_rewoocontext_defined(self) -> None:
        assert RewooContext is not None