"""ADG-driven tests for apps_shared/config/refine_config_ranking_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module refine_config_ranking_config must be importable."""
    import apps_shared.config.refine_config_ranking_config  # noqa: F401

    assert apps_shared.config.refine_config_ranking_config is not None