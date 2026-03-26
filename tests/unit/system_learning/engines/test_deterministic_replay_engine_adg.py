"""ADG importability contract for system_learning/engines/deterministic_replay_engine.py."""
from __future__ import annotations

def test_module_importable():
    """Module deterministic_replay_engine must be importable."""
    import system_learning.engines.deterministic_replay_engine
    assert system_learning.engines.deterministic_replay_engine is not None