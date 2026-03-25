"""ADG contract tests for apps_rg/types/resume_section_node_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_rg.types.resume_section_node_types  # noqa: F401


def test_module_importable():
    """Module resume_section_node_types must be importable."""
    assert apps_rg.types.resume_section_node_types is not None
