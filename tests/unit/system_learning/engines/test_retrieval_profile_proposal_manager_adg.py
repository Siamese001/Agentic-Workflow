"""ADG importability contract for system_learning/engines/retrieval_profile_proposal_manager.py."""
from __future__ import annotations

def test_module_importable():
    """Module retrieval_profile_proposal_manager must be importable."""
    import system_learning.engines.retrieval_profile_proposal_manager
    assert system_learning.engines.retrieval_profile_proposal_manager is not None
