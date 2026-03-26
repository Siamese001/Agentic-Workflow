"""ADG importability contract for apps_lic/reasoning/LicHealingOrchestrator.py."""
from __future__ import annotations



def test_module_importable():
    """Module LicHealingOrchestrator must be importable."""
    import apps_lic.reasoning.LicHealingOrchestrator  # noqa: F401

    assert apps_lic.reasoning.LicHealingOrchestrator is not None