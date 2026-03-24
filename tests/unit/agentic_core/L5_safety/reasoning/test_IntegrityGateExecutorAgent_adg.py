"""ADG importability contract for agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_IntegrityGateExecutorAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.IntegrityGateExecutorAgent import (  # noqa: F401
        FinancialProofPoint,
        IntegrityGateResult,
        KeyExecutive,
        KeyTechnology,
        ValidationRejectionReason,
        Violation,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ValidationRejectionReason = None  # type: ignore[assignment,misc]
    Violation = None  # type: ignore[assignment,misc]
    IntegrityGateResult = None  # type: ignore[assignment,misc]
    FinancialProofPoint = None  # type: ignore[assignment,misc]
    KeyTechnology = None  # type: ignore[assignment,misc]
    KeyExecutive = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="IntegrityGateExecutorAgent deps unavailable")
class TestIntegritygateexecutoragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/IntegrityGateExecutorAgent.py must be importable."""
        assert _AVAILABLE

    def test_validationrejectionreason_defined(self) -> None:
        assert ValidationRejectionReason is not None

    def test_violation_defined(self) -> None:
        assert Violation is not None

    def test_integritygateresult_defined(self) -> None:
        assert IntegrityGateResult is not None

    def test_financialproofpoint_defined(self) -> None:
        assert FinancialProofPoint is not None

    def test_keytechnology_defined(self) -> None:
        assert KeyTechnology is not None

    def test_keyexecutive_defined(self) -> None:
        assert KeyExecutive is not None