"""ADG importability contract for apps_lic/utils/__init__.py."""
from __future__ import annotations

import apps_lic.utils.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module utils must be importable."""
    assert _mod is not None
