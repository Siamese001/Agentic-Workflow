"""ADG importability contract for apps_rg/validators/__init__.py."""
from __future__ import annotations


def test_module_importable():
    """Module validators must be importable."""
    import apps_rg.validators.__init__ as _mod  # noqa: F401

    assert _mod is not None
