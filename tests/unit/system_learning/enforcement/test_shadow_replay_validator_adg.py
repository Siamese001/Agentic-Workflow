"""ADG importability contract for system_learning/enforcement/shadow_replay_validator.py."""
from __future__ import annotations

import system_learning.enforcement.shadow_replay_validator  # noqa: F401


def test_module_importable():
    """Module shadow_replay_validator must be importable."""
    assert system_learning.enforcement.shadow_replay_validator is not None
