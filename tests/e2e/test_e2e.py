""""""
from __future__ import annotations

import playwright.sync_api  # noqa: F401


def test_module_importable():
    """Module sync_api must be importable."""
    assert playwright.sync_api is not None
