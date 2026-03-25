"""ADG importability contract for apps_shared/spine/base_spine_adapter.py."""
from __future__ import annotations

import apps_shared.spine.base_spine_adapter  # noqa: F401


def test_module_importable():
    """Module base_spine_adapter must be importable."""
    assert apps_shared.spine.base_spine_adapter is not None
