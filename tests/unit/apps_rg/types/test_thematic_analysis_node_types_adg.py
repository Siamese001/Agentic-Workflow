"""ADG contract tests for apps_rg/types/thematic_analysis_node_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module thematic_analysis_node_types must be importable."""
    import apps_rg.types.thematic_analysis_node_types  # noqa: F401

    assert apps_rg.types.thematic_analysis_node_types is not None