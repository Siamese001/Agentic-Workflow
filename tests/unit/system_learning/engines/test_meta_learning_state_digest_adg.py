"""ADG importability contract for system_learning/engines/meta_learning_state_digest.py."""
from __future__ import annotations



def test_module_importable():
    """Module meta_learning_state_digest must be importable."""
    import system_learning.engines.meta_learning_state_digest  # noqa: F401

    assert system_learning.engines.meta_learning_state_digest is not None