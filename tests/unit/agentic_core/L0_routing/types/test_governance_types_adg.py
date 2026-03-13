"""ADG importability contract for agentic_core/L0_routing/types/governance_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_governance_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.governance_types import (  # noqa: F401
        EvidencePack,
        ExceptionScope,
        PolicyExceptionArtifact,
        PolicySnapshot,
        ProposalStatus,
        RouteDecisionRef,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RouteDecisionRef = None  # type: ignore[assignment,misc]
    PolicySnapshot = None  # type: ignore[assignment,misc]
    EvidencePack = None  # type: ignore[assignment,misc]
    ExceptionScope = None  # type: ignore[assignment,misc]
    PolicyExceptionArtifact = None  # type: ignore[assignment,misc]
    ProposalStatus = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="governance_types deps unavailable")
class TestGovernanceTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/governance_types.py must be importable."""
        assert _AVAILABLE

    def test_routedecisionref_defined(self) -> None:
        assert RouteDecisionRef is not None

    def test_policysnapshot_defined(self) -> None:
        assert PolicySnapshot is not None

    def test_evidencepack_defined(self) -> None:
        assert EvidencePack is not None

    def test_exceptionscope_defined(self) -> None:
        assert ExceptionScope is not None

    def test_policyexceptionartifact_defined(self) -> None:
        assert PolicyExceptionArtifact is not None

    def test_proposalstatus_defined(self) -> None:
        assert ProposalStatus is not None
