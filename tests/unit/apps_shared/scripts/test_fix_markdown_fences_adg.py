"""ADG-driven tests for apps_shared/scripts/fix_markdown_fences.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module fix_markdown_fences must be importable."""
    import apps_shared.scripts.fix_markdown_fences  # noqa: F401

    assert apps_shared.scripts.fix_markdown_fences is not None