"""ADG contract tests for apps_shared/types/rate_limiter_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module rate_limiter_types must be importable."""
    import apps_shared.types.rate_limiter_types  # noqa: F401

    assert apps_shared.types.rate_limiter_types is not None
