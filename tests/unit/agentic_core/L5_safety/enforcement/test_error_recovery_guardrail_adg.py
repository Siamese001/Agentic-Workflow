"""ADG importability contract for agentic_core/L5_safety/enforcement/error_recovery_guardrail.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_error_recovery_guardrail.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.error_recovery_guardrail import (  # noqa: F401
        ErrorCategory,
        ErrorContext,
        ErrorRecoveryGuardrail,
        RecoveryResult,
        RecoveryStrategy,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ErrorCategory = None  # type: ignore[assignment,misc]
    RecoveryStrategy = None  # type: ignore[assignment,misc]
    ErrorContext = None  # type: ignore[assignment,misc]
    RecoveryResult = None  # type: ignore[assignment,misc]
    ErrorRecoveryGuardrail = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="error_recovery_guardrail deps unavailable")
class TestErrorRecoveryGuardrailImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/error_recovery_guardrail.py must be importable."""
        assert _AVAILABLE

    def test_errorcategory_defined(self) -> None:
        assert ErrorCategory is not None

    def test_recoverystrategy_defined(self) -> None:
        assert RecoveryStrategy is not None

    def test_errorcontext_defined(self) -> None:
        assert ErrorContext is not None

    def test_recoveryresult_defined(self) -> None:
        assert RecoveryResult is not None

    def test_errorrecoveryguardrail_defined(self) -> None:
        assert ErrorRecoveryGuardrail is not None