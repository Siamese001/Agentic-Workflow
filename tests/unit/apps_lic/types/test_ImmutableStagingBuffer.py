"""Foundational behavioral tests for apps_lic/types/ImmutableStagingBuffer.py."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module ImmutableStagingBuffer must be importable."""
    import apps_lic.types.ImmutableStagingBuffer  # noqa: F401

    assert apps_lic.types.ImmutableStagingBuffer is not None
