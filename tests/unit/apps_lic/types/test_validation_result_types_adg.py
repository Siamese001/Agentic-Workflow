"""ADG contract tests for apps_lic/types/validation_result_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.types.validation_result_types  # noqa: F401


def test_module_importable():
    """Module validation_result_types must be importable."""
    assert apps_lic.types.validation_result_types is not None
