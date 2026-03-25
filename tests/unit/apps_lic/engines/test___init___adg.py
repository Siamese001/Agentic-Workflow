"""ADG importability contract for apps_lic/engines/__init__.py."""
from __future__ import annotations

import apps_lic.engines.__init__ as _mod  # noqa: F401


def test_module_importable():
    """Module engines must be importable."""
    assert _mod is not None
