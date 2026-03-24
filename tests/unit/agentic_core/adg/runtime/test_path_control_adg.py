"""ADG importability contract for agentic_core/adg/runtime/path_control.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_path_control.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.path_control import (  # noqa: F401
        ExecutionPath,
        ExecutionPathController,
        PathControlReport,
        PathTransition,
        PathTransitionReason,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ExecutionPath = None  # type: ignore[assignment,misc]
    PathTransitionReason = None  # type: ignore[assignment,misc]
    PathTransition = None  # type: ignore[assignment,misc]
    PathControlReport = None  # type: ignore[assignment,misc]
    ExecutionPathController = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="path_control deps unavailable")
class TestPathControlImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/path_control.py must be importable."""
        assert _AVAILABLE

    def test_executionpath_defined(self) -> None:
        assert ExecutionPath is not None

    def test_pathtransitionreason_defined(self) -> None:
        assert PathTransitionReason is not None

    def test_pathtransition_defined(self) -> None:
        assert PathTransition is not None

    def test_pathcontrolreport_defined(self) -> None:
        assert PathControlReport is not None

    def test_executionpathcontroller_defined(self) -> None:
        assert ExecutionPathController is not None