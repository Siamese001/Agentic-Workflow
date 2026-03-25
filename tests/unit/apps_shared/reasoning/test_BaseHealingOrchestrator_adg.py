"""ADG importability contract for apps_shared/reasoning/BaseHealingOrchestrator.py."""
from __future__ import annotations

import apps_shared.reasoning.BaseHealingOrchestrator  # noqa: F401


def test_module_importable():
    """Module BaseHealingOrchestrator must be importable."""
    assert apps_shared.reasoning.BaseHealingOrchestrator is not None
