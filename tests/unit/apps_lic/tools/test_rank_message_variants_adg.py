"""ADG-driven tests for apps_lic/tools/rank_message_variants.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.tools.rank_message_variants  # noqa: F401


def test_module_importable():
    """Module rank_message_variants must be importable."""
    assert apps_lic.tools.rank_message_variants is not None
