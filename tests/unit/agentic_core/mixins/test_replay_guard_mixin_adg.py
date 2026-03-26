"""ADG importability contract for agentic_core/mixins/replay_guard_mixin.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.mixins.replay_guard_mixin  # noqa: F401


def test_module_importable():
    import agentic_core.mixins.replay_guard_mixin  # noqa: F401
    """Module replay_guard_mixin must be importable."""
    assert agentic_core.mixins.replay_guard_mixin is not None
