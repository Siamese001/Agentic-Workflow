"""ADG contract tests for apps_shared/types/model_router_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module model_router_types must be importable."""
    import apps_shared.types.model_router_types  # noqa: F401

    assert apps_shared.types.model_router_types is not None