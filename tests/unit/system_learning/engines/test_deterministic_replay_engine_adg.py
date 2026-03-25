"""ADG importability contract for system_learning/engines/deterministic_replay_engine.py."""
from __future__ import annotations

import system_learning.engines.deterministic_replay_engine  # noqa: F401


def test_module_importable():
    """Module deterministic_replay_engine must be importable."""
    assert system_learning.engines.deterministic_replay_engine is not None
