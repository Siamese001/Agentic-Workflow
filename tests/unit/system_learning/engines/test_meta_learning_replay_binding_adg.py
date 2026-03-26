"""ADG importability contract for system_learning/engines/meta_learning_replay_binding.py."""
from __future__ import annotations



def test_module_importable():
    """Module meta_learning_replay_binding must be importable."""
    import system_learning.engines.meta_learning_replay_binding  # noqa: F401

    assert system_learning.engines.meta_learning_replay_binding is not None