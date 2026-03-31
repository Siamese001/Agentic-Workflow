"""ADG contract tests for apps_shared/types/invocation_type_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module invocation_type_types must be importable."""
    import apps_shared.types.invocation_type_types  # noqa: F401

    assert apps_shared.types.invocation_type_types is not None
