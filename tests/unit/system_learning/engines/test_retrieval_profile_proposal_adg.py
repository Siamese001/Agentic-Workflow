"""ADG importability contract for system_learning/engines/retrieval_profile_proposal.py."""
from __future__ import annotations

import system_learning.engines.retrieval_profile_proposal  # noqa: F401


def test_module_importable():
    """Module retrieval_profile_proposal must be importable."""
    assert system_learning.engines.retrieval_profile_proposal is not None
