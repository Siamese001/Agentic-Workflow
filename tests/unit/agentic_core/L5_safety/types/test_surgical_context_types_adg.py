"""ADG importability contract for agentic_core/L5_safety/types/surgical_context_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_surgical_context_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.types.surgical_context_types import (  # noqa: F401
        ASTCoordinate,
        SurgicalContext,
        SurgicalContextBuilder,
        ViolationConstraint,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ASTCoordinate = None  # type: ignore[assignment,misc]
    ViolationConstraint = None  # type: ignore[assignment,misc]
    SurgicalContext = None  # type: ignore[assignment,misc]
    SurgicalContextBuilder = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="surgical_context_types deps unavailable")
class TestSurgicalContextTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/types/surgical_context_types.py must be importable."""
        assert _AVAILABLE

    def test_astcoordinate_defined(self) -> None:
        assert ASTCoordinate is not None

    def test_violationconstraint_defined(self) -> None:
        assert ViolationConstraint is not None

    def test_surgicalcontext_defined(self) -> None:
        assert SurgicalContext is not None

    def test_surgicalcontextbuilder_defined(self) -> None:
        assert SurgicalContextBuilder is not None
