"""ADG-driven tests for apps_shared/scripts/update_validator_imports.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module update_validator_imports must be importable."""
    import apps_shared.scripts.update_validator_imports  # noqa: F401

    assert apps_shared.scripts.update_validator_imports is not None
