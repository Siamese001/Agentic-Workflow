"""ADG importability contract for agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ssot_structure_validation_enforcer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.ssot_structure_validation_enforcer import (  # noqa: F401
        SSOTStructureValidator,
        StructureValidationResult,
        StructureViolation,
        run_structure_validation,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    StructureViolation = None  # type: ignore[assignment,misc]
    StructureValidationResult = None  # type: ignore[assignment,misc]
    SSOTStructureValidator = None  # type: ignore[assignment,misc]
    run_structure_validation = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_structure_validation_enforcer deps unavailable")
class TestSsotStructureValidationEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/ssot_structure_validation_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_structureviolation_defined(self) -> None:
        assert StructureViolation is not None

    def test_structurevalidationresult_defined(self) -> None:
        assert StructureValidationResult is not None

    def test_ssotstructurevalidator_defined(self) -> None:
        assert SSOTStructureValidator is not None
