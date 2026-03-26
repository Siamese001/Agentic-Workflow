"""ADG importability contract for apps_shared/config/__init__.py."""
from __future__ import annotations



def test_module_importable():
    """Module config must be importable."""
    import apps_shared.config.__init__ as _mod  # noqa: F401

    assert _mod is not None