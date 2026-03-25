"""ADG importability contract for apps_shared/scripts/meta_learning_bridge.py."""
from __future__ import annotations

import apps_shared.scripts.meta_learning_bridge  # noqa: F401


def test_module_importable():
    """Module meta_learning_bridge must be importable."""
    assert apps_shared.scripts.meta_learning_bridge is not None
