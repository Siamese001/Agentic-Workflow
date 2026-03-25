"""ADG importability contract for apps_shared/data/__init__.py."""
from __future__ import annotations

import apps_shared.data.__init__  # noqa: F401


def test_module_importable():
    """Module data must be importable."""
    assert apps_shared.data.__init__ is not None
