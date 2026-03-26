"""ADG contract tests for apps_lic/types/validation_severity_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module validation_severity_types must be importable."""
    import apps_lic.types.validation_severity_types  # noqa: F401

    assert apps_lic.types.validation_severity_types is not None
