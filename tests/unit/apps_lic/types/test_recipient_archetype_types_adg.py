"""ADG contract tests for apps_lic/types/recipient_archetype_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.types.recipient_archetype_types  # noqa: F401


def test_module_importable():
    """Module recipient_archetype_types must be importable."""
    assert apps_lic.types.recipient_archetype_types is not None
