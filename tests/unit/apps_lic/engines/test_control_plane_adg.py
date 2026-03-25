"""ADG importability contract for apps_lic/engines/control_plane.py."""
from __future__ import annotations

import apps_lic.engines.control_plane  # noqa: F401


def test_module_importable():
    """Module control_plane must be importable."""
    assert apps_lic.engines.control_plane is not None
