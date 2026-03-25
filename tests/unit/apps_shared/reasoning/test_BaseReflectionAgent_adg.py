"""ADG importability contract for apps_shared/reasoning/BaseReflectionAgent.py."""
from __future__ import annotations

import apps_shared.reasoning.BaseReflectionAgent  # noqa: F401


def test_module_importable():
    """Module BaseReflectionAgent must be importable."""
    assert apps_shared.reasoning.BaseReflectionAgent is not None
