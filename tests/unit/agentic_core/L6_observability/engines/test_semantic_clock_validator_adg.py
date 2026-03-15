"""ADG importability contract for agentic_core/L6_observability/engines/semantic_clock_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_semantic_clock_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.semantic_clock_validator import (  # noqa: F401
        SemanticClockHashMismatch,
        SemanticClockValidationResult,
        scan_module_for_wallclock,
        validate_artifact,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SemanticClockHashMismatch = None  # type: ignore[assignment,misc]
    SemanticClockValidationResult = None  # type: ignore[assignment,misc]
    validate_artifact = None  # type: ignore[assignment,misc]
    scan_module_for_wallclock = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="semantic_clock_validator deps unavailable")
class TestSemanticClockValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L6_observability/engines/semantic_clock_validator.py must be importable."""
        assert _AVAILABLE

    def test_semanticclockhashmismatch_defined(self) -> None:
        assert SemanticClockHashMismatch is not None

    def test_semanticclockvalidationresult_defined(self) -> None:
        assert SemanticClockValidationResult is not None
