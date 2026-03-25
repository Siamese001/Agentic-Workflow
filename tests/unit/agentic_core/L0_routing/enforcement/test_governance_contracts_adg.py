"""ADG importability contract for agentic_core/L0_routing/enforcement/governance_contracts.py.

Auto-generated stub - covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_governance_contracts.py (no _adg suffix).
"""
from __future__ import annotations

from agentic_core.L0_routing.enforcement.governance_contracts import (
    EvidencePackError,
    PolicyExceptionError,
)  # noqa: F401


class TestGovernanceContractsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/enforcement/governance_contracts.py must be importable."""

        pass  # Import verified at module level

    def test_evidencepackerror_defined(self) -> None:
        assert EvidencePackError is not None

    def test_policyexceptionerror_defined(self) -> None:
        assert PolicyExceptionError is not None
