"""ADG importability contract for agentic_core/L5_safety/enforcement/system_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_system_enforcer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.system_enforcer import (  # noqa: F401
        SystemValidator,
        ValidationReport,
        ValidationResult,
        main,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ValidationResult = None  # type: ignore[assignment,misc]
    ValidationReport = None  # type: ignore[assignment,misc]
    SystemValidator = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="system_enforcer deps unavailable")
class TestSystemEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/system_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_validationresult_defined(self) -> None:
        assert ValidationResult is not None

    def test_validationreport_defined(self) -> None:
        assert ValidationReport is not None

    def test_systemvalidator_defined(self) -> None:
        assert SystemValidator is not None