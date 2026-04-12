"""Foundational behavioral tests for system_learning/types/index_build_metadata_types.py."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module index_build_metadata_types must be importable."""
    import system_learning.types.index_build_metadata_types

    assert system_learning.types.index_build_metadata_types is not None
