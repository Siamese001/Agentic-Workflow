"""ADG contract tests for apps_lic/types/ImmutableStagingBuffer.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.types.ImmutableStagingBuffer  # noqa: F401


def test_module_importable():
    """Module ImmutableStagingBuffer must be importable."""
    assert apps_lic.types.ImmutableStagingBuffer is not None
