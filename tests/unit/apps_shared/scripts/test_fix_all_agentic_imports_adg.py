"""ADG-driven tests for apps_shared/scripts/fix_all_agentic_imports.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module fix_all_agentic_imports must be importable."""
    import apps_shared.scripts.fix_all_agentic_imports  # noqa: F401

    assert apps_shared.scripts.fix_all_agentic_imports is not None
