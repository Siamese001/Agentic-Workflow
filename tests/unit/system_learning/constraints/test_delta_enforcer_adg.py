"""ADG importability contract for system_learning/constraints/delta_enforcer.py."""
from __future__ import annotations

import system_learning.constraints.delta_enforcer  # noqa: F401


def test_module_importable():
    """Module delta_enforcer must be importable."""
    assert system_learning.constraints.delta_enforcer is not None
