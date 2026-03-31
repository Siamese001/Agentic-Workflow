"""ADG importability contract for system_learning/engines/retrieval_profile_proposal.py."""
from __future__ import annotations

def test_module_importable():
    """Module retrieval_profile_proposal must be importable."""
    import system_learning.engines.retrieval_profile_proposal
    assert system_learning.engines.retrieval_profile_proposal is not None
