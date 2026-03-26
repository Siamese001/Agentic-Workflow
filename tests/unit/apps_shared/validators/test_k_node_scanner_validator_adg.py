"""ADG-driven tests for apps_shared/validators/k_node_scanner_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module k_node_scanner_validator must be importable."""
    import apps_shared.validators.k_node_scanner_validator  # noqa: F401

    assert apps_shared.validators.k_node_scanner_validator is not None