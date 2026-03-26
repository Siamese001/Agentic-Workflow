"""ADG importability contract for system_learning/types/offline_replay_types.py."""
from __future__ import annotations

def test_module_importable():
    """Module offline_replay_types must be importable."""
    import system_learning.types.offline_replay_types
    assert system_learning.types.offline_replay_types is not None