"""ADG importability contract for apps_shared/config/app_guardian_registry.py."""
from __future__ import annotations



def test_module_importable():
    """Module app_guardian_registry must be importable."""
    import apps_shared.config.app_guardian_registry  # noqa: F401

    assert apps_shared.config.app_guardian_registry is not None
