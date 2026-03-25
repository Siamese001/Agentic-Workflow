"""ADG importability contract for system_learning/engines/shadow_drift_analyzer.py."""
from __future__ import annotations

import system_learning.engines.shadow_drift_analyzer  # noqa: F401


def test_module_importable():
    """Module shadow_drift_analyzer must be importable."""
    assert system_learning.engines.shadow_drift_analyzer is not None
