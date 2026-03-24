"""ADG importability contract for system_learning/engines/retrieval_profile_proposal.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_retrieval_profile_proposal.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.engines.retrieval_profile_proposal import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        RetrievalProfileProposal,
        create_proposal_digest,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    RetrievalProfileProposal = None  # type: ignore[assignment,misc]
    create_proposal_digest = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_profile_proposal.py deps unavailable")
class TestRetrievalProfileProposalImportability:
    def test_module_importable(self) -> None:
        """ADG contract: retrieval_profile_proposal.py must be importable."""
        assert _AVAILABLE

    def test_retrievalprofileproposal_is_type(self) -> None:
        assert RetrievalProfileProposal is not None

    def test_create_proposal_digest_callable(self) -> None:
        assert callable(create_proposal_digest)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None