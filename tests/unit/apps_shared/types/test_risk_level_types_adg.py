"""ADG contract tests for apps_shared/types/risk_level_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module risk_level_types must be importable."""
    import apps_shared.types.risk_level_types  # noqa: F401

    assert apps_shared.types.risk_level_types is not None