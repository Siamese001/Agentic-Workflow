"""ADG contract tests for apps_lic/types/recipient_archetype_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module recipient_archetype_types must be importable."""
    import apps_lic.types.recipient_archetype_types  # noqa: F401

    assert apps_lic.types.recipient_archetype_types is not None