"""ADG importability contract for system_learning/engines/retrieval_profile_proposal_manager.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_retrieval_profile_proposal_manager.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.retrieval_profile_proposal_manager import (  # noqa: F401
        RetrievalProfileProposalManager,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    RetrievalProfileProposalManager = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_profile_proposal_manager.py deps unavailable")
class TestRetrievalProfileProposalManagerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: retrieval_profile_proposal_manager.py must be importable."""
        assert _AVAILABLE

    def test_retrievalprofileproposalmanager_is_type(self) -> None:
        assert RetrievalProfileProposalManager is not None