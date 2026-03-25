"""ADG importability contract for system_learning/engines/meta_learning_state_digest.py."""
from __future__ import annotations

import system_learning.engines.meta_learning_state_digest  # noqa: F401


def test_module_importable():
    """Module meta_learning_state_digest must be importable."""
    assert system_learning.engines.meta_learning_state_digest is not None
