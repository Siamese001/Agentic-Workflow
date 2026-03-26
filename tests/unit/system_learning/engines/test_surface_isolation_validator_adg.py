"""ADG importability contract for system_learning/engines/surface_isolation_validator.py."""
from __future__ import annotations

def test_module_importable():
    """Module surface_isolation_validator must be importable."""
    import system_learning.engines.surface_isolation_validator
    assert system_learning.engines.surface_isolation_validator is not None