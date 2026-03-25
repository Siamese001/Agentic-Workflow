"""ADG importability contract for system_learning/engines/retrieval_profile_proposal_manager.py."""
from __future__ import annotations

import system_learning.engines.retrieval_profile_proposal_manager  # noqa: F401


def test_module_importable():
    """Module retrieval_profile_proposal_manager must be importable."""
    assert system_learning.engines.retrieval_profile_proposal_manager is not None
