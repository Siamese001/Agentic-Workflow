"""ADG contract tests for apps_lic/types/lic_models_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module lic_models_types must be importable."""
    import apps_lic.types.lic_models_types  # noqa: F401

    assert apps_lic.types.lic_models_types is not None