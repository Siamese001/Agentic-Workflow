"""ADG-driven tests for apps_shared/validators/cache_entry_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module cache_entry_validator must be importable."""
    import apps_shared.validators.cache_entry_validator  # noqa: F401

    assert apps_shared.validators.cache_entry_validator is not None