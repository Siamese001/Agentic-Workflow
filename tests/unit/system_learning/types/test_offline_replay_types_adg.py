"""ADG importability contract for system_learning/types/offline_replay_types.py."""
from __future__ import annotations

import system_learning.types.offline_replay_types  # noqa: F401


def test_module_importable():
    """Module offline_replay_types must be importable."""
    assert system_learning.types.offline_replay_types is not None
