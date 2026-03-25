"""ADG-driven tests for apps_lic/scripts/purge_legacy_archive.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.scripts.purge_legacy_archive  # noqa: F401


def test_module_importable():
    """Module purge_legacy_archive must be importable."""
    assert apps_lic.scripts.purge_legacy_archive is not None
