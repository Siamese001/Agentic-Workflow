"""ADG importability contract for apps_shared/utils/__init__.py."""
from __future__ import annotations

import apps_shared.utils.__init__  # noqa: F401


def test_module_importable():
    """Module utils must be importable."""
    assert apps_shared.utils.__init__ is not None
