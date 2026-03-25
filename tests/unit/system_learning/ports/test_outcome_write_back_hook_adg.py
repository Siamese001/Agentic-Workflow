"""ADG importability contract for system_learning/ports/outcome_write_back_hook.py."""
from __future__ import annotations

import system_learning.ports.outcome_write_back_hook  # noqa: F401


def test_module_importable():
    """Module outcome_write_back_hook must be importable."""
    assert system_learning.ports.outcome_write_back_hook is not None
