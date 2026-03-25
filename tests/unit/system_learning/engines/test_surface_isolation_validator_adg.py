"""ADG importability contract for system_learning/engines/surface_isolation_validator.py."""
from __future__ import annotations

import system_learning.engines.surface_isolation_validator  # noqa: F401


def test_module_importable():
    """Module surface_isolation_validator must be importable."""
    assert system_learning.engines.surface_isolation_validator is not None
