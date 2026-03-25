"""ADG importability contract for apps_lic/engines/hop_stage_registry.py."""
from __future__ import annotations

import apps_lic.engines.hop_stage_registry  # noqa: F401


def test_module_importable():
    """Module hop_stage_registry must be importable."""
    assert apps_lic.engines.hop_stage_registry is not None
