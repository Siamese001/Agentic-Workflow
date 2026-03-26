"""ADG contract tests for apps_shared/types/health_status_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module health_status_types must be importable."""
    import apps_shared.types.health_status_types  # noqa: F401

    assert apps_shared.types.health_status_types is not None