"""ADG contract tests for apps_lic/types/state_checkpoint_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.types.state_checkpoint_types  # noqa: F401


def test_module_importable():
    """Module state_checkpoint_types must be importable."""
    assert apps_lic.types.state_checkpoint_types is not None
