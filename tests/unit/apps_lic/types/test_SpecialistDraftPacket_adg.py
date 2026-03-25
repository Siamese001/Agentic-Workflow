"""ADG contract tests for apps_lic/types/SpecialistDraftPacket.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_lic.types.SpecialistDraftPacket  # noqa: F401


def test_module_importable():
    """Module SpecialistDraftPacket must be importable."""
    assert apps_lic.types.SpecialistDraftPacket is not None
