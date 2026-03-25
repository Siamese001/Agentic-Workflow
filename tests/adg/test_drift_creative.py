""""""
from __future__ import annotations

import hypothesis  # noqa: F401


def test_module_importable():
    """Module hypothesis must be importable."""
    assert hypothesis is not None
