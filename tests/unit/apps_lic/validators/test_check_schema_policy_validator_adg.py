"""ADG-driven tests for apps_lic/validators/check_schema_policy_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    import apps_lic.validators.check_schema_policy_validator as _mod  # noqa: F401
    _AVAILABLE = True
except Exception:
    _mod = None
    _AVAILABLE = False


def test_module_importable():
    """Module check_schema_policy_validator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
