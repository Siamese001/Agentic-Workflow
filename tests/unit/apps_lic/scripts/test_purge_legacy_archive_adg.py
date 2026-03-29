"""ADG-driven tests for apps_lic/scripts/purge_legacy_archive.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module purge_legacy_archive must be importable."""
    import apps_lic.scripts.purge_legacy_archive  # noqa: F401

    assert apps_lic.scripts.purge_legacy_archive is not None
