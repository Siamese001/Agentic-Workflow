"""ADG importability contract for system_learning/engines/retrieval_profile_activation_gate.py."""
from __future__ import annotations

import system_learning.engines.retrieval_profile_activation_gate  # noqa: F401


def test_module_importable():
    """Module retrieval_profile_activation_gate must be importable."""
    assert system_learning.engines.retrieval_profile_activation_gate is not None
