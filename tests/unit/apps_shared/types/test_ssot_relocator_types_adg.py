"""ADG contract tests for apps_shared/types/ssot_relocator_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.ssot_relocator_types  # noqa: F401


def test_module_importable():
    """Module ssot_relocator_types must be importable."""
    assert apps_shared.types.ssot_relocator_types is not None
