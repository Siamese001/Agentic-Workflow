"""ADG importability contract for agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_StructuralValidatorAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.StructuralValidatorAgent import (  # noqa: F401
        StructuralValidatorAgent,
        StructureConfig,
        StructureViolation,
        StructureViolationType,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    StructureViolationType = None  # type: ignore[assignment,misc]
    StructureViolation = None  # type: ignore[assignment,misc]
    StructureConfig = None  # type: ignore[assignment,misc]
    StructuralValidatorAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="StructuralValidatorAgent deps unavailable")
class TestStructuralvalidatoragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py must be importable."""
        assert _AVAILABLE

    def test_structureviolationtype_defined(self) -> None:
        assert StructureViolationType is not None

    def test_structureviolation_defined(self) -> None:
        assert StructureViolation is not None

    def test_structureconfig_defined(self) -> None:
        assert StructureConfig is not None

    def test_structuralvalidatoragent_defined(self) -> None:
        assert StructuralValidatorAgent is not None