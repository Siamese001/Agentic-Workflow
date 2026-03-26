"""ADG importability contract for system_learning/engines/retrieval_profile_activation_gate.py."""
from __future__ import annotations



def test_module_importable():
    """Module retrieval_profile_activation_gate must be importable."""
    import system_learning.engines.retrieval_profile_activation_gate  # noqa: F401

    assert system_learning.engines.retrieval_profile_activation_gate is not None