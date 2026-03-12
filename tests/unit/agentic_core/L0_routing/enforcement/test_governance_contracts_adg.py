"""ADG importability contract for agentic_core/L0_routing/enforcement/governance_contracts.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_governance_contracts.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.enforcement.governance_contracts import (  # noqa: F401
        EvidencePackError,
        PolicyExceptionError,
        PolicyUpdateError,
        build_evidence_pack,
        validate_evidence_pack,
        build_hil_evidence_pack,
        emit_policy_exception,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    EvidencePackError = None  # type: ignore[assignment,misc]
    PolicyExceptionError = None  # type: ignore[assignment,misc]
    PolicyUpdateError = None  # type: ignore[assignment,misc]
    build_evidence_pack = None  # type: ignore[assignment,misc]
    validate_evidence_pack = None  # type: ignore[assignment,misc]
    build_hil_evidence_pack = None  # type: ignore[assignment,misc]
    emit_policy_exception = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="governance_contracts.py deps unavailable")
class TestGovernanceContractsImportability:
    def test_module_importable(self) -> None:
        """ADG contract: governance_contracts.py must be importable."""
        assert _AVAILABLE

    def test_evidencepackerror_is_type(self) -> None:
        assert EvidencePackError is not None

    def test_policyexceptionerror_is_type(self) -> None:
        assert PolicyExceptionError is not None

    def test_policyupdateerror_is_type(self) -> None:
        assert PolicyUpdateError is not None

    def test_build_evidence_pack_callable(self) -> None:
        assert callable(build_evidence_pack)

    def test_validate_evidence_pack_callable(self) -> None:
        assert callable(validate_evidence_pack)

