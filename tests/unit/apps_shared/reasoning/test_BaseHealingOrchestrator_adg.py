"""ADG importability contract for apps_shared/reasoning/BaseHealingOrchestrator.py."""
from __future__ import annotations


def test_module_importable():
    """Module BaseHealingOrchestrator must be importable."""
    import apps_shared.reasoning.BaseHealingOrchestrator  # noqa: F401

    assert apps_shared.reasoning.BaseHealingOrchestrator is not None