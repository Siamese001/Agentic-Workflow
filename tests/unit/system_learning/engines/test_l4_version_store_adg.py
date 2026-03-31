"""ADG importability contract for system_learning/engines/l4_version_store.py."""
from __future__ import annotations

def test_module_importable():
    """Module l4_version_store must be importable."""
    import system_learning.engines.l4_version_store
    assert system_learning.engines.l4_version_store is not None
