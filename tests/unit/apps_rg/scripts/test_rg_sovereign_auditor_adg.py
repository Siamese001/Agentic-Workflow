"""ADG-driven tests for apps_rg/scripts/rg_sovereign_auditor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module rg_sovereign_auditor must be importable."""
    import apps_rg.scripts.rg_sovereign_auditor  # noqa: F401

    assert apps_rg.scripts.rg_sovereign_auditor is not None