"""ADG importability contract for apps_rg/types/__init__.py."""
from __future__ import annotations


def test_module_importable():
    """Module types must be importable."""
    import apps_rg.types.__init__ as _mod  # noqa: F401

    assert _mod is not None