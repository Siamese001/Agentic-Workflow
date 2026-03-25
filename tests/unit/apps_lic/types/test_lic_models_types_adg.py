"""ADG contract tests for apps_lic/types/lic_models_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.types.lic_models_types  # noqa: F401


def test_module_importable():
    """Module lic_models_types must be importable."""
    assert apps_lic.types.lic_models_types is not None
