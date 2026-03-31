"""ADG importability contract for system_learning/engines/change_package_impl.py."""
from __future__ import annotations

def test_module_importable():
    """Module change_package_impl must be importable."""
    import system_learning.engines.change_package_impl
    assert system_learning.engines.change_package_impl is not None
