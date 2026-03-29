"""ADG contract tests for apps_shared/types/unified_formatter_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module unified_formatter_types must be importable."""
    import apps_shared.types.unified_formatter_types  # noqa: F401

    assert apps_shared.types.unified_formatter_types is not None