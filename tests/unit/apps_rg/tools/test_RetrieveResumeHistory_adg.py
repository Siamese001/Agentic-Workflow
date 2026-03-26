"""ADG-driven tests for apps_rg/tools/RetrieveResumeHistory.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module RetrieveResumeHistory must be importable."""
    import apps_rg.tools.RetrieveResumeHistory  # noqa: F401

    assert apps_rg.tools.RetrieveResumeHistory is not None