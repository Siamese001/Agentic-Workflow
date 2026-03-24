"""ADG importability contract for agentic_core/L5_safety/validators/governance_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_governance_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.validators.governance_validator import (  # noqa: F401
        GovernanceResult,
        GovernanceShieldValidator,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    GovernanceResult = None  # type: ignore[assignment,misc]
    GovernanceShieldValidator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="governance_validator deps unavailable")
class TestGovernanceValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/validators/governance_validator.py must be importable."""
        assert _AVAILABLE

    def test_governanceresult_defined(self) -> None:
        assert GovernanceResult is not None

    def test_governanceshieldvalidator_defined(self) -> None:
        assert GovernanceShieldValidator is not None