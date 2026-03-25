"""ADG importability contract for system_learning/engines/l4_version_store.py."""
from __future__ import annotations

import system_learning.engines.l4_version_store  # noqa: F401


def test_module_importable():
    """Module l4_version_store must be importable."""
    assert system_learning.engines.l4_version_store is not None
