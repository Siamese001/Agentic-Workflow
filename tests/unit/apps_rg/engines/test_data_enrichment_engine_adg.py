"""ADG-driven tests for apps_rg/engines/data_enrichment_engine.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module data_enrichment_engine must be importable."""
    import apps_rg.engines.data_enrichment_engine  # noqa: F401

    assert apps_rg.engines.data_enrichment_engine is not None
