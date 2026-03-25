"""ADG importability contract for apps_shared/enforcement/GlobalcacheStrategy.py."""
from __future__ import annotations

import apps_shared.enforcement.GlobalcacheStrategy  # noqa: F401


def test_module_importable():
    """Module GlobalcacheStrategy must be importable."""
    assert apps_shared.enforcement.GlobalcacheStrategy is not None
