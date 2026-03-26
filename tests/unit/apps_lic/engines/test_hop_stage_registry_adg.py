"""ADG importability contract for apps_lic/engines/hop_stage_registry.py."""
from __future__ import annotations



def test_module_importable():
    """Module hop_stage_registry must be importable."""
    import apps_lic.engines.hop_stage_registry  # noqa: F401

    assert apps_lic.engines.hop_stage_registry is not None