"""ADG importability contract for apps_lic/engines/control_plane.py."""
from __future__ import annotations



def test_module_importable():
    """Module control_plane must be importable."""
    import apps_lic.engines.control_plane  # noqa: F401

    assert apps_lic.engines.control_plane is not None
