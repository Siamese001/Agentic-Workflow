"""ADG contract tests for apps_lic/types/competitor_recon_agent_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.types.competitor_recon_agent_types  # noqa: F401


def test_module_importable():
    """Module competitor_recon_agent_types must be importable."""
    assert apps_lic.types.competitor_recon_agent_types is not None
