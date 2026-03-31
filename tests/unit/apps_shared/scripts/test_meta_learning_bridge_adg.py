"""ADG importability contract for apps_shared/scripts/meta_learning_bridge.py."""
from __future__ import annotations


def test_module_importable():
    """Module meta_learning_bridge must be importable."""
    import apps_shared.scripts.meta_learning_bridge  # noqa: F401

    assert apps_shared.scripts.meta_learning_bridge is not None
