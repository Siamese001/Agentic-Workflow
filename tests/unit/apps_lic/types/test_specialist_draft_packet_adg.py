"""ADG contract tests for apps_lic/types/SpecialistDraftPacket.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module SpecialistDraftPacket must be importable."""
    import apps_lic.types.SpecialistDraftPacket  # noqa: F401

    assert apps_lic.types.SpecialistDraftPacket is not None
