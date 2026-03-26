"""ADG contract tests for apps_shared/types/schema_search_mode_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module schema_search_mode_types must be importable."""
    import apps_shared.types.schema_search_mode_types  # noqa: F401

    assert apps_shared.types.schema_search_mode_types is not None