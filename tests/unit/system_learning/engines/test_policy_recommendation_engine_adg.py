"""ADG importability contract for system_learning/engines/policy_recommendation_engine.py."""
from __future__ import annotations

import system_learning.engines.policy_recommendation_engine  # noqa: F401


def test_module_importable():
    """Module policy_recommendation_engine must be importable."""
    assert system_learning.engines.policy_recommendation_engine is not None
