"""ADG importability contract for apps_shared/spine/d0_engine_adapter.py."""
from __future__ import annotations

import apps_shared.spine.d0_engine_adapter  # noqa: F401


def test_module_importable():
    """Module d0_engine_adapter must be importable."""
    assert apps_shared.spine.d0_engine_adapter is not None
